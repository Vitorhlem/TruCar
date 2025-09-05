<template>
  <div class="podium-card text-center" :class="cardClass">
    <q-avatar :size="avatarSize">
      <img :src="driver.avatar_url || defaultAvatar" />
    </q-avatar>
    <div class="text-weight-bold q-mt-sm ellipsis">{{ driver.full_name }}</div>
    <div class="text-weight-bolder" :class="valueClass">
      {{ driver.primary_metric_value.toFixed(1) }}
    </div>
    <div class="text-caption text-grey-7">{{ unit }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DashboardPodiumDriver } from 'src/models/report-models';
import defaultAvatar from '../assets/default-avatar.png';

const props = defineProps<{
  driver: DashboardPodiumDriver;
  rank: number;
  unit: string;
}>();

const cardClass = computed(() => {
  if (props.rank === 1) return 'gold';
  if (props.rank === 2) return 'silver';
  return 'bronze';
});

const avatarSize = computed(() => {
  if (props.rank === 1) return '100px';
  if (props.rank === 2) return '80px';
  return '70px';
});

const valueClass = computed(() => {
  if (props.rank === 1) return 'text-h4';
  if (props.rank === 2) return 'text-h5';
  return 'text-h6';
});
</script>

<style scoped lang="scss">
.podium-card {
  padding: 16px 8px;
  border-radius: 12px;
  border-bottom: 4px solid;
  transition: transform 0.3s ease-in-out;
  background: linear-gradient(145deg, #ffffff, #f0f0f0);
  .body--dark & {
    background: linear-gradient(145deg, $grey-9, $grey-10);
    border-color: lighten($grey-9, 10%);
  }
}
.gold { border-color: #ffd700; order: 2; transform: scale(1.1); z-index: 1;}
.silver { border-color: #c0c0c0; order: 1; }
.bronze { border-color: #cd7f32; order: 3; }
</style>