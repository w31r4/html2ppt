<template>
  <div class="timeline">
    <div class="progress-row">
      <span>Progress</span>
      <div class="progress-bar"><span :style="{ width: progressPercent }"></span></div>
      <span>{{ Math.round(progress * 100) }}%</span>
    </div>
    <div
      v-for="(step, index) in steps"
      :key="step.id"
      class="timeline-item"
      :class="stepState(step.id)"
      :style="{ animationDelay: `${index * 80}ms` }"
    >
      <span class="timeline-dot"></span>
      <div class="timeline-copy">
        <h4>{{ step.label }}</h4>
        <p>{{ step.description }}</p>
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
</script>
