<template>
  <div class="page-shell">
    <AppHeader
      :status="store.status"
      :sessions="store.history"
      :active-session="store.sessionId"
      @select-session="selectSession"
      @new-session="resetSession"
      @open-streamlit="openStreamlit"
    />

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

      <section class="card">
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

const selectSession = (id: string) => {
  if (!id) return;
  store.loadSession(id);
};

const openStreamlit = () => {
  window.open('/', '_blank');
};

const exportZip = () => {
  if (!store.sessionId) return;
  window.open(`/api/export/${store.sessionId}?include_components=true`, '_blank');
};

const exportMarkdown = () => {
  if (!store.sessionId) return;
  window.open(`/api/export/${store.sessionId}`, '_blank');
};
</script>
