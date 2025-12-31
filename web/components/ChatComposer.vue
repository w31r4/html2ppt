<template>
  <div class="composer">
    <textarea
      :value="modelValue"
      :disabled="disabled"
      placeholder="Describe your deck, audience, tone, and must-have visuals..."
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      @keydown="onKeydown"
    ></textarea>
    <div class="composer-actions">
      <span class="composer-hint">Tip: add audience, theme, and time limit.</span>
      <button class="btn-primary" type="button" :disabled="disabled || !canSend" @click="send">
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'send'): void;
}>();

const canSend = computed(() => props.modelValue.trim().length > 0);

const send = () => {
  if (!canSend.value || props.disabled) return;
  emit('send');
};

const onKeydown = (event: KeyboardEvent) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault();
    send();
  }
};
</script>
