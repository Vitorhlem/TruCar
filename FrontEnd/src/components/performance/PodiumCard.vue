<template>
  <q-card flat bordered class="floating-card" :class="`podium-${rank}`">
    <q-card-section class="text-center">
      <q-avatar :size="avatarSize" class="q-mb-sm shadow-3">
        <img v-if="driver.avatar_url" :src="driver.avatar_url">
        <q-icon v-else name="account_circle" color="grey-5" :size="avatarSize" />
      </q-avatar>
      <div class="text-body1 text-weight-bold ellipsis">{{ driver.full_name }}</div>
      <q-icon :name="medalIcon" :color="medalColor" size="32px" class="q-my-xs" />
      <div class="text-h5 text-weight-bolder">{{ driver.performance_score.toFixed(0) }}</div>
      <div class="text-caption">Score</div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DriverPerformance } from 'src/models/performance-models';

const props = defineProps<{
  driver: DriverPerformance,
  rank: '1' | '2' | '3'
}>();

// A LÓGICA DAS MEDALHAS AGORA VIVE DENTRO DO COMPONENTE
const medalIcon = computed(() => {
  const icons = { '1': 'emoji_events', '2': 'military_tech', '3': 'workspace_premium' };
  return icons[props.rank];
});

const medalColor = computed(() => {
  const colors = { '1': 'yellow-8', '2': 'blue-grey-3', '3': 'brown-5' };
  return colors[props.rank];
});

const avatarSize = computed(() => {
  return props.rank === '1' ? '96px' : '72px';
});
</script>

<style lang="scss" scoped>
.podium-1 {
  transform: scale(1.1);
  border-width: 2px;
  border-color: $warning;
  z-index: 10;
}
.podium-2 {
  border-color: $grey-5;
}
.podium-3 {
  border-color: #A1887F;
}
</style>
