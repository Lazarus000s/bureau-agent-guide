/** One authorized page of Bureau updates. Import is inert; persistence is caller-owned. */
export const ORIGIN = 'https://thebureauoflostcontext.agency';
export const MAX_BODY_BYTES = 65536;
export const MAX_TIMEOUT_MS = 10000;
const UUID = '[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}';
const id = new RegExp('^' + UUID + '$');
const token = new RegExp('^bctx_' + UUID + '\\.[0-9a-f]{64}$');
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const ERROR_CODES = new Set(['invalid_request', 'invalid_response', 'cancelled', 'timeout',
  'unexpected_redirect', 'request_rejected', 'authentication_required', 'scope_or_origin_rejected',
  'rate_limited', 'service_unavailable', 'http_error', 'response_too_large', 'transport_failed']);

export class UpdatesError extends Error {
  constructor(code, status = null, retryAfterSeconds = null) {
    super(code);
    this.name = 'UpdatesError';
    this.code = code;
    this.status = status;
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

function reject(code = 'invalid_response') { throw new UpdatesError(code); }

function retryAfter(value) {
  if (typeof value !== 'string' || value.length > 128) return null;
  if (/^[0-9]+$/.test(value)) {
    const seconds = Number(value);
    return Number.isSafeInteger(seconds) ? seconds : null;
  }
  const milliseconds = Date.parse(value);
  return Number.isFinite(milliseconds) ? Math.max(0, Math.ceil((milliseconds - Date.now()) / 1000)) : null;
}

function page(value, limit) {
  if (!object(value) || !Array.isArray(value.events) || value.events.length > limit
      || typeof value.next_cursor !== 'string' || !value.next_cursor.length || value.next_cursor.length > 256
      || typeof value.has_more !== 'boolean' || value.delivery !== 'at_least_once'
      || !Number.isSafeInteger(value.suggested_poll_seconds) || value.suggested_poll_seconds < 1
      || value.suggested_poll_seconds > 86400 || value.has_more && value.events.length !== limit) reject();
  let sequence = 0;
  const ids = new Set();
  const events = value.events.map(event => {
    if (!object(event) || typeof event.id !== 'string' || !id.test(event.id) || ids.has(event.id)
        || !Number.isSafeInteger(event.sequence) || event.sequence <= sequence
        || typeof event.type !== 'string' || !/^[a-z][a-z0-9_.]{0,63}$/.test(event.type)
        || typeof event.resource_type !== 'string' || !/^[a-z][a-z0-9_]{0,63}$/.test(event.resource_type)
        || typeof event.resource_id !== 'string' || !id.test(event.resource_id)
        || event.case_id !== null && (typeof event.case_id !== 'string' || !id.test(event.case_id))
        || typeof event.created_at !== 'string'
        || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(event.created_at)) reject();
    sequence = event.sequence;
    ids.add(event.id);
    // Copy only the documented metadata; unknown provider fields never escape.
    return Object.freeze({ id: event.id, sequence: event.sequence, type: event.type,
      resource_type: event.resource_type, resource_id: event.resource_id,
      case_id: event.case_id, created_at: event.created_at });
  });
  return Object.freeze({ events: Object.freeze(events), next_cursor: value.next_cursor,
    has_more: value.has_more, delivery: 'at_least_once', suggested_poll_seconds: value.suggested_poll_seconds });
}

/**
 * Supply an authorized updates:read bearer and the saved opaque cursor.
 * One GET only. A second parameter permits a local transport in tests.
 * Commit processed events and next_cursor together in your own durable store.
 */
export async function readUpdates({ bearer, cursor = '', limit = 20,
  timeoutMs = MAX_TIMEOUT_MS, signal } = {}, { fetchImpl = globalThis.fetch } = {}) {
  if (typeof bearer !== 'string' || !token.test(bearer) || typeof cursor !== 'string' || cursor.length > 256
      || !Number.isSafeInteger(limit) || limit < 1 || limit > 50
      || !Number.isSafeInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > MAX_TIMEOUT_MS
      || typeof fetchImpl !== 'function'
      || signal !== undefined && !(signal instanceof AbortSignal)) reject('invalid_request');
  if (signal?.aborted) reject('cancelled');
  const url = new URL('/api/v1/updates', ORIGIN);
  url.searchParams.set('limit', String(limit));
  if (cursor) url.searchParams.set('cursor', cursor);
  const controller = new AbortController();
  const deadline = performance.now() + timeoutMs;
  let reader, response, timer, cancelWait;
  let cancelled = false, timedOut = false;
  const stopped = new Promise((_, rejectPromise) => {
    cancelWait = () => {
      cancelled = true;
      controller.abort();
      rejectPromise(new UpdatesError('cancelled'));
    };
    timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
      rejectPromise(new UpdatesError('timeout'));
    }, timeoutMs);
  });
  stopped.catch(() => {});
  signal?.addEventListener('abort', cancelWait, { once: true });
  const withinBudget = promise => Promise.race([promise, stopped]);
  const checkBudget = () => {
    if (cancelled) reject('cancelled');
    if (performance.now() >= deadline) timedOut = true;
    if (timedOut) reject('timeout');
  };
  try {
    // A signal can be aborted between the initial check and listener attachment.
    if (signal?.aborted) cancelWait();
    checkBudget();
    response = await withinBudget(fetchImpl(url.href, {
      method: 'GET', headers: { Accept: 'application/json', Authorization: 'Bearer ' + bearer },
      redirect: 'error', credentials: 'omit', cache: 'no-store', signal: controller.signal
    }));
    checkBudget();
    if (response?.redirected || response?.url && response.url !== url.href) reject('unexpected_redirect');
    if (response?.status !== 200) {
      const status = Number.isInteger(response?.status) && response.status >= 100 && response.status <= 599 ? response.status : null;
      const code = ({ 400: 'request_rejected', 401: 'authentication_required', 403: 'scope_or_origin_rejected',
        429: 'rate_limited', 503: 'service_unavailable' })[status] || 'http_error';
      throw new UpdatesError(code, status, [429, 503].includes(status) ? retryAfter(response.headers?.get('retry-after')) : null);
    }
    if (response.headers?.get('content-type')?.split(';')[0].trim().toLowerCase() !== 'application/json') reject();
    reader = response.body?.getReader?.();
    if (!reader) reject();
    let length = 0;
    const chunks = [];
    for (;;) {
      const part = await withinBudget(reader.read());
      checkBudget();
      if (part.done) break;
      if (!(part.value instanceof Uint8Array) || (length += part.value.byteLength) > MAX_BODY_BYTES) reject('response_too_large');
      chunks.push(part.value);
    }
    const bytes = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
    let value;
    try { value = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); }
    catch { reject(); }
    const result = page(value, limit);
    checkBudget();
    return result;
  } catch (error) {
    controller.abort();
    // Stream cancellation must not extend the request's total budget.
    try { Promise.resolve(reader ? reader.cancel() : response?.body?.cancel()).catch(() => {}); } catch {}
    if (cancelled) reject('cancelled');
    if (timedOut) reject('timeout');
    if (error instanceof UpdatesError && ERROR_CODES.has(error.code)) {
      const status = Number.isInteger(error.status) && error.status >= 100 && error.status <= 599 ? error.status : null;
      const delay = Number.isSafeInteger(error.retryAfterSeconds) && error.retryAfterSeconds >= 0 ? error.retryAfterSeconds : null;
      throw new UpdatesError(error.code, status, delay);
    }
    reject('transport_failed');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancelWait);
    try { reader?.releaseLock(); } catch {}
  }
}
