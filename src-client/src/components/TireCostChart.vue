<template>
  <div>
    <apexchart
      type="bar"
      height="250"
      :options="chartOptions"
      :series="chartSeries"
    ></apexchart>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';


interface Cost {
  date: Date;
  amount: number;
}


interface ChartSeriesItem {
  name: string;
  data: number[];
}

const props = defineProps({
  costs: {
    type: Array as PropType<Cost[]>,
    required: true,
  }
});

const monthlyCosts = computed(() => {
  const result: { [key: string]: number } = {};

  const sortedCosts = [...props.costs].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  sortedCosts.forEach(cost => {

    const costDate = new Date(cost.date);
    const month = format(costDate, 'MMM/yy', { locale: ptBR });
    if (!result[month]) {
      result[month] = 0;
    }
    result[month] += cost.amount;
  });
  return result;
});


const chartSeries = computed<ChartSeriesItem[]>(() => {
  return [{
    name: 'Custos Mensais',
    data: Object.values(monthlyCosts.value),
  }];
});
const chartOptions = computed(() => {
  return {
    chart: {
      type: 'bar',
      height: 250,
      toolbar: { show: false },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '50%',
        borderRadius: 4,
      },
    },
    dataLabels: { enabled: false },
    xaxis: {
      categories: Object.keys(monthlyCosts.value),
    },
    yaxis: {
      title: { text: 'Reais (R$)' }
    },
    tooltip: {
      y: {
        formatter: (val: number) => `R$ ${val.toLocaleString('pt-BR')}`
      }
    },
    fill: { opacity: 1 },
  };
});
</script>