import { defineConfig, presetUno, presetWebFonts } from 'unocss';

export default defineConfig({
  presets: [
    presetUno(),
    presetWebFonts({
      provider: 'google',
      fonts: {
        sans: 'Inter:300,400,500,600,700',
        mono: 'JetBrains Mono:400,500',
      },
    }),
  ],
  theme: {
    colors: {
      primary: {
        DEFAULT: '#2D9C8F',
        dark: '#1E7A6E',
      },
      background: {
        light: '#F2EFE9',
        dark: '#1a1b1e',
      },
      card: {
        light: '#FFFFFF',
        dark: '#25262b',
      },
      text: {
        light: '#374151',
        dark: '#C1C2C5',
      },
      border: {
        light: '#E5E7EB',
        dark: '#2C2E33',
      },
    },
  },
  shortcuts: {
    'card': 'bg-card-light dark:bg-card-dark border border-border-light dark:border-border-dark rounded-lg shadow-sm',
    'btn': 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-colors',
    'btn-primary': 'bg-primary hover:bg-primary-dark text-white shadow-sm shadow-primary/30',
    'btn-ghost': 'bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700',
    'icon-btn': 'p-2 rounded-xl text-gray-400 hover:text-primary hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors',
    'custom-scrollbar': 'scrollbar scrollbar-w-1.5 scrollbar-track-transparent scrollbar-thumb-gray-300/30 hover:scrollbar-thumb-gray-300/50 scrollbar-thumb-rounded-full',
  }
});
