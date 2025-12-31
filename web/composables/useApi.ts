export function useApi() {
  const config = useRuntimeConfig();
  let rawBase = (config.public.apiBase || '/api').replace(/\/$/, '');
  if (
    process.client &&
    rawBase === '/api' &&
    window.location.hostname === 'localhost' &&
    (process.dev || import.meta.dev)
  ) {
    rawBase = 'http://localhost:8000/api';
  }
  const origin = process.client ? window.location.origin : useRequestURL().origin;
  const base = rawBase.startsWith('http')
    ? rawBase
    : `${origin}${rawBase.startsWith('/') ? '' : '/'}${rawBase}`;

  const request = async <T>(path: string, options: Record<string, unknown> = {}): Promise<T> => {
    const safePath = path.startsWith('/') ? path : `/${path}`;
    const url = `${base}${safePath}`;
    return await $fetch<T>(url, options);
  };

  return { request, base };
}
