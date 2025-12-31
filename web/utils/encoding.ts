export function encodeBase64(value: string): string {
  if (typeof value !== 'string') {
    return '';
  }
  if (typeof window === 'undefined') {
    return Buffer.from(value, 'utf-8').toString('base64');
  }
  const bytes = new TextEncoder().encode(value);
  let binary = '';
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}

export function encodeJsonBase64(payload: unknown): string {
  return encodeBase64(JSON.stringify(payload ?? {}));
}
