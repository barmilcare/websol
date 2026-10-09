import test from 'node:test';
import assert from 'node:assert/strict';
import { handleEnquiry } from '../server/enquiry.mjs';

const origin = 'https://websolutionsydney.com.au';
const env = { RESEND_API_KEY: 'test-secret-not-live', ENQUIRY_FROM: 'Website <forms@example.com>', ENQUIRY_TO: 'owner@example.com' };
const fields = { name: 'Test User', email: 'visitor@example.com', message: 'Please discuss a business website.', requestId: 'ea616011-a221-4098-9b8f-6ff5ebefcc6c', company_url: '' };
function request(data = fields, overrides = {}) {
  return new Request(origin + '/api/enquiry', { method: 'POST', headers: { origin, 'content-type': 'application/json' }, body: JSON.stringify(data), ...overrides });
}
function network(email = { id: 'test-accepted-id' }, emailStatus = 200) {
  const calls = [];
  return { calls, fetcher: async (url, options) => {
    calls.push({ url, ...options });
    return new Response(JSON.stringify(email), { status: emailStatus, headers: { 'content-type': 'application/json' } });
  }};
}

test('unconfigured form disables direct delivery and makes no external calls', async () => {
  const n = network();
  assert.deepEqual(await (await handleEnquiry(new Request(origin + '/api/enquiry'), {})).json(), { enabled: false });
  assert.equal((await handleEnquiry(request(), {}, n.fetcher)).status, 503);
  assert.equal(n.calls.length, 0);
});
test('configuration reports enabled when all 3 env vars are set', async () => {
  const response = await handleEnquiry(new Request(origin + '/api/enquiry'), env);
  assert.deepEqual(await response.json(), { enabled: true });
  assert.equal(response.headers.get('cache-control'), 'no-store');
});
test('missing any one env var disables the form', async () => {
  for (const key of ['RESEND_API_KEY', 'ENQUIRY_FROM', 'ENQUIRY_TO']) {
    const partial = { ...env, [key]: undefined };
    assert.deepEqual(await (await handleEnquiry(new Request(origin + '/api/enquiry'), partial)).json(), { enabled: false });
  }
});
test('invalid fields, header injection, honeypot and bad requestId are rejected', async () => {
  for (const patch of [{ email: 'invalid' }, { name: 'Acme\r\nBcc: attacker@example.com' }, { company_url: 'spam' }, { message: 'short' }, { requestId: 'invalid' }]) {
    const n = network();
    assert.equal((await handleEnquiry(request({ ...fields, ...patch }), env, n.fetcher)).status, 400);
    assert.equal(n.calls.length, 0);
  }
});
test('limits streamed request bytes even without a content-length header', async () => {
  const n = network();
  const response = await handleEnquiry(request({ ...fields, message: 'x'.repeat(21000) }), env, n.fetcher);
  assert.equal(response.status, 413);
  assert.equal(n.calls.length, 0);
});
test('malformed JSON and unsupported content type do not send emails', async () => {
  const n = network();
  assert.equal((await handleEnquiry(request(fields, { body: '{bad' }), env, n.fetcher)).status, 400);
  assert.equal((await handleEnquiry(request(fields, { headers: { origin, 'content-type': 'text/plain' } }), env, n.fetcher)).status, 415);
  assert.equal(n.calls.length, 0);
});
test('email rejection and success response without provider ID never report acceptance', async () => {
  for (const [body, code] of [[{ message: 'blocked' }, 403], [{}, 200]]) {
    const n = network(body, code);
    const response = await handleEnquiry(request(), env, n.fetcher);
    assert.equal(response.status, 502);
    assert.notEqual((await response.json()).status, 'accepted');
  }
});
test('valid request uses fixed recipient, visitor reply-to, plain text and idempotency', async () => {
  const n = network();
  const response = await handleEnquiry(request({ ...fields, to: 'attacker@example.com' }), env, n.fetcher);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: 'accepted' });
  const email = JSON.parse(n.calls[0].body);
  assert.deepEqual(email.to, ['owner@example.com']);
  assert.equal(email.reply_to, fields.email);
  assert.equal(email.from, env.ENQUIRY_FROM);
  assert.equal(email.html, undefined);
  assert.ok(email.text.includes(fields.message));
  assert.equal(n.calls[0].headers['Idempotency-Key'], 'wss-enquiry/' + fields.requestId);
});
test('network outage during email send returns 502', async () => {
  const response = await handleEnquiry(request(), env, async () => { throw new Error('offline'); });
  assert.equal(response.status, 502);
});
