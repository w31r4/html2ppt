import { defineConfig, presetUno } from 'unocss';

export default defineConfig({
  presets: [presetUno()],
  shortcuts: {
    'card': 'rounded-[var(--radius-lg)] bg-[var(--surface)] border border-[var(--line)] shadow-[var(--shadow-soft)]',
    'card-warm': 'rounded-[var(--radius-lg)] bg-[var(--surface-warm)] border border-[var(--line)] shadow-[var(--shadow-soft)]',
    'btn': 'inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition-colors',
    'btn-primary': 'btn bg-[var(--accent-teal)] text-white hover:bg-[#278f89]',
    'btn-ghost': 'btn border border-[var(--line)] text-[var(--ink)] hover:bg-[var(--surface-warm)]',
    'pill': 'inline-flex items-center gap-2 rounded-full border border-[var(--line)] px-3 py-1 text-xs uppercase tracking-[0.2em]'
  }
});
