<template>
  <div class="px-6 py-5 border-b border-border-light dark:border-border-dark bg-gray-50/50 dark:bg-gray-800/20">
    <div class="flex justify-between items-center mb-3">
      <h3 class="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">Progress</h3>
      <span class="text-xs font-bold text-primary">{{ Math.round(progress * 100) }}%</span>
    </div>
    <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mb-4 overflow-hidden">
      <div class="bg-primary h-1.5 rounded-full transition-all duration-300" :style="{ width: progressPercent }"></div>
    </div>
    <div class="space-y-3">
      <div v-for="step in steps" :key="step.id" class="flex items-start gap-3" :class="{ 'opacity-50': stepState(step.id) === 'pending' }">
        <div 
          class="w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 transition-colors"
          :class="getIconClass(step.id)"
        >
          <span class="material-icons-outlined text-[12px] text-white">{{ getIcon(step.id) }}</span>
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ step.label }}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-1">{{ step.description }}</p>
        </div>
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

const stepState = (id: string) => {
  if (props.status === 'error') {
    return 'error';
  }
  const order = steps.map((step) => step.id);
  const currentIndex = order.indexOf(currentStep.value);
  const index = order.indexOf(id);
  if (index < currentIndex) return 'complete';
  if (index === currentIndex) return 'active';
  return 'pending';
};

const getIconClass = (id: string) => {
  const state = stepState(id);
  if (state === 'complete') return 'bg-primary';
  if (state === 'active') return 'bg-primary shadow-sm shadow-primary/30';
  return 'bg-gray-300 dark:bg-gray-600';
};

const getIcon = (id: string) => {
  const state = stepState(id);
  if (state === 'complete') return 'check';
  if (state === 'active') return 'edit';
  return 'circle';
};
</script>