export { createGenerator } from '@unocss/core';
export { default as presetAttributify } from '@unocss/preset-attributify';
export { default as presetIcons } from '@unocss/preset-icons/browser';
export { default as presetUno } from '@unocss/preset-uno';
export { default as presetWebFonts } from '@unocss/preset-web-fonts';

export function defineConfig<T>(config: T): T {
  return config;
}
