<template>
  <q-page padding>
    <div v-if="userStore.isLoading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="3em" />
    </div>
    <div v-else-if="userStore.selectedUserStats" class="q-gutter-y-lg">
      <div class="row items-center q-gutter-md">
        <q-btn flat round dense icon="arrow_back" @click="router.back()" />
        <h1 class="text-h5 text-weight-bold q-my-none">Painel de Performance</h1>
      </div>
      
      <!-- SCORECARD E KPIs -->
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-4">
          <q-card flat bordered class="full-height text-center floating-card">
            <q-card-section>
              <div class="text-overline text-grey-8">Score de Eficiência</div>
              <q-circular-progress :value="efficiencyScore" size="150px" :thickness="0.22" color="primary" track-color="grey-3" class="q-ma-md" show-value>
                <span class="text-h4 text-weight-bold">{{ efficiencyScore.toFixed(0) }}</span>
              </q-circular-progress>
              <div class="text-caption">Baseado na média da frota</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-8 q-gutter-y-md">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6"><q-card flat bordered class="  floating-card"><q-card-section><div class="text-grey-8">Eficiência Média</div><div class="text-h5 text-weight-bold">{{ userStore.selectedUserStats.avg_km_per_liter.toFixed(2) }} <span class="text-body2">KM/L</span></div></q-card-section></q-card></div>
            <div class="col-12 col-sm-6"><q-card flat bordered class="floating-card"><q-card-section><div class="text-grey-8">Custo Médio por KM</div><div class="text-h5 text-weight-bold">R$ {{ userStore.selectedUserStats.avg_cost_per_km.toFixed(2) }}</div></q-card-section></q-card></div>
            <div class="col-12 col-sm-6"><q-card flat bordered class="floating-card"><q-card-section><div class="text-grey-8">Viagens Realizadas</div><div class="text-h5 text-weight-bold">{{ userStore.selectedUserStats.total_journeys }}</div></q-card-section></q-card></div>
            <div class="col-12 col-sm-6"><q-card flat bordered class="floating-card"><q-card-section><div class="text-grey-8">Chamados Abertos</div><div class="text-h5 text-weight-bold">{{ userStore.selectedUserStats.maintenance_requests_count }}</div></q-card-section></q-card></div>
          </div>
        </div>
      </div>

      <!-- GRÁFICOS COMPARATIVOS -->
      <div class="row q-col-gutter-lg">
        <div class="col-12 col-md-6">
          <q-card flat bordered class="floating-card">
            <q-card-section>
              <div class="text-h6">Eficiência de Combustível</div>
              <ApexChart type="bar" height="250" :options="efficiencyChart.options" :series="efficiencyChart.series" />
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
           <q-card flat bordered class="floating-card">
            <q-card-section>
              <div class="text-h6">Quilometragem por Veículo</div>
              <ApexChart type="bar" height="250" :options="kmByVehicleChart.options" :series="kmByVehicleChart.series" />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from 'stores/user-store';
import type { JourneysByVehicle } from 'src/models/user-models';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const efficiencyScore = computed(() => {
  const stats = userStore.selectedUserStats;
  if (!stats || !stats.fleet_avg_km_per_liter) return 0;
  const score = (stats.avg_km_per_liter / stats.fleet_avg_km_per_liter) * 100;
  return Math.min(score, 120);
});

const efficiencyChart = computed(() => {
    const stats = userStore.selectedUserStats;
    const series = [{ data: [stats?.avg_km_per_liter.toFixed(2) || 0, stats?.fleet_avg_km_per_liter.toFixed(2) || 0] }];
    const options = {
        chart: { toolbar: { show: false } },
        xaxis: { categories: ['Eficiência do Motorista', 'Média da Frota'] },
        yaxis: { title: { text: 'KM/L' } },
        plotOptions: { bar: { distributed: true, borderRadius: 4 } },
        legend: { show: false }
    };
    return { series, options };
});

const kmByVehicleChart = computed(() => {
    const data = userStore.selectedUserStats?.journeys_by_vehicle || [];
    const series = [{ name: 'KM Rodados', data: data.map((item: JourneysByVehicle) => item.km_driven_in_vehicle) }];
    const options = {
      chart: { toolbar: { show: false } },
      xaxis: { categories: data.map((item: JourneysByVehicle) => item.vehicle_info) },
      plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
      dataLabels: { enabled: true, formatter: (val: number) => `${val.toFixed(0)} km` },
    };
    return { series, options };
});

onMounted(() => {
  const userId = Number(route.params.id);
  if (userId) {
    void userStore.fetchUserStats(userId);
  }
});
</script>