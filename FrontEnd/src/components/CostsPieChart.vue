<template>
  <v-chart class="chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { computed } from 'vue';
import { useQuasar } from 'quasar'; // <-- 1. IMPORTAR O useQuasar
import type { VehicleCost } from 'src/models/cost-models';

use([
  CanvasRenderer,
  PieChart,
  TooltipComponent,
  LegendComponent,
]);

const props = defineProps<{
  costs: VehicleCost[];
}>();

const $q = useQuasar(); // <-- 2. INICIALIZAR O QUASAR

// 3. Criar uma propriedade computada para a cor do texto
const textColor = computed(() => ($q.dark.isActive ? '#FFFFFF' : '#666'));

const option = computed(() => {
  const costsByType = props.costs.reduce((acc: Record<string, number>, cost) => {
    acc[cost.cost_type] = (acc[cost.cost_type] || 0) + cost.amount;
    return acc;
  }, {});

  const chartData = Object.entries(costsByType).map(([name, value]) => ({
    name,
    value: parseFloat(value.toFixed(2)),
  }));

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: R$ {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: chartData.map(d => d.name),
      // 4. Aplicar a cor dinâmica
      textStyle: {
        color: textColor.value,
      },
    },
    series: [
      {
        name: 'Custos por Tipo',
        type: 'pie',
        radius: '70%',
        center: ['65%', '50%'],
        data: chartData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };
});
</script>

<style scoped>
.chart {
  height: 300px;
}
</style>