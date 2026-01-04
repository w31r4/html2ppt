<template>
  <div class="flex flex-col h-full">
    <div class="flex justify-between items-center mb-4 shrink-0">
      <div>
        <h3 class="font-bold text-lg text-gray-900 dark:text-white">Artifacts</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">Slides markdown and generated components.</p>
      </div>
      <span class="px-2 py-1 rounded-full border border-gray-200 dark:border-gray-700 text-[10px] font-bold text-gray-500">{{ badgeText }}</span>
    </div>
    <div class="bg-[#15171c] rounded-2xl flex-1 overflow-hidden flex flex-col font-mono text-sm border border-[#2b2f36] shadow-inner">
      <div class="bg-[#1f242b] px-4 py-2 text-xs text-gray-400 border-b border-[#2b2f36] flex gap-4" role="tablist">
        <button
          role="tab"
          :aria-selected="activeTab === 'slides'"
          class="pb-1.5 -mb-2 cursor-pointer transition-colors"
          :class="activeTab === 'slides' ? 'text-white border-b-2 border-primary' : 'hover:text-gray-200'"
          @click="activeTab = 'slides'"
        >
          slides.md
        </button>
        <button
          v-if="result?.components?.length"
          role="tab"
          :aria-selected="activeTab === 'components'"
          class="pb-1.5 -mb-2 cursor-pointer transition-colors"
          :class="activeTab === 'components' ? 'text-white border-b-2 border-primary' : 'hover:text-gray-200'"
          @click="activeTab = 'components'"
        >
          Components ({{ result.components.length }})
        </button>
      </div>
      <div class="p-4 overflow-y-auto custom-scrollbar text-gray-300 leading-6 h-full" role="tabpanel">
        <div v-if="!result">
          <p class="text-gray-500 italic">Generate a deck to inspect artifacts.</p>
        </div>
        <template v-else>
          <!-- Slides Tab -->
          <div v-show="activeTab === 'slides'">
            <div class="flex justify-end mb-2">
              <button
                class="text-xs text-gray-400 hover:text-white px-2 py-1 rounded bg-[#2b2f36] hover:bg-[#3b3f46] transition-colors flex items-center gap-1"
                @click="copyToClipboard(result.slides_md)"
                :title="copied === 'slides' ? 'Copied!' : 'Copy to clipboard'"
              >
                <span class="material-symbols-rounded text-sm">{{ copied === 'slides' ? 'check' : 'content_copy' }}</span>
                {{ copied === 'slides' ? 'Copied!' : 'Copy' }}
              </button>
            </div>
            <pre class="whitespace-pre-wrap">{{ result.slides_md }}</pre>
          </div>
          <!-- Components Tab -->
          <div v-show="activeTab === 'components'" v-if="result?.components?.length">
            <div v-for="(component, index) in result.components" :key="index" class="mb-6">
              <div class="flex justify-between items-center mb-2">
                <span class="text-primary font-semibold text-xs">{{ component.name || `Component ${index + 1}` }}</span>
                <button
                  class="text-xs text-gray-400 hover:text-white px-2 py-1 rounded bg-[#2b2f36] hover:bg-[#3b3f46] transition-colors flex items-center gap-1"
                  @click="copyToClipboard(component.code, index)"
                  :title="copied === index ? 'Copied!' : 'Copy to clipboard'"
                >
                  <span class="material-symbols-rounded text-sm">{{ copied === index ? 'check' : 'content_copy' }}</span>
                  {{ copied === index ? 'Copied!' : 'Copy' }}
                </button>
              </div>
              <pre class="whitespace-pre-wrap bg-[#1a1d24] p-3 rounded-lg border border-[#2b2f36]">{{ component.code }}</pre>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import type { GenerationResult } from '@/stores/session';

const props = defineProps<{
  result: GenerationResult | null;
}>();

const activeTab = ref<'slides' | 'components'>('slides');
const copied = ref<'slides' | number | null>(null);

const badgeText = computed(() => {
  if (!props.result) return 'Waiting';
  const count = props.result.components?.length || 0;
  return `${count} Components`;
});

// Reset to slides tab when result changes (new generation)
watch(() => props.result, () => {
  activeTab.value = 'slides';
});

const copyToClipboard = async (text: string, index?: number) => {
  try {
    await navigator.clipboard.writeText(text);
    copied.value = index !== undefined ? index : 'slides';
    setTimeout(() => {
      copied.value = null;
    }, 2000);
  } catch {
    console.error('Failed to copy to clipboard');
  }
};
</script>
