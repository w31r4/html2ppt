import { createPreviewState, renderVueComponent, cleanupPreview } from './VuePreview';

const state = createPreviewState();

function getCodeFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search);
  const codeBase64 = params.get('code');
  if (!codeBase64) return null;
  
  try {
    return atob(codeBase64);
  } catch (e) {
    console.error('Failed to decode base64 code:', e);
    return null;
  }
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
  
  if (!code) {
    showError('No content provided. Use ?code=base64_encoded_slidev_markdown');
    return;
  }
  
  try {
    await renderVueComponent(code, containerEl, mountEl, state);
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
      await renderVueComponent(code, containerEl, mountEl, state);
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