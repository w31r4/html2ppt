<template>
  <div class="flex-1 bg-black relative flex items-center justify-center overflow-hidden w-full h-full">
    <div v-if="!slidesMd" class="text-center text-gray-500">
      <p class="font-bold mb-1">No preview available</p>
      <p class="text-xs">Confirm outline to generate slides.</p>
    </div>
    <div v-else class="w-full h-full relative group">
      <iframe
        ref="iframeRef"
        class="w-full h-full border-none bg-[#0f1110]"
        :key="previewKey"
        :src="previewUrl"
        title="Slide preview"
        loading="lazy"
        sandbox="allow-scripts allow-same-origin"
        @load="handleFrameLoad"
      ></iframe>
      
      <div class="absolute bottom-0 left-0 right-0 h-12 bg-black/80 backdrop-blur text-white flex items-center justify-between px-4 text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span class="text-gray-400" v-if="!frameReady">Loading preview...</span>
        <span class="text-gray-400" v-else>Ready</span>
        <div class="flex gap-2">
          <button class="p-1 hover:text-primary"><span class="material-icons-outlined text-sm">chevron_left</span></button>
          <span class="font-mono text-xs pt-0.5">-- / --</span>
          <button class="p-1 hover:text-primary"><span class="material-icons-outlined text-sm">chevron_right</span></button>
        </div>
        <button class="p-1 hover:text-primary"><span class="material-icons-outlined text-sm">fullscreen</span></button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
  target.postMessage(
    {
      type: 'preview-code',
      code: props.slidesMd,
      components: componentsMap.value ?? undefined
    },
    previewOrigin.value || '*'
  );
};

const handleFrameLoad = () => {
  frameReady.value = true;
  sendPreviewMessage();
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
