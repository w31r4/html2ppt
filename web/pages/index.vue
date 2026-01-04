<template>
  <!-- Mobile Tab Switcher -->
  <div class="md:hidden flex border-b border-border-light dark:border-border-dark bg-card-light dark:bg-card-dark shrink-0">
    <button
      class="flex-1 py-3 text-sm font-medium transition-colors"
      :class="activePanel === 'chat' ? 'text-primary border-b-2 border-primary' : 'text-gray-500'"
      @click="activePanel = 'chat'"
    >
      Chat
    </button>
    <button
      class="flex-1 py-3 text-sm font-medium transition-colors"
      :class="activePanel === 'preview' ? 'text-primary border-b-2 border-primary' : 'text-gray-500'"
      @click="activePanel = 'preview'"
    >
      Preview
    </button>
    <button
      class="flex-1 py-3 text-sm font-medium transition-colors"
      :class="activePanel === 'code' ? 'text-primary border-b-2 border-primary' : 'text-gray-500'"
      @click="activePanel = 'code'"
    >
      Code
    </button>
  </div>

  <!-- Chat Sidebar (Desktop always visible, Mobile conditional) -->
  <aside
    class="flex flex-col border-r border-border-light dark:border-border-dark bg-white/90 dark:bg-[#15161a]/90 shrink-0 relative z-10 backdrop-blur
           w-full md:w-[360px] lg:w-[400px]
           h-full"
    :class="{ 'hidden md:flex': activePanel !== 'chat' }"
    aria-label="Chat workspace"
  >
    <div class="p-4 md:p-6 border-b border-border-light dark:border-border-dark flex justify-between items-center">
      <div>
        <h2 class="font-bold text-lg md:text-xl text-gray-900 dark:text-white">Workspace</h2>
        <div class="flex items-center gap-2 mt-1">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse" v-if="statusLabel" aria-hidden="true"></span>
          <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider" role="status" aria-live="polite">{{ statusLabel || 'Ready' }}</span>
        </div>
      </div>
      <button
        class="px-3 py-1.5 text-xs font-medium bg-gray-100/80 dark:bg-gray-800/80 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-xl transition-colors text-gray-700 dark:text-gray-300 shadow-sm focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:outline-none"
        @click="resetSession"
        aria-label="Start a new session"
      >
        New Session
      </button>
    </div>

    <WorkspaceProgress :stage="store.stage" :status="store.status" :progress="store.progress" />

    <div class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar flex flex-col" role="log" aria-label="Chat messages" aria-live="polite">
      <div class="text-center mb-4 md:mb-6">
        <p class="text-xs text-gray-400 dark:text-gray-500">Today, {{ formattedTime }}</p>
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

    <div class="p-3 md:p-4 border-t border-border-light dark:border-border-dark bg-white/90 dark:bg-[#15161a]/90">
      <ChatComposer v-model="prompt" @send="send" />
    </div>
  </aside>

  <!-- Main Content Area (Desktop always visible, Mobile conditional) -->
  <main
    class="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark relative"
    :class="{ 'hidden md:flex': activePanel === 'chat' }"
    aria-label="Presentation preview and editing"
  >
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-4 md:p-6 flex flex-col gap-4 md:gap-6 min-h-0">
        <!-- Header with Export Buttons -->
        <div
          class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-1"
          :class="{ 'hidden md:flex': activePanel === 'code' }"
        >
          <div class="flex items-center gap-3">
            <h2 class="font-bold text-xl md:text-2xl text-gray-900 dark:text-white">Live Preview</h2>
            <span class="text-xs md:text-sm text-gray-500 dark:text-gray-400 hidden sm:inline">Slidev output with Vue components</span>
          </div>
          <div class="flex gap-2 md:gap-3 w-full sm:w-auto" role="group" aria-label="Export options">
            <button
              class="flex-1 sm:flex-none px-3 md:px-4 py-2 text-xs md:text-sm font-medium text-gray-700 dark:text-gray-200 bg-white/80 dark:bg-card-dark border border-gray-200/80 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:outline-none"
              :disabled="!store.result"
              @click="exportMarkdown"
              :aria-label="store.result ? 'Export presentation as Markdown' : 'Generate a presentation first to export'"
            >
              <span class="hidden sm:inline">Export </span>Markdown
            </button>
            <button
              class="flex-1 sm:flex-none px-3 md:px-4 py-2 text-xs md:text-sm font-medium text-white bg-primary rounded-xl hover:bg-primary-dark transition-colors shadow-sm shadow-primary/30 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:outline-none"
              :disabled="!store.result"
              @click="exportZip"
              :aria-label="store.result ? 'Export presentation as ZIP archive' : 'Generate a presentation first to export'"
            >
              <span class="material-symbols-rounded text-sm" aria-hidden="true">download</span>
              <span class="hidden sm:inline">Export </span>ZIP
            </button>
          </div>
        </div>

        <!-- Preview Stage (visible on preview panel or desktop) -->
        <div
          class="bg-card-light dark:bg-card-dark rounded-2xl md:rounded-3xl shadow-[0_20px_45px_rgba(15,23,42,0.12)] border border-border-light dark:border-border-dark overflow-hidden flex flex-col relative group h-[50vh] md:h-[55vh] min-h-[280px] md:min-h-[360px]"
          :class="{ 'hidden md:flex': activePanel === 'code' }"
          role="region"
          aria-label="Slide preview"
        >
          <PreviewStage
            :slides-md="store.result?.slides_md || ''"
            :components="store.result?.components || []"
            class="h-full w-full"
          />
          <div v-if="store.error" class="absolute bottom-4 left-4 right-4 p-3 md:p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm" role="alert">
            {{ store.error }}
          </div>
        </div>

        <!-- Outline and Code Panels -->
        <div
          class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 pb-6"
          :class="{ 'hidden md:grid': activePanel === 'preview' }"
        >
          <div
            class="bg-card-light dark:bg-card-dark rounded-2xl md:rounded-3xl p-4 md:p-5 shadow-sm border border-border-light dark:border-border-dark flex flex-col overflow-hidden h-[400px] md:h-[clamp(420px,45vh,640px)]"
            role="region"
            aria-label="Outline editor"
          >
            <OutlineEditor
              :outline="store.outline"
              :status="store.status"
              @save="saveOutline"
              @confirm="confirmOutline"
            />
          </div>
          <div
            class="bg-card-light dark:bg-card-dark rounded-2xl md:rounded-3xl p-4 md:p-5 shadow-sm border border-border-light dark:border-border-dark flex flex-col overflow-hidden h-[400px] md:h-[clamp(420px,45vh,640px)]"
            role="region"
            aria-label="Code artifacts viewer"
          >
            <CodeViewer :result="store.result" />
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';

import { useSessionStore } from '@/stores/session';

const store = useSessionStore();
const prompt = ref('');
const activePanel = ref<'chat' | 'preview' | 'code'>('chat');
const formattedTime = ref('');

const chips = [
  'Make it technical',
  'Warm palette',
  'Add comparison',
  'Architecture diagrams',
  '10 slides max'
];

// Update time every minute instead of every render
let timeInterval: ReturnType<typeof setInterval> | null = null;

const updateTime = () => {
  formattedTime.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

onMounted(() => {
  store.initHistory();
  store.ensureIntro();
  updateTime();
  timeInterval = setInterval(updateTime, 60000);
});

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval);
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
