<template>
  <q-card class="dashboard-card full-height">
    <q-card-section>
      <div class="text-h6">Custos por Categoria (Últimos 30 dias)</div>
    </q-card-section>
    <q-separator />
    <q-card-section v-if="!isLoading">
      <v-chart v-if="chartData.length > 0" class="chart" :option="chartOptions" autoresize />
      <div v-else class="text-center text-grey q-pa-lg">
        <q-icon name="pie_chart" size="4em" />
        <p class="q-mt-md">Não há dados de custos para exibir.</p>
      </div>
    </q-card-section>
    <q-skeleton v-else height="250px" square />
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import api from 'src/services/api';
import { type EChartsOption } from 'echarts';
import VChart from 'vue-echarts';

const $q = useQuasar();
const isLoading = ref(true);
const chartData = ref<{ name: string; value: number }[]>([]);

async function fetchData() {
  isLoading.value = true;
  try {

    const response = await api.get<{ name: string; value: number }[]>('/api/dashboard/costs-by-category');
    chartData.value = response.data;
  } catch (error) {
    console.error('Falha ao buscar dados de custos por categoria:', error);

  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchData);

const chartOptions = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: R$ {c} ({d}%)',
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    textStyle: {
      color: $q.dark.isActive ? '#fff' : '#333',
    },
  },
  series: [
    {
      name: 'Custos por Categoria',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: $q.dark.isActive ? '#1d1d1d' : '#fff',
        borderWidth: 2,
      },
      label: {
        show: false,
        position: 'center',
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '20',
          fontWeight: 'bold',
        },
      },
      labelLine: {
        show: false,
      },
      data: chartData.value,
    },
  ],
}));
</script>

<style scoped>
.chart {
  height: 250px;
}
</style>