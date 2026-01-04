<template>
  <div class="flex-1 bg-black relative flex items-center justify-center overflow-hidden w-full h-full">
    <!-- Empty State -->
    <div v-if="!slidesMd" class="text-center text-gray-400 flex flex-col items-center gap-4 p-6">
      <div class="w-16 h-16 rounded-2xl bg-gray-800 flex items-center justify-center">
        <span class="material-symbols-rounded text-3xl text-gray-500">slideshow</span>
      </div>
      <div>
        <p class="font-semibold text-gray-300 mb-1">No preview available</p>
        <p class="text-sm text-gray-500">Describe your presentation and confirm the outline to generate slides.</p>
      </div>
    </div>

    <!-- Preview Content -->
    <div v-else class="w-full h-full relative group">
      <!-- Loading Overlay -->
      <div
        v-if="!frameReady"
        class="absolute inset-0 bg-gray-900 flex items-center justify-center z-10"
      >
        <div class="flex flex-col items-center gap-3">
          <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm text-gray-400">Loading preview...</span>
        </div>
      </div>

      <iframe
        ref="iframeRef"
        class="w-full h-full border-none bg-[#0f1110]"
        :key="previewKey"
        :src="previewUrl"
        title="Slide preview"
        loading="lazy"
        sandbox="allow-scripts allow-same-origin"
        @load="handleFrameLoad"
        @error="handleFrameError"
      ></iframe>

      <!-- Bottom Control Bar -->
      <div class="absolute bottom-0 left-0 right-0 h-12 bg-black/80 backdrop-blur text-white flex items-center justify-between px-4 text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span class="text-gray-400 flex items-center gap-2">
          <span class="material-symbols-rounded text-lg" :class="frameReady ? 'text-green-400' : 'text-gray-500'">{{ frameReady ? 'check_circle' : 'pending' }}</span>
          {{ frameReady ? 'Preview ready' : 'Loading...' }}
        </span>
        <button
          class="p-2 hover:text-primary hover:bg-white/10 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          @click="openFullscreen"
          aria-label="Open fullscreen"
          title="Fullscreen"
        >
          <span class="material-symbols-rounded text-lg">fullscreen</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import type { ComponentArtifact } from '@/stores/session';

const props = defineProps<{
  slidesMd: string;
  components: ComponentArtifact[];
}>();

const config = useRuntimeConfig();
const previewBase = computed(() => {
  const raw = (config.public.previewBase || '/preview').replace(/\/$/, '');
  if (
    import.meta.client &&
    raw === '/preview' &&
    window.location.hostname === 'localhost' &&
    import.meta.dev
  ) {
    return 'http://localhost:5173';
  }
  return raw;
});

const previewOrigin = computed(() => {
  if (!import.meta.client) return '';
  const raw = previewBase.value;
  if (raw.startsWith('http')) {
    try {
      return new URL(raw).origin;
    } catch {
      return window.location.origin;
    }
  }
  return window.location.origin;
});

const componentsMap = computed(() => {
  if (!props.components?.length) return null;
  return props.components.reduce<Record<string, string>>((acc, item) => {
    if (item.name && item.code) {
      acc[item.name] = item.code;
    }
    return acc;
  }, {});
});

const previewUrl = computed(() => {
  if (!props.slidesMd) return '';
  return `${previewBase.value}/?mode=post`;
});

const previewKey = computed(() => {
  const componentCount = props.components?.length || 0;
  return `${props.slidesMd.length}-${componentCount}`;
});

const iframeRef = ref<HTMLIFrameElement | null>(null);
const frameReady = ref(false);

const sendPreviewMessage = () => {
  if (!frameReady.value || !props.slidesMd) return;
  const target = iframeRef.value?.contentWindow;
  if (!target) return;

  try {
    target.postMessage(
      {
        type: 'preview-code',
        code: props.slidesMd,
        components: componentsMap.value ?? undefined
      },
      previewOrigin.value || '*'
    );
  } catch (error) {
    console.error('Failed to send preview message:', error);
  }
};

const handleFrameLoad = () => {
  frameReady.value = true;
  sendPreviewMessage();
};

const handleFrameError = () => {
  console.error('Preview iframe failed to load');
  frameReady.value = false;
};

const openFullscreen = () => {
  if (iframeRef.value?.requestFullscreen) {
    iframeRef.value.requestFullscreen();
  }
};

watch(
  [() => props.slidesMd, componentsMap],
  () => {
    if (!props.slidesMd) {
      frameReady.value = false;
      return;
    }
    sendPreviewMessage();
  },
  { deep: true }
);
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
