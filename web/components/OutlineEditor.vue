<template>
  <div class="outline-editor">
    <div class="card-header">
      <div>
        <h3>Outline</h3>
        <p>Review structure before generating slides.</p>
      </div>
      <span class="badge">{{ badgeLabel }}</span>
    </div>
    <div class="card-body">
      <textarea v-model="localOutline" :disabled="isLocked"></textarea>
      <div class="composer-actions" style="margin-top: 12px;">
        <button class="btn-ghost" type="button" :disabled="!canSave" @click="save">
          Save outline
        </button>
        <button class="btn-primary" type="button" :disabled="!canConfirm" @click="confirm">
          Confirm + Generate
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
