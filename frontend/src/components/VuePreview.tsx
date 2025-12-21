import { useEffect, useRef, useState } from 'react';
import * as VueRuntime from 'vue';
import { compileScript, compileTemplate, parse } from '@vue/compiler-sfc';

interface VuePreviewProps {
  code: string;
  className?: string;
}

const SCRIPT_HELPERS = `
const {
  ref,
  computed,
  reactive,
  watch,
  watchEffect,
  onMounted,
  onBeforeMount,
  onUnmounted,
} = Vue;
`;

export default function VuePreview({ code, className = '' }: VuePreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!code.trim()) {
      setError('No Vue component code provided.');
      return;
    }

    let app: ReturnType<typeof VueRuntime.createApp> | null = null;
    let styleEl: HTMLStyleElement | null = null;
    let disposed = false;

    const mountPreview = () => {
      const { descriptor } = parse(code);
      const template = descriptor.template?.content?.trim() || '';

      if (!template) {
        throw new Error('Missing <template> block.');
      }

      let scriptExports: Record<string, unknown> = {};
      if (descriptor.script || descriptor.scriptSetup) {
        const script = compileScript(descriptor, { id: 'preview' });
        const scriptCode = script.content
          .replace(/^\s*import[^;]+;?\s*$/gm, '')
          .replace(/export default/g, 'return');

        const scriptFn = new Function('Vue', `${SCRIPT_HELPERS}\n${scriptCode}`);
        scriptExports = (scriptFn(VueRuntime) as Record<string, unknown>) || {};
      }

      const templateResult = compileTemplate({
        source: template,
        filename: 'Component.vue',
        id: 'preview',
      });

      if (templateResult.errors.length) {
        throw new Error(String(templateResult.errors[0]));
      }

      const renderCode = templateResult.code
        .replace(/^\s*import[^;]+;?\s*$/gm, '')
        .replace(/export function render/, 'return function render')
        .replace(/export const render/, 'return function render');
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
      app.mount(containerRef.current as HTMLDivElement);
    };

    try {
      setError(null);
      containerRef.current.innerHTML = '';
      mountPreview();
    } catch (err) {
      if (!disposed) {
        setError(err instanceof Error ? err.message : 'Failed to render component.');
      }
    }

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
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
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

  return <div ref={containerRef} className={className} />;
}
