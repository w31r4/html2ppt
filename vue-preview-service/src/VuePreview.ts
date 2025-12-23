import * as VueRuntime from 'vue';
import { compileScript, compileTemplate, parse } from '@vue/compiler-sfc';
import { createGenerator } from '@unocss/core';
import presetUno from '@unocss/preset-uno';

const SLIDE_WIDTH = 1920;
const SLIDE_HEIGHT = 1080;

const unoPromise = createGenerator({
  presets: [presetUno()],
});

const normalizeImports = (code: string): string =>
  code
    .replace(/import\s+\{([^}]+)\}\s+from\s+['"]vue['"];?/g, (_, imports) => {
      const normalized = String(imports).replace(/\s+as\s+/g, ': ');
      return `const {${normalized}} = Vue;`;
    })
    .replace(/^\s*import[^;]+;?\s*$/gm, '');

const collectClassTokens = (root: HTMLElement): string[] => {
  const tokens = new Set<string>();
  const elements = [root, ...Array.from(root.querySelectorAll<HTMLElement>('*'))];
  for (const element of elements) {
    const classValue =
      typeof element.className === 'string'
        ? element.className
        : element.getAttribute('class') || '';
    classValue
      .split(/\s+/)
      .map((token) => token.trim())
      .filter(Boolean)
      .forEach((token) => tokens.add(token));
  }
  return Array.from(tokens);
};

const applyUnoStyles = async (root: HTMLElement): Promise<HTMLStyleElement | null> => {
  const uno = await unoPromise;
  const tokens = collectClassTokens(root);
  if (!tokens.length) return null;
  const { css } = await uno.generate(tokens.join(' '), { preflights: false });
  if (!css.trim()) return null;
  const style = document.createElement('style');
  style.textContent = css;
  style.dataset.unoPreview = 'true';
  document.head.appendChild(style);
  return style;
};

const ensureSlidevGlobals = () => {
  const nav = {
    clicks: 999,
    currentPage: 1,
    total: 1,
    next: () => {},
    prev: () => {},
    go: () => {},
    goto: () => {},
  };
  return {
    nav,
    themeConfigs: {},
    configs: {},
  };
};

export interface PreviewState {
  app: ReturnType<typeof VueRuntime.createApp> | null;
  styleEl: HTMLStyleElement | null;
  unoStyleEl: HTMLStyleElement | null;
  resizeObserver: ResizeObserver | null;
}

export function createPreviewState(): PreviewState {
  return {
    app: null,
    styleEl: null,
    unoStyleEl: null,
    resizeObserver: null,
  };
}

export function cleanupPreview(state: PreviewState, mountEl: HTMLElement | null): void {
  if (state.app) {
    state.app.unmount();
    state.app = null;
  }
  if (state.styleEl) {
    state.styleEl.remove();
    state.styleEl = null;
  }
  if (state.unoStyleEl) {
    state.unoStyleEl.remove();
    state.unoStyleEl = null;
  }
  if (state.resizeObserver) {
    state.resizeObserver.disconnect();
    state.resizeObserver = null;
  }
  if (mountEl) {
    mountEl.innerHTML = '';
  }
}

export async function renderVueComponent(
  code: string,
  containerEl: HTMLElement,
  mountEl: HTMLElement,
  state: PreviewState
): Promise<void> {
  // Cleanup previous state
  cleanupPreview(state, mountEl);

  if (!code.trim()) {
    throw new Error('No Vue component code provided.');
  }

  const updateScale = () => {
    const { width, height } = containerEl.getBoundingClientRect();
    if (!width || !height) return;
    const scale = Math.min(width / SLIDE_WIDTH, height / SLIDE_HEIGHT);
    const offsetX = Math.max((width - SLIDE_WIDTH * scale) / 2, 0);
    const offsetY = Math.max((height - SLIDE_HEIGHT * scale) / 2, 0);
    mountEl.style.width = `${SLIDE_WIDTH}px`;
    mountEl.style.height = `${SLIDE_HEIGHT}px`;
    mountEl.style.transformOrigin = 'top left';
    mountEl.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
  };

  const { descriptor } = parse(code);
  const template = descriptor.template?.content?.trim() || '';

  if (!template) {
    throw new Error('Missing <template> block.');
  }

  let scriptExports: Record<string, unknown> = {};
  let bindingMetadata: Record<string, unknown> | undefined;
  
  if (descriptor.script || descriptor.scriptSetup) {
    const script = compileScript(descriptor, { id: 'preview' });
    bindingMetadata = script.bindings as Record<string, unknown>;
    const scriptCode = normalizeImports(script.content)
      .replace(/export default/g, 'return')
      .replace(/export const /g, 'const ')
      .replace(/export function /g, 'function ');

    const scriptFn = new Function('Vue', scriptCode);
    scriptExports = (scriptFn(VueRuntime) as Record<string, unknown>) || {};
  }

  const templateResult = compileTemplate({
    source: template,
    filename: 'Component.vue',
    id: 'preview',
    compilerOptions: {
      isCustomElement: (tag) => tag.startsWith('v-'),
      bindingMetadata,
    },
  });

  if (templateResult.errors.length) {
    throw new Error(String(templateResult.errors[0]));
  }

  const renderCode = normalizeImports(templateResult.code)
    .replace(/export function render/, 'return function render')
    .replace(/export const render/, 'return function render')
    .replace(/export const /g, 'const ');
  const render = new Function('Vue', renderCode)(VueRuntime);

  const component = {
    ...scriptExports,
    render,
  };

  if (descriptor.styles?.length) {
    const styleContent = descriptor.styles.map((style) => style.content).join('\n');
    state.styleEl = document.createElement('style');
    state.styleEl.textContent = styleContent;
    state.styleEl.dataset.vuePreview = 'true';
    document.head.appendChild(state.styleEl);
  }

  state.app = VueRuntime.createApp(component);
  state.app.config.globalProperties.$slidev = ensureSlidevGlobals();
  state.app.config.globalProperties.$frontmatter = {};
  
  state.app.directive('click', {
    mounted() {},
    updated() {},
  });
  state.app.directive('motion', {
    mounted() {},
    updated() {},
  });
  
  state.app.component(
    'v-clicks',
    VueRuntime.defineComponent({
      name: 'v-clicks',
      setup(_, { slots }) {
        return () => VueRuntime.h('div', slots.default ? slots.default() : []);
      },
    })
  );
  
  state.app.mount(mountEl);
  updateScale();
  
  state.resizeObserver = new ResizeObserver(updateScale);
  state.resizeObserver.observe(containerEl);
  
  state.unoStyleEl = await applyUnoStyles(mountEl);
}