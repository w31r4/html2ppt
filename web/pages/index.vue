<template>
  <aside class="w-[400px] flex flex-col border-r border-border-light dark:border-border-dark bg-white/90 dark:bg-[#15161a]/90 shrink-0 h-full relative z-10 backdrop-blur" aria-label="Chat workspace">
    <div class="p-6 border-b border-border-light dark:border-border-dark flex justify-between items-center">
      <div>
        <h2 class="font-bold text-xl text-gray-900 dark:text-white">Workspace</h2>
        <div class="flex items-center gap-2 mt-1">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse" v-if="statusLabel" aria-hidden="true"></span>
          <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider" role="status" aria-live="polite">{{ statusLabel || 'Ready' }}</span>
        </div>
      </div>
      <button
        class="px-3 py-1.5 text-xs font-medium bg-gray-100/80 dark:bg-gray-800/80 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-xl transition-colors text-gray-700 dark:text-gray-300 shadow-sm"
        @click="resetSession"
        aria-label="Start a new session"
      >
        New Session
      </button>
    </div>

    <WorkspaceProgress :stage="store.stage" :status="store.status" :progress="store.progress" />

    <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar flex flex-col" role="log" aria-label="Chat messages" aria-live="polite">
      <div class="text-center mb-6">
        <p class="text-xs text-gray-400 dark:text-gray-500">Today, {{ new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</p>
      </div>

      <ChatThread
        :messages="store.messages"
        :is-loading="isProcessing"
        :loading-text="statusLabel"
      />

      <div class="mt-auto pt-4">
        <CommandBar :chips="chips" @append="appendChip" />
      </div>
    </div>

    <div class="p-4 border-t border-border-light dark:border-border-dark bg-white/90 dark:bg-[#15161a]/90">
      <ChatComposer v-model="prompt" @send="send" />
    </div>
  </aside>

  <main class="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark relative" aria-label="Presentation preview and editing">
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 flex flex-col gap-6 min-h-0">
        <div class="flex justify-between items-center px-1">
          <div class="flex items-center gap-3">
            <h2 class="font-bold text-2xl text-gray-900 dark:text-white">Live Preview</h2>
            <span class="text-sm text-gray-500 dark:text-gray-400">Slidev output with Vue components</span>
          </div>
          <div class="flex gap-3" role="group" aria-label="Export options">
            <button
              class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white/80 dark:bg-card-dark border border-gray-200/80 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!store.result"
              @click="exportMarkdown"
              :aria-label="store.result ? 'Export presentation as Markdown' : 'Generate a presentation first to export'"
            >
              Export Markdown
            </button>
            <button
              class="px-4 py-2 text-sm font-medium text-white bg-primary rounded-xl hover:bg-primary-dark transition-colors shadow-sm shadow-primary/30 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!store.result"
              @click="exportZip"
              :aria-label="store.result ? 'Export presentation as ZIP archive' : 'Generate a presentation first to export'"
            >
              <span class="material-icons-outlined text-sm" aria-hidden="true">download</span>
              Export ZIP
            </button>
          </div>
        </div>

        <div class="bg-card-light dark:bg-card-dark rounded-3xl shadow-[0_20px_45px_rgba(15,23,42,0.12)] border border-border-light dark:border-border-dark overflow-hidden flex flex-col relative group h-[55vh] min-h-[360px]" role="region" aria-label="Slide preview">
          <PreviewStage
            :slides-md="store.result?.slides_md || ''"
            :components="store.result?.components || []"
            class="h-full w-full"
          />
          <div v-if="store.error" class="absolute bottom-4 left-4 right-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm" role="alert">
            {{ store.error }}
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6 pb-6 min-h-[480px]">
          <div class="bg-card-light dark:bg-card-dark rounded-3xl p-5 shadow-sm border border-border-light dark:border-border-dark flex flex-col overflow-hidden h-[clamp(420px,45vh,640px)]" role="region" aria-label="Outline editor">
            <OutlineEditor
              :outline="store.outline"
              :status="store.status"
              @save="saveOutline"
              @confirm="confirmOutline"
            />
          </div>
          <div class="bg-card-light dark:bg-card-dark rounded-3xl p-5 shadow-sm border border-border-light dark:border-border-dark flex flex-col overflow-hidden h-[clamp(420px,45vh,640px)]" role="region" aria-label="Code artifacts viewer">
            <CodeViewer :result="store.result" />
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useSessionStore } from '@/stores/session';

const store = useSessionStore();
const prompt = ref('');

const chips = [
  'Make it technical',
  'Warm palette',
  'Add comparison',
  'Architecture diagrams',
  '10 slides max'
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

const isProcessing = computed(() => {
  const processingStatuses = ['pending', 'generating', 'assembling'];
  return store.status && processingStatuses.includes(store.status);
});
</script>
