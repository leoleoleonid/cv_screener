const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';

async function request<T>(
  path: string,
  options: RequestInit & { json?: unknown } = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const payload =
    options.json !== undefined ? JSON.stringify(options.json) : options.body;

  const response = await fetch(url, { ...options, headers, body: payload });
  let data: unknown = null;
  try {
    data = await response.json();
  } catch {
    // ignore JSON errors; we'll throw below if needed
  }

  if (!response.ok) {
    const detail =
      typeof (data as { detail?: unknown })?.detail === 'string'
        ? (data as { detail: string }).detail
        : response.statusText || 'Request failed';
    throw new Error(detail);
  }

  return data as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'GET' });
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', json: body });
}
