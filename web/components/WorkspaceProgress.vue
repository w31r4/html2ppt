<template>
  <div class="px-6 py-3 border-b border-border-light dark:border-border-dark bg-white/70 dark:bg-[#15161a]/70 backdrop-blur">
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 shrink-0">
        <h3 class="text-[11px] font-semibold uppercase tracking-[0.2em] text-gray-400 dark:text-gray-500">Progress</h3>
        <span class="text-xs font-semibold text-gray-700 dark:text-gray-200">{{ currentStepLabel }}</span>
      </div>
      <div class="flex-1 flex items-center gap-3">
        <div class="w-full bg-gray-200/80 dark:bg-gray-700/60 rounded-full h-1.5 overflow-hidden">
          <div
            class="h-1.5 rounded-full bg-gradient-to-r from-primary to-primary-dark transition-all duration-300"
            :style="{ width: progressPercent }"
          ></div>
        </div>
        <span class="text-xs font-semibold text-primary tabular-nums">{{ Math.round(progress * 100) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { WorkflowStage, SessionStatus } from '@/stores/session';

const props = defineProps<{
  stage: WorkflowStage;
  status: SessionStatus;
  progress: number;
}>();

const steps = [
  { id: 'outline', label: 'Outline', description: 'Shape the narrative structure.' },
  { id: 'design', label: 'Design System', description: 'Set tone, colors, and typography.' },
  { id: 'components', label: 'Components', description: 'Generate Vue SFC slides.' },
  { id: 'assemble', label: 'Assemble', description: 'Compose Slidev markdown.' },
  { id: 'ready', label: 'Ready', description: 'Export or refine the deck.' }
];

const progressPercent = computed(() => `${Math.min(100, Math.max(0, props.progress * 100))}%`);

const currentStep = computed(() => {
  const stage = props.stage;
  if (stage === 'error') return 'error';
  if (stage === 'completed') return 'ready';
  if (stage === 'slidev_assembling') return 'assemble';
  if (stage === 'pagination_review') return 'assemble';
  if (stage === 'vue_completed') return 'assemble';
  if (stage === 'vue_generating') return 'components';
  if (stage === 'outline_confirmed') return 'design';
  if (stage === 'outline_generated') return 'outline';
  return 'outline';
});

const currentStepLabel = computed(() => {
  if (props.status === 'error' || props.stage === 'error') return 'Error';
  const match = steps.find((step) => step.id === currentStep.value);
  return match?.label ?? 'Outline';
});
</script>
