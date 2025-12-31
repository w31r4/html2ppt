<template>
  <div class="flex flex-col h-full">
    <div class="flex justify-between items-center mb-4 shrink-0">
      <div>
        <h3 class="font-bold text-lg text-gray-900 dark:text-white">Outline</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">Review structure before generating.</p>
      </div>
      <span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px] font-bold text-gray-500 uppercase tracking-wider border border-gray-200 dark:border-gray-700">{{ badgeLabel }}</span>
    </div>
    <div class="bg-white/70 dark:bg-[#17181c] rounded-2xl p-4 flex-1 overflow-y-auto border border-gray-100/80 dark:border-gray-800 font-sans text-sm leading-relaxed custom-scrollbar relative group">
      <textarea
        v-model="localOutline"
        :disabled="isLocked"
        class="w-full h-full bg-transparent border-none resize-none focus:ring-0 p-0 text-gray-700 dark:text-gray-200"
      ></textarea>
      
      <div class="absolute bottom-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button class="btn-ghost text-xs py-1.5 px-3" type="button" :disabled="!canSave" @click="save">
          Save
        </button>
        <button class="btn-primary text-xs py-1.5 px-3" type="button" :disabled="!canConfirm" @click="confirm">
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
