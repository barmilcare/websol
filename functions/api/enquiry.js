import { handleEnquiry } from '../../server/enquiry.mjs';

export function onRequest({ request, env }) {
  return handleEnquiry(request, env);
}
