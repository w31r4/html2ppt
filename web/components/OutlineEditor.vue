<template>
  <div class="flex flex-col h-full">
    <div class="flex justify-between items-center mb-4 shrink-0">
      <div>
        <h3 class="font-bold text-lg text-gray-900 dark:text-white">Outline</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">Review structure before generating.</p>
      </div>
      <span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px] font-bold text-gray-500 uppercase tracking-wider border border-gray-200 dark:border-gray-700">{{ badgeLabel }}</span>
    </div>
    <div class="bg-white/70 dark:bg-[#17181c] rounded-2xl flex-1 overflow-hidden border border-gray-100/80 dark:border-gray-800 font-sans text-sm leading-relaxed flex flex-col">
      <textarea
        v-model="localOutline"
        :disabled="isLocked"
        class="w-full flex-1 bg-transparent border-none resize-none focus:ring-0 p-4 text-gray-700 dark:text-gray-200 custom-scrollbar"
        placeholder="Outline will appear here after you describe your presentation..."
      ></textarea>

      <!-- Action buttons - always visible at bottom -->
      <div class="flex gap-2 justify-end p-3 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/30 shrink-0">
        <button
          class="btn btn-ghost text-xs py-1.5 px-3"
          type="button"
          :disabled="!canSave"
          @click="save"
        >
          <span class="material-symbols-rounded text-sm mr-1">save</span>
          Save Draft
        </button>
        <button
          class="btn btn-primary text-xs py-1.5 px-3"
          type="button"
          :disabled="!canConfirm"
          @click="confirm"
        >
          <span class="material-symbols-rounded text-sm mr-1">check_circle</span>
          Confirm & Generate
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import type { SessionStatus } from '@/stores/session';

const props = defineProps<{
  outline: string;
  status: SessionStatus;
}>();

const emit = defineEmits<{
  (e: 'save', value: string): void;
  (e: 'confirm'): void;
}>();

const localOutline = ref(props.outline);

watch(
  () => props.outline,
  (value) => {
    localOutline.value = value;
  }
);

const canSave = computed(() => !isLocked.value && localOutline.value.trim().length > 0);
const canConfirm = computed(() => ['draft', 'outline_ready'].includes(props.status));
const isLocked = computed(() => !['draft', 'outline_ready'].includes(props.status));
const badgeLabel = computed(() => {
  const labels: Record<string, string> = {
    outline_ready: 'Outline Ready',
    draft: 'Draft',
    confirmed: 'Confirmed',
    generating: 'Generating',
    assembling: 'Assembling',
    completed: 'Locked',
    error: 'Error'
  };
  return labels[props.status] || 'Draft';
});

const save = () => {
  if (!canSave.value) return;
  emit('save', localOutline.value);
};

const confirm = () => {
  emit('confirm');
};
</script>
