<template>
  <div ref="chartRef" style="width: 100%; height: 100%;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, type PropType } from 'vue';
import * as echarts from 'echarts';




interface ChartCost {
  cost_type: string;
  amount: number;
}

const props = defineProps({



  costs: {
    type: Array as PropType<ChartCost[]>,
    required: true,
  },
});



const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const setupChart = () => {
  if (!chartInstance) return;

  const dataForChart = props.costs.map(cost => ({
    name: cost.cost_type,
    value: cost.amount,
  }));

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: dataForChart.map(d => d.name)
    },
    series: [
      {
        name: 'Custos por Categoria',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: dataForChart,
      },
    ],
  };

  chartInstance.setOption(option);
};

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    setupChart();
  }
});

watch(() => props.costs, () => {
  setupChart();
}, { deep: true });
</script>