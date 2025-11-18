<template>
  <q-card class="metric-card full-height column justify-between">
    <q-card-section class="row items-center justify-between no-wrap">
      <div class="text-subtitle2 ellipsis">{{ title }}</div>
      <q-icon :name="icon" :color="color" size="24px" class=" q-pa-xs rounded-borders" />
    </q-card-section>

    <q-card-section class="q-pt-none">
      <div class="row items-baseline">
        <div class="text-h4 text-weight-bold q-mr-xs">
          {{ formattedValue }}
        </div>
        <div class="text-subtitle1">{{ unit }}</div>
      </div>
      
      <div v-if="trend" class="row items-center q-mt-sm text-caption">
        <q-badge :color="trendColor" text-color="white" :label="trend" class="q-mr-xs" />
        <span class="">vs. mês anterior</span>
      </div>
    </q-card-section>
    
    <q-tooltip v-if="tooltip">{{ tooltip }}</q-tooltip>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  title: string;
  value: number;
  unit?: string;
  icon: string;
  color: string;
  trend?: string;
  trendColor?: string;
  tooltip?: string;
  formatter?: (val: number) => string;
}>();

const formattedValue = computed(() => {
  if (props.formatter) {
    return props.formatter(props.value);
  }
  // Formatação padrão se nenhuma função for passada
  return props.value.toLocaleString('pt-BR', { maximumFractionDigits: 2 });
});
</script>

<style scoped lang="scss">
.metric-card {
  border-radius: 12px;
  border: 1px solid #000000;
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  }
}
.body--dark .metric-card {
  background: #1d1d1d;
  border-color: #333;
  color: #fff;
}
</style>