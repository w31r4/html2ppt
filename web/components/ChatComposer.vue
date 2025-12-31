<template>
  <div>
    <div class="relative rounded-2xl border border-gray-200/70 dark:border-gray-700/70 bg-white/80 dark:bg-[#111317]/80 shadow-[0_12px_30px_rgba(15,23,42,0.08)] backdrop-blur focus-within:ring-2 focus-within:ring-primary/30">
      <textarea
        class="w-full pl-4 pr-14 py-4 bg-transparent border-none rounded-2xl text-sm leading-relaxed focus:ring-0 resize-none min-h-[96px] custom-scrollbar text-gray-800 dark:text-gray-100 placeholder:text-gray-400"
        :value="modelValue"
        :disabled="disabled"
        placeholder="Describe your deck, audience, tone..."
        @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        @keydown="onKeydown"
      ></textarea>
      <div class="absolute bottom-3 right-3 flex items-center gap-2">
        <span class="hidden sm:inline text-[10px] text-gray-400">Cmd/Ctrl + Enter</span>
        <button
          class="p-2.5 bg-primary hover:bg-primary-dark text-white rounded-xl shadow-md transition-colors flex items-center justify-center w-10 h-10 disabled:opacity-50 disabled:cursor-not-allowed"
          type="button"
          :disabled="disabled || !canSend"
          @click="send"
        >
          <span class="material-icons-outlined text-[18px]">send</span>
        </button>
      </div>
    </div>
    <p class="text-[11px] text-gray-400 mt-2 text-center">Tip: add audience, theme, and time limit.</p>
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
