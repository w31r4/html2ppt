<template>
  <div>
    <div class="relative">
      <textarea
        class="w-full pl-4 pr-12 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-primary focus:border-transparent resize-none h-24 custom-scrollbar dark:text-white"
        :value="modelValue"
        :disabled="disabled"
        placeholder="Describe your deck, audience, tone..."
        @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        @keydown="onKeydown"
      ></textarea>
      <button
        class="absolute bottom-3 right-3 p-2 bg-primary hover:bg-primary-dark text-white rounded-lg shadow-md transition-colors flex items-center justify-center w-8 h-8 disabled:opacity-50 disabled:cursor-not-allowed"
        type="button"
        :disabled="disabled || !canSend"
        @click="send"
      >
        <span class="material-icons-outlined text-sm">send</span>
      </button>
    </div>
    <p class="text-[10px] text-gray-400 mt-2 text-center">Tip: add audience, theme, and time limit.</p>
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
