import { createApp, h, type Component } from 'vue';
import { SlideRenderer, SlidesRender, type RendererOptions, type SlideSource } from 'slidev-parser';
import 'slidev-parser/index.css';

export interface PreviewState {
  app: ReturnType<typeof createApp> | null;
}

type SlideSlotProps = {
  component: Component;
  index: number;
};

export function createPreviewState(): PreviewState {
  return {
    app: null,
  };
}

export function cleanupPreview(state: PreviewState, mountEl: HTMLElement | null): void {
  if (state.app) {
    state.app.unmount();
    state.app = null;
  }
  if (mountEl) {
    mountEl.innerHTML = '';
  }
}

function parseSlides(markdown: string): SlideSource[] {
  try {
    const slides = SlideRenderer.parse(markdown) as SlideSource[];
    return slides.map((slide) => ({
      ...slide,
      note: slide.note ?? '',
    }));
  } catch (error) {
    console.error('Failed to parse Slidev markdown', error);
    return [];
  }
}

export async function renderVueComponent(
  code: string,
  containerEl: HTMLElement,
  mountEl: HTMLElement,
  state: PreviewState,
  rendererOptions?: RendererOptions
): Promise<void> {
  cleanupPreview(state, mountEl);

  if (!code.trim()) {
    throw new Error('No content provided.');
  }

  const slides = parseSlides(code);
  if (!slides.length) {
    throw new Error('No valid Slidev slides parsed.');
  }

  const slideBaseId = `preview-${Math.random().toString(36).slice(2, 8)}`;

  state.app = createApp({
    setup() {
      return () =>
        h(
          SlidesRender,
          {
            slides,
            rendererOptions,
            id: slideBaseId,
          },
          {
            slide: ({ component, index }: SlideSlotProps) =>
              h(
                'div',
                {
                  class: 'preview-scale-target',
                  'data-slide-index': index,
                },
                [h(component, { id: `${slideBaseId}-${index}` })]
              ),
          }
        );
    },
  });

  state.app.mount(mountEl);
}
