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
      class="preview-frame"
      :key="previewKey"
      :src="previewUrl"
      title="Slide preview"
      loading="lazy"
      sandbox="allow-scripts allow-same-origin"
    ></iframe>
  </div>
</template>

<script setup lang="ts">
import type { ComponentArtifact } from '@/stores/session';
import { encodeBase64, encodeJsonBase64 } from '@/utils/encoding';

const props = defineProps<{
  slidesMd: string;
  components: ComponentArtifact[];
}>();

const config = useRuntimeConfig();
const previewBase = computed(() => (config.public.previewBase || '/preview').replace(/\/$/, ''));

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
  const codeParam = encodeBase64(props.slidesMd);
  const params = new URLSearchParams({ code: codeParam });
  if (componentsMap.value) {
    params.set('components', encodeJsonBase64(componentsMap.value));
  }
  return `${previewBase.value}/?${params.toString()}`;
});

const previewKey = computed(() => {
  const componentCount = props.components?.length || 0;
  return `${props.slidesMd.length}-${componentCount}`;
});
</script>
