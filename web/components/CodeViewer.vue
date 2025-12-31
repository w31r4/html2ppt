<template>
  <div class="flex flex-col h-full">
    <div class="flex justify-between items-center mb-4 shrink-0">
      <div>
        <h3 class="font-bold text-lg text-gray-900 dark:text-white">Artifacts</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">Slides markdown and generated components.</p>
      </div>
      <span class="px-2 py-1 rounded-full border border-gray-200 dark:border-gray-700 text-[10px] font-bold text-gray-500">{{ badgeText }}</span>
    </div>
    <div class="bg-[#1e1e1e] rounded-xl flex-1 overflow-hidden flex flex-col font-mono text-sm border border-gray-800 shadow-inner">
      <div class="bg-[#2d2d2d] px-4 py-2 text-xs text-gray-400 border-b border-gray-700 flex gap-4">
        <span class="text-white border-b-2 border-primary pb-1.5 -mb-2 cursor-pointer">slides.md</span>
        <span class="hover:text-gray-200 cursor-pointer" v-if="result?.components?.length">Components</span>
      </div>
      <div class="p-4 overflow-y-auto custom-scrollbar text-gray-300 leading-relaxed h-full">
        <div v-if="!result">
          <p class="text-gray-500 italic">Generate a deck to inspect artifacts.</p>
        </div>
        <template v-else>
          <pre class="whitespace-pre-wrap">{{ result.slides_md }}</pre>
        </template>
      </div>
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
