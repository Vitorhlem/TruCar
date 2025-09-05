<template>
  <q-card class="dashboard-card">
    <q-card-section>
      <div class="text-h6">Top 5 Veículos por Custo</div>
    </q-card-section>
    <q-separator />
    <q-card-section>
      <div ref="chartRef" style="width: 100%; height: 300px;"></div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import * as echarts from 'echarts';

// Props para receber os dados
const props = defineProps<{
  data: { labels: string[], values: number[] }
}>();

const $q = useQuasar();
const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

// Computed property para os dados do gráfico, agora corrigida
const chartData = computed(() => {
  // CORRIGIDO: Criamos uma cópia com `[... ]` antes de reverter para evitar side-effects
  const reversedLabels = [...props.data.labels].reverse();
  const reversedValues = [...props.data.values].reverse();
  return { labels: reversedLabels, values: reversedValues };
});

const chartOptions = computed<echarts.EChartsOption>(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    boundaryGap: [0, 0.01],
    axisLabel: { color: $q.dark.isActive ? '#fff' : '#333' }
  },
  yAxis: {
    type: 'category',
    data: chartData.value.labels, // Usa os dados já revertidos
    axisLabel: { color: $q.dark.isActive ? '#fff' : '#333' },
  },
  series: [{
    name: 'Custo Total',
    type: 'bar',
    data: chartData.value.values, // Usa os dados já revertidos
    itemStyle: {
      borderRadius: 5,
      color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
        { offset: 0, color: '#83bff6' },
        { offset: 1, color: '#188df0' },
      ]),
    },
  }],
}));

function initChart() {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    chartInstance.setOption(chartOptions.value);
  }
}

// Observa mudanças nas opções (como troca de tema dark/light) e atualiza o gráfico
watch(chartOptions, () => {
  if (chartInstance) {
    chartInstance.setOption(chartOptions.value);
  }
});

onMounted(() => {
  initChart();
});
</script>
