import { useEffect, useRef, useState } from 'react';
import * as VueRuntime from 'vue';
import { compileScript, compileTemplate, parse } from '@vue/compiler-sfc';
import { createGenerator } from '@unocss/core';
import presetUno from '@unocss/preset-uno';

interface VuePreviewProps {
  code: string;
  className?: string;
}

const SLIDE_WIDTH = 1920;
const SLIDE_HEIGHT = 1080;

const unoPromise = createGenerator({
  presets: [presetUno()],
});

const normalizeImports = (code: string) =>
  code
    .replace(/import\s+\{([^}]+)\}\s+from\s+['"]vue['"];?/g, (_, imports) => {
      const normalized = String(imports).replace(/\s+as\s+/g, ': ');
      return `const {${normalized}} = Vue;`;
    })
    .replace(/^\s*import[^;]+;?\s*$/gm, '');

const collectClassTokens = (root: HTMLElement) => {
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

const applyUnoStyles = async (root: HTMLElement) => {
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

export default function VuePreview({ code, className = '' }: VuePreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current || !mountRef.current) return;
    if (!code.trim()) {
      setError('No Vue component code provided.');
      return;
    }

    let app: ReturnType<typeof VueRuntime.createApp> | null = null;
    let styleEl: HTMLStyleElement | null = null;
    let unoStyleEl: HTMLStyleElement | null = null;
    let resizeObserver: ResizeObserver | null = null;
    let disposed = false;

    const updateScale = () => {
      if (!containerRef.current || !mountRef.current) return;
      const { width, height } = containerRef.current.getBoundingClientRect();
      if (!width || !height) return;
      const scale = Math.min(width / SLIDE_WIDTH, height / SLIDE_HEIGHT);
      const offsetX = Math.max((width - SLIDE_WIDTH * scale) / 2, 0);
      const offsetY = Math.max((height - SLIDE_HEIGHT * scale) / 2, 0);
      mountRef.current.style.width = `${SLIDE_WIDTH}px`;
      mountRef.current.style.height = `${SLIDE_HEIGHT}px`;
      mountRef.current.style.transformOrigin = 'top left';
      mountRef.current.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
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

    const mountPreview = async () => {
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
        styleEl = document.createElement('style');
        styleEl.textContent = styleContent;
        styleEl.dataset.vuePreview = 'true';
        document.head.appendChild(styleEl);
      }

      app = VueRuntime.createApp(component);
      app.config.globalProperties.$slidev = ensureSlidevGlobals();
      app.config.globalProperties.$frontmatter = {};
      app.directive('click', {
        mounted() {},
        updated() {},
      });
      app.directive('motion', {
        mounted() {},
        updated() {},
      });
      app.component(
        'v-clicks',
        VueRuntime.defineComponent({
          name: 'v-clicks',
          setup(_, { slots }) {
            return () => VueRuntime.h('div', slots.default ? slots.default() : []);
          },
        })
      );
      app.mount(mountRef.current as HTMLDivElement);
      updateScale();
      resizeObserver = new ResizeObserver(updateScale);
      resizeObserver.observe(containerRef.current as HTMLDivElement);
      unoStyleEl = await applyUnoStyles(mountRef.current as HTMLDivElement);
      if (disposed && unoStyleEl) {
        unoStyleEl.remove();
        unoStyleEl = null;
      }
    };

    const run = async () => {
      try {
        setError(null);
        if (mountRef.current) {
          mountRef.current.innerHTML = '';
        }
        await mountPreview();
      } catch (err) {
        if (!disposed) {
          setError(err instanceof Error ? err.message : 'Failed to render component.');
        }
      }
    };
    void run();

    return () => {
      disposed = true;
      if (app) {
        app.unmount();
        app = null;
      }
      if (styleEl) {
        styleEl.remove();
        styleEl = null;
      }
      if (unoStyleEl) {
        unoStyleEl.remove();
        unoStyleEl = null;
      }
      if (resizeObserver) {
        resizeObserver.disconnect();
        resizeObserver = null;
      }
      if (mountRef.current) {
        mountRef.current.innerHTML = '';
      }
    };
  }, [code]);

  if (error) {
    return (
      <div className={`text-sm text-red-600 ${className}`}>
        {error}
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`relative overflow-hidden ${className}`}>
      <div ref={mountRef} className="relative" />
    </div>
  );
}
