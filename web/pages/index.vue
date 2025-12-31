<template>
  <aside class="w-[400px] flex flex-col border-r border-border-light dark:border-border-dark bg-white dark:bg-[#1C1C1F] shrink-0 h-full relative z-10">
    <div class="p-6 border-b border-border-light dark:border-border-dark flex justify-between items-center">
      <div>
        <h2 class="font-bold text-xl text-gray-900 dark:text-white">Workspace</h2>
        <div class="flex items-center gap-2 mt-1">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse" v-if="statusLabel"></span>
          <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ statusLabel || 'Ready' }}</span>
        </div>
      </div>
      <button class="px-3 py-1.5 text-xs font-medium bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md transition-colors text-gray-700 dark:text-gray-300" @click="resetSession">
        New Session
      </button>
    </div>

    <WorkspaceProgress :stage="store.stage" :status="store.status" :progress="store.progress" />

    <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar flex flex-col">
      <div class="text-center mb-6">
        <p class="text-xs text-gray-400 dark:text-gray-500">Today, {{ new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</p>
      </div>
      
      <ChatThread :messages="store.messages" />
      
      <div class="mt-auto pt-4">
        <CommandBar :chips="chips" @append="appendChip" />
      </div>
    </div>

    <div class="p-4 border-t border-border-light dark:border-border-dark bg-white dark:bg-[#1C1C1F]">
      <ChatComposer v-model="prompt" @send="send" />
    </div>
  </aside>

  <main class="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark relative">
    <div class="flex-1 p-6 pb-0 flex flex-col min-h-0">
      <div class="flex justify-between items-center mb-4 px-1">
        <div class="flex items-center gap-3">
          <h2 class="font-bold text-2xl text-gray-900 dark:text-white">Live Preview</h2>
          <span class="text-sm text-gray-500 dark:text-gray-400">Slidev output with Vue components</span>
        </div>
        <div class="flex gap-3">
          <button class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-card-dark border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm" :disabled="!store.result" @click="exportMarkdown">
            Export Markdown
          </button>
          <button class="px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors shadow-sm shadow-primary/30 flex items-center gap-2" :disabled="!store.result" @click="exportZip">
            <span class="material-icons-outlined text-sm">download</span>
            Export ZIP
          </button>
        </div>
      </div>
      
      <div class="flex-1 bg-card-light dark:bg-card-dark rounded-2xl shadow-lg border border-border-light dark:border-border-dark overflow-hidden flex flex-col relative group mb-6">
        <PreviewStage
          :slides-md="store.result?.slides_md || ''"
          :components="store.result?.components || []"
          class="h-full w-full"
        />
        <div v-if="store.error" class="absolute bottom-4 left-4 right-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {{ store.error }}
        </div>
      </div>
    </div>

    <div class="h-[300px] p-6 pt-0 grid grid-cols-2 gap-6 shrink-0">
      <div class="bg-card-light dark:bg-card-dark rounded-2xl p-5 shadow-sm border border-border-light dark:border-border-dark flex flex-col h-full overflow-hidden">
        <OutlineEditor
          :outline="store.outline"
          :status="store.status"
          @save="saveOutline"
          @confirm="confirmOutline"
        />
      </div>
      <div class="bg-card-light dark:bg-card-dark rounded-2xl p-5 shadow-sm border border-border-light dark:border-border-dark flex flex-col h-full overflow-hidden">
        <CodeViewer :result="store.result" />
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
</script>
