import { createPreviewState, renderVueComponent, cleanupPreview } from './VuePreview';

const state = createPreviewState();

type ComponentMap = Record<string, string>;

function decodeBase64(value: string): string {
  const bytes = Uint8Array.from(atob(value), (char) => char.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

function getCodeFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search);
  const codeBase64 = params.get('code');
  if (!codeBase64) return null;
  
  try {
    return decodeBase64(codeBase64);
  } catch (e) {
    console.error('Failed to decode base64 code:', e);
    return null;
  }
}

function parseComponentsPayload(payload: string): ComponentMap | null {
  try {
    const json = decodeBase64(payload);
    const parsed = JSON.parse(json) as Record<string, string>;
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return null;
    }
    return parsed;
  } catch (e) {
    console.error('Failed to decode components payload:', e);
    return null;
  }
}

function getComponentsFromUrl(): ComponentMap | null {
  const params = new URLSearchParams(window.location.search);
  const componentsBase64 = params.get('components');
  if (!componentsBase64) return null;
  return parseComponentsPayload(componentsBase64);
}

function normalizeComponents(payload: unknown): ComponentMap | null {
  if (!payload) return null;
  if (typeof payload === 'string') {
    return parseComponentsPayload(payload);
  }
  if (typeof payload === 'object' && !Array.isArray(payload)) {
    return payload as ComponentMap;
  }
  return null;
}

function showError(message: string): void {
  const container = document.getElementById('preview-container');
  if (container) {
    container.innerHTML = `<div class="error-message">${message}</div>`;
  }
}

function showLoading(): void {
  const container = document.getElementById('preview-container');
  if (container) {
    container.innerHTML = `
      <div id="preview-mount"></div>
      <div class="loading-message" id="loading">Loading preview...</div>
    `;
  }
}

async function renderPreview(): Promise<void> {
  const containerEl = document.getElementById('preview-container');
  const mountEl = document.getElementById('preview-mount');
  
  if (!containerEl || !mountEl) {
    showError('Preview container not found');
    return;
  }
  
  const code = getCodeFromUrl();
  const components = getComponentsFromUrl();
  
  if (!code) {
    showError('No content provided. Use ?code=base64_encoded_slidev_markdown');
    return;
  }
  
  try {
    const rendererOptions = components ? { sfcComponents: components } : undefined;
    await renderVueComponent(code, containerEl, mountEl, state, rendererOptions);
    // Remove loading message
    const loadingEl = document.getElementById('loading');
    if (loadingEl) loadingEl.remove();
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : 'Failed to render component';
    showError(errorMsg);
    console.error('Render error:', e);
  }
}

// Handle postMessage for code updates (alternative to URL params)
window.addEventListener('message', async (event) => {
  if (event.data && event.data.type === 'preview-code') {
    const code = event.data.code;
    const components = normalizeComponents(event.data.components);
    if (!code) return;
    
    const containerEl = document.getElementById('preview-container');
    let mountEl = document.getElementById('preview-mount');
    
    if (!containerEl) return;
    
    // Reset container if needed
    if (!mountEl) {
      containerEl.innerHTML = '<div id="preview-mount"></div>';
      mountEl = document.getElementById('preview-mount');
    }
    
    if (!mountEl) return;
    
    try {
      const rendererOptions = components ? { sfcComponents: components } : undefined;
      await renderVueComponent(code, containerEl, mountEl, state, rendererOptions);
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : 'Failed to render component';
      showError(errorMsg);
      console.error('Render error:', e);
    }
  }
});

// Initialize
showLoading();
renderPreview();
