<template>
  <div class="code-panel">
    <div class="card-header">
      <div>
        <h3>Artifacts</h3>
        <p>Slides markdown and generated components.</p>
      </div>
      <span class="badge">{{ badgeText }}</span>
    </div>
    <div class="card-body">
      <div v-if="!result">
        <p class="composer-hint">Generate a deck to inspect the Slidev output.</p>
      </div>
      <template v-else>
        <div>
          <strong>slides.md</strong>
          <pre>{{ result.slides_md }}</pre>
        </div>
        <div v-if="result.components?.length">
          <strong>Components</strong>
          <div class="code-panel" style="margin-top: 8px;">
            <details v-for="component in result.components" :key="component.name">
              <summary>{{ component.name }}</summary>
              <pre>{{ component.code }}</pre>
            </details>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenerationResult } from '@/stores/session';

const props = defineProps<{
  result: GenerationResult | null;
}>();

const badgeText = computed(() => {
  if (!props.result) return 'Waiting';
  const count = props.result.components?.length || 0;
  return `${count} Components`;
});
</script>
