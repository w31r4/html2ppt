import { createApp, h } from 'vue';
import { SlideRenderer, SlidesRender, type SlideSource } from 'slidev-parser';
import 'slidev-parser/index.css';

export interface PreviewState {
  app: ReturnType<typeof createApp> | null;
}

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
  state: PreviewState
): Promise<void> {
  cleanupPreview(state, mountEl);

  if (!code.trim()) {
    throw new Error('No content provided.');
  }

  const slides = parseSlides(code);
  if (!slides.length) {
    throw new Error('No valid Slidev slides parsed.');
  }

  state.app = createApp({
    setup() {
      return () => h(SlidesRender, {
        slides,
      });
    },
  });

  state.app.mount(mountEl);
}
