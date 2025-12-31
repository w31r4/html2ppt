<template>
  <div>
    <div v-if="!slidesMd" class="preview-placeholder">
      <div>
        <p><strong>No preview yet.</strong></p>
        <p>Confirm the outline to generate slides and see the live preview.</p>
      </div>
    </div>
    <iframe
      v-else
      ref="iframeRef"
      class="preview-frame"
      :key="previewKey"
      :src="previewUrl"
      title="Slide preview"
      loading="lazy"
      sandbox="allow-scripts allow-same-origin"
      @load="handleFrameLoad"
    ></iframe>
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
