const services = new Set(['New website', 'Website redesign', 'Hosting & care', 'SEO', 'AI marketing', 'Not sure yet']);
const maxBytes = 20000;

function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });
}

function allowedHostname(hostname) {
  return hostname === 'websolutionsydney.com.au' ||
    hostname.endsWith('.websolutionsydney.com.au') ||
    hostname === 'websolseo.pages.dev' ||
    hostname.endsWith('.websolseo.pages.dev');
}

function value(...values) {
  return values.find(item => typeof item === 'string' && item.trim())?.trim() || '';
}

function configuration(env, request) {
  const config = {
    resendKey: value(env.RESEND_API_KEY),
    from: value(env.ENQUIRY_FROM, env.SEO_FROM_EMAIL, env.CONTACT_FROM_EMAIL, env.CONTACT_FORM_FROM_EMAIL, env.RESEND_FROM_EMAIL),
    to: value(env.ENQUIRY_TO, env.SEO_ENQUIRY_TO_EMAIL, env.CONTACT_TO_EMAIL, env.CONTACT_EMAIL, env.RESEND_TO_EMAIL),
    turnstileSecret: value(env.TURNSTILE_SECRET_KEY),
    turnstileSite: value(env.TURNSTILE_SITE_KEY, env.PUBLIC_TURNSTILE_SITE_KEY, env.VITE_TURNSTILE_SITE_KEY)
  };
  if (Object.values(config).some(item => !item)) return null;
  try {
    const site = new URL(request.url);
    return site.protocol === 'https:' && allowedHostname(site.hostname) ? config : null;
  } catch { return null; }
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

function validate(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return null;
  const data = {};
  for (const [key, minimum, maximum] of [['name',1,100],['business',1,150],['email',3,254],['service',1,50],['website',0,500],['message',10,4000],['token',1,2048],['requestId',36,36]]) {
    if (typeof input[key] !== 'string') return null;
    data[key] = input[key].trim();
    if (data[key].length < minimum || data[key].length > maximum) return null;
  }
  if (input.company_url) return null;
  if (!services.has(data.service) || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) return null;
  if (/[\r\n\u0000]/.test(data.name + data.business + data.email + data.service)) return null;
  if (!/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(data.requestId)) return null;
  if (data.website) {
    try { if (!['http:', 'https:'].includes(new URL(data.website).protocol)) return null; }
    catch { return null; }
  }
  return data;
}

async function handleEnquiry(request, env, fetcher = fetch) {
  if (!['GET', 'POST'].includes(request.method)) return json({ message: 'Method not allowed.' }, 405);
  const config = configuration(env, request);
  if (request.method === 'GET') return json(config ? { enabled: true, siteKey: config.turnstileSite } : { enabled: false });
  if (!config) return json({ message: 'Direct sending is unavailable. Please email ryan@websolutionsydney.com.au.' }, 503);
  const origin = new URL(request.url).origin;
  if (request.headers.get('origin') !== origin) return json({ message: 'Please send the enquiry from our website.' }, 403);
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get('content-type') || '')) return json({ message: 'Unsupported request format.' }, 415);
  let input;
  try { input = await boundedBody(request); }
  catch (error) { return json({ message: 'Please check the form and shorten your message if needed.' }, error.message === 'too_large' ? 413 : 400); }
  const data = validate(input);
  if (!data) return json({ message: 'Please check the form fields and complete the security check again.' }, 400);
  let verification;
  try {
    const response = await fetcher('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret: config.turnstileSecret, response: data.token, remoteip: request.headers.get('CF-Connecting-IP') || undefined }),
      signal: AbortSignal.timeout(10000)
    });
    if (!response.ok) throw new Error('security_unavailable');
    verification = await response.json();
  } catch { return json({ message: 'The security check is unavailable. Please try again or email us.' }, 502); }
  if (verification.success !== true || verification.hostname !== new URL(origin).hostname || verification.action !== 'enquiry') {
    return json({ message: 'Please complete the security check again.' }, 400);
  }
  const text = `Name: ${data.name}\nBusiness: ${data.business}\nReply email: ${data.email}\nService: ${data.service}\nWebsite: ${data.website || 'Not provided'}\n\n${data.message}`;
  try {
    const response = await fetcher('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${config.resendKey}`, 'Content-Type': 'application/json', 'Idempotency-Key': `wss-enquiry/${data.requestId}` },
      body: JSON.stringify({ from: config.from, to: [config.to], reply_to: data.email, subject: `${data.service} enquiry — ${data.business}`, text }),
      signal: AbortSignal.timeout(10000)
    });
    const result = await response.json();
    if (!response.ok || typeof result.id !== 'string' || !result.id) throw new Error('not_accepted');
    return json({ status: 'accepted' });
  } catch {
    return json({ message: 'We could not confirm email delivery. Please email or call us before trying again.' }, 502);
  }
}


export default {
  async fetch(request, env) {
    const pathname = new URL(request.url).pathname;
    if (pathname === '/api/enquiry' || pathname === '/api/enquiry/') {
      return handleEnquiry(request, env);
    }
    return env.ASSETS.fetch(request);
  }
};
