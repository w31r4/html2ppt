<template>
  <div class="workspace-page">
    <header class="workspace-header">
      <div class="header-title">
        <h1>Workspace</h1>
        <div class="status-pill" v-if="statusLabel">
          <span class="status-dot"></span>
          <span>{{ statusLabel }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-ghost" type="button" @click="resetSession">
          New Session
        </button>
      </div>
    </header>

    <main class="grid-shell">
      <section class="chat-panel card">
        <div class="card-header">
          <div>
            <h2>Conversation</h2>
            <p>Collaborate with the agent to shape your deck.</p>
          </div>
        </div>
        <div class="card-body">
          <ChatThread :messages="store.messages" />
          <CommandBar :chips="chips" @append="appendChip" />
          <ChatComposer v-model="prompt" @send="send" />
        </div>
      </section>

      <section class="card preview-card">
        <div class="card-header">
          <div>
            <h2>Live Preview</h2>
            <p>Slidev output with Vue components rendered live.</p>
          </div>
          <div class="header-actions">
            <button class="btn-ghost" type="button" :disabled="!store.result" @click="exportMarkdown">
              Export Markdown
            </button>
            <button class="btn-primary" type="button" :disabled="!store.result" @click="exportZip">
              Export ZIP
            </button>
          </div>
        </div>
        <div class="card-body">
          <PreviewStage
            :slides-md="store.result?.slides_md || ''"
            :components="store.result?.components || []"
          />
          <div v-if="store.error" class="composer-hint" style="margin-top: 12px; color: #b24d3b;">
            {{ store.error }}
          </div>
        </div>
      </section>
    </main>

    <section class="grid-shell" style="margin-top: 24px;">
      <section class="card soft">
        <StepTimeline :stage="store.stage" :status="store.status" :progress="store.progress" />
      </section>
      <section class="artifact-grid">
        <div class="card">
          <OutlineEditor
            :outline="store.outline"
            :status="store.status"
            @save="saveOutline"
            @confirm="confirmOutline"
          />
        </div>
        <div class="card">
          <CodeViewer :result="store.result" />
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
const store = useSessionStore();
const prompt = ref('');

const chips = [
  'Make it technical and concise',
  'Use a warm neutral palette',
  'Add a comparison table',
  'Include an animated hero slide',
  'Focus on architecture diagrams',
  'Keep it to 10 slides'
];

onMounted(() => {
  store.initHistory();
  store.ensureIntro();
});

const send = async () => {
  const value = prompt.value;
  prompt.value = '';
  await store.sendPrompt(value);
};

const appendChip = (chip: string) => {
  prompt.value = `${prompt.value} ${chip}`.trim();
};

const saveOutline = async (outline: string) => {
  await store.updateOutline(outline);
};

const confirmOutline = async () => {
  await store.confirmOutline();
};

const resetSession = () => {
  store.resetSession();
};

const exportZip = () => {
  if (!store.sessionId) return;
  window.open(`/api/export/${store.sessionId}?include_components=true`, '_blank');
};

const exportMarkdown = () => {
  if (!store.sessionId) return;
  window.open(`/api/export/${store.sessionId}`, '_blank');
};
const statusLabel = computed(() => {
  if (!store.status || store.status === 'idle') return '';
  const labels: Record<string, string> = {
    pending: 'Preparing',
    outline_ready: 'Outline Ready',
    draft: 'Outline Draft',
    confirmed: 'Confirmed',
    generating: 'Generating',
    assembling: 'Assembling',
    completed: 'Ready',
    error: 'Error'
  };
  return labels[store.status] || store.status;
});
</script>

<style scoped>
.workspace-page {
  animation: rise 0.6s ease both;
}

.workspace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title h1 {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  margin: 0;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--line);
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-teal);
  box-shadow: 0 0 0 3px rgba(47, 167, 160, 0.15);
}

.preview-card {
  min-height: 600px;
}
</style>
