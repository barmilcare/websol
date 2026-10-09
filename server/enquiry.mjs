const maxBytes = 20000;

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      ...corsHeaders(),
    },
  });
}

async function boundedBody(request) {
  if (Number(request.headers.get('content-length')) > maxBytes) throw new Error('too_large');
  if (!request.body) throw new Error('invalid_body');
  const reader = request.body.getReader();
  const chunks = [];
  let total = 0;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > maxBytes) { await reader.cancel(); throw new Error('too_large'); }
    chunks.push(value);
  }
  const joined = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { joined.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder().decode(joined));
}

function configuration(env) {
  const resendKey = (env.RESEND_API_KEY || '').trim();
  const from = (env.ENQUIRY_FROM || '').trim();
  const to = (env.ENQUIRY_TO || '').trim();
  if (!resendKey || !from || !to) return null;
  return { resendKey, from, to };
}

function validate(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return null;
  if (input.company_url) return null;
  const data = {};
  for (const [key, minimum, maximum] of [['name', 1, 100], ['email', 3, 254], ['message', 10, 4000], ['requestId', 36, 36]]) {
    if (typeof input[key] !== 'string') return null;
    data[key] = input[key].trim();
    if (data[key].length < minimum || data[key].length > maximum) return null;
  }
  if (typeof input.service === 'string' && input.service.length <= 100) data.service = input.service.trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) return null;
  if (/[\r\n\u0000]/.test(data.name + data.email)) return null;
  if (!/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(data.requestId)) return null;
  return data;
}

export async function handleEnquiry(request, env, fetcher = fetch) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 200, headers: corsHeaders() });
  if (!['GET', 'POST'].includes(request.method)) return json({ message: 'Method not allowed.' }, 405);
  const config = configuration(env);
  if (request.method === 'GET') return json({ enabled: Boolean(config) });
  if (!config) return json({ message: 'Direct sending is unavailable. Please email ryan@websolutionsydney.com.au.' }, 503);
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get('content-type') || '')) return json({ message: 'Unsupported request format.' }, 415);
  let input;
  try { input = await boundedBody(request); }
  catch (error) { return json({ message: 'Please check the form and shorten your message if needed.' }, error.message === 'too_large' ? 413 : 400); }
  const data = validate(input);
  if (!data) return json({ message: 'Please check the form fields and try again.' }, 400);
  const text = `Name: ${data.name}\nReply email: ${data.email}${data.service ? `\nInterested in: ${data.service}` : ''}\n\n${data.message}`;
  try {
    const response = await fetcher('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${config.resendKey}`, 'Content-Type': 'application/json', 'Idempotency-Key': `wss-enquiry/${data.requestId}` },
      body: JSON.stringify({ from: config.from, to: [config.to], reply_to: data.email, subject: `Website enquiry — ${data.name}`, text }),
      signal: AbortSignal.timeout(10000)
    });
    const result = await response.json();
    if (!response.ok || typeof result.id !== 'string' || !result.id) throw new Error('not_accepted');
    return json({ status: 'accepted' });
  } catch {
    return json({ message: 'We could not confirm email delivery. Please email or call us before trying again.' }, 502);
  }
}
