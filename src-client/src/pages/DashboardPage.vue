<template>
  <q-page padding class="dashboard-page">
    <div class="page-content-container">

      <template v-if="isManager">
        <div class="flex items-center justify-between q-mb-md">
          <div>
            <h1 class="text-h4 text-weight-bold q-my-none">Dashboard de Gestão</h1>
            <div class="text-subtitle1 text-grey-7">Bem-vindo, {{ authStore.user?.full_name }}.</div>
          </div>
          <div class="flex items-center q-gutter-md">
            <q-select
              v-model="selectedPeriod"
              :options="periodOptions"
              label="Período"
              dense outlined style="min-width: 200px;"
              class="gt-xs"
            />
            <q-btn-dropdown
              color="primary" icon="add" label="Ações Rápidas"
              unelevated class="gt-xs"
            >
              <q-list dense>
                <q-item clickable v-close-popup @click="router.push('/vehicles')"><q-item-section avatar><q-icon name="local_shipping" /></q-item-section><q-item-section>Adicionar Veículo</q-item-section></q-item>
                <q-item clickable v-close-popup @click="router.push('/users')"><q-item-section avatar><q-icon name="person_add" /></q-item-section><q-item-section>Adicionar Motorista</q-item-section></q-item>
                <q-item clickable v-close-popup @click="router.push('/journeys')"><q-item-section avatar><q-icon name="route" /></q-item-section><q-item-section>Iniciar Jornada</q-item-section></q-item>
              </q-list>
            </q-btn-dropdown>
          </div>
        </div>

        <div class="row q-col-gutter-lg q-mb-lg">
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard
  label="Total de Veículos"
  :value="kpis?.total_vehicles ?? 0"
  :limit="authStore.isDemo ? (authStore.user?.organization?.vehicle_limit ?? -1) : -1"
  icon="local_shipping"
  color="primary"
  :loading="dashboardStore.isLoading"
  to="/vehicles"
/>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard label="Disponíveis" :value="kpis?.available_vehicles ?? 0" icon="check_circle_outline" color="positive" :loading="dashboardStore.isLoading" to="/vehicles?status=available"/>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard :label="journeyNounInProgress" :value="kpis?.in_use_vehicles ?? 0" icon="alt_route" color="warning" :loading="dashboardStore.isLoading" to="/vehicles?status=in_use"/>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard
          label="Em Manutenção"
          :value="kpis?.maintenance_vehicles ?? 0"
          icon="build"
          color="negative"
          :loading="dashboardStore.isLoading"
          to="/maintenance"
        />
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard label="Custo por KM" :value="`R$ ${efficiencyKpis?.cost_per_km.toFixed(2) ?? '0.00'}`" icon="paid" color="deep-purple" :loading="dashboardStore.isLoading"/>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard label="Gasto Combustível" :value="`R$ ${fuelCostTotal.toFixed(2)}`" icon="local_gas_station" color="orange-9" :loading="dashboardStore.isLoading"/>
    </div>
    <div class="col-12 col-sm-6 col-lg-3">
        <StatCard label="Taxa de Utilização" :value="`${efficiencyKpis?.utilization_rate.toFixed(1) ?? '0.0'}%`" icon="pie_chart" color="teal" :loading="dashboardStore.isLoading"/>
    </div>
</div>
        <div class="row q-col-gutter-lg" v-if="dashboardStore.managerDashboard">
          <div class="col-12 col-lg-8">
            <div class="column q-gutter-y-lg">
              <q-card class="dashboard-card">
                <q-card-section>
                  <div class="text-h6">Operação em Tempo Real</div>
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-none">
                  <div style="height: 450px; width: 100%;">
                    <l-map ref="mapRef" v-model:zoom="zoom" :center="center" :use-global-leaflet="false">
                      <l-tile-layer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        layer-type="base"
                        name="OpenStreetMap"
                        attribution="&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>"
                      ></l-tile-layer>
                      <l-marker
                        v-for="vehicle in dashboardStore.vehiclePositions"
                        :key="vehicle.id"
                        :lat-lng="[vehicle.latitude, vehicle.longitude]"
                      >
                        <l-icon :icon-url="getVehicleIcon(vehicle.status)" :icon-size="[38, 48]" />
                        <l-popup>
                          <strong>{{ vehicle.license_plate || vehicle.identifier }}</strong><br>
                          Status: {{ vehicle.status }}
                        </l-popup>
                      </l-marker>
                    </l-map>
                  </div>
                </q-card-section>
              </q-card>

              <div></div>
              <div class="row q-col-gutter-lg">
                <div class="col-12 col-md-6">
                  <PremiumWidget title="Análise de Custos" :icon="`insights`" :description="`Análise de custos do período de ${selectedPeriod.label}`">
                    <ApexChart type="bar" height="280" :options="costAnalysisChart.options" :series="costAnalysisChart.series" />
                  </PremiumWidget>
                </div>
                <div class="col-12 col-md-6">
                  <PremiumWidget title="Análise de Atividade" :icon="`show_chart`" :description="`Análise de atividade do período de ${selectedPeriod.label}`">
                    <ApexChart type="area" height="280" :options="lineChart.options" :series="lineChart.series" />
                  </PremiumWidget>
                </div>
              </div>
            </div>
          </div>

          <div class="col-12 col-lg-4">
              <div class="column q-gutter-y-lg">
              <q-card class="dashboard-card">
                <q-card-section>
                  <div class="text-h6">Alertas Recentes</div>
                </q-card-section>
                <q-list separator>
                  <q-item v-for="alert in recentAlerts" :key="alert.id">
                    <q-item-section avatar>
                      <q-icon :name="alert.icon" :color="alert.color" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ alert.title }}</q-item-label>
                      <q-item-label caption>{{ alert.subtitle }}</q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label caption>{{ alert.time }}</q-item-label>
                    </q-item-section>
                  </q-item>
                    <q-item v-if="!recentAlerts?.length">
                    <q-item-section class="text-center text-grey-6">Nenhum alerta recente.</q-item-section>
                  </q-item>
                </q-list>
              </q-card>

              <q-card class="dashboard-card">
                <q-card-section>
                  <div class="text-h6">Próximas Manutenções</div>
                </q-card-section>
                <q-list separator>
                    <q-item v-for="maint in upcomingMaintenances" :key="maint.vehicle_info">
                    <q-item-section>
                      <q-item-label>{{ maint.vehicle_info }}</q-item-label>
                      <q-item-label caption>Vence em {{ maint.due_date ? new Date(maint.due_date).toLocaleDateString() : `${maint.due_km} km` }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn dense flat round icon="event" color="primary" @click="scheduleMaintenance(maint.vehicle_info)">
                        <q-tooltip>Agendar</q-tooltip>
                      </q-btn>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="!upcomingMaintenances?.length">
                    <q-item-section class="text-center text-grey-6">Nenhuma manutenção próxima.</q-item-section>
                  </q-item>
                </q-list>
              </q-card>
              
              <q-card class="dashboard-card" v-if="activeGoal">
                  <q-card-section>
                    <div class="text-h6">Meta do Mês: {{ activeGoal.title }}</div>
                    <div class="text-subtitle2 text-grey-7">Progresso: {{ activeGoal.current_value.toFixed(2) }} / {{ activeGoal.target_value }} ({{ activeGoal.unit }})</div>
                  </q-card-section>
                  <q-card-section>
                    <q-linear-progress size="25px" :value="goalProgress" color="positive" class="q-mt-sm">
                      <div class="absolute-full flex flex-center">
                        <q-badge color="white" text-color="black" :label="`${(goalProgress * 100).toFixed(1)}%`" />
                      </div>
                    </q-linear-progress>
                  </q-card-section>
              </q-card>

              <PremiumWidget title="Top 3 Motoristas do Mês" icon="emoji_events" description="Reconheça os seus motoristas com melhor performance.">
                <div class="row items-end justify-center q-pa-md" style="min-height: 252px;">
                  <PodiumDriverCard v-for="(driver, index) in podiumDrivers" :key="driver.full_name" :driver="driver" :rank="index + 1" :unit="terminologyStore.distanceUnit" />
                    <div v-if="!podiumDrivers?.length" class="text-grey-6">Dados insuficientes para gerar o pódio.</div>
                </div>
              </PremiumWidget>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="isDriver">
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">Meu Desempenho</h1>
          <div class="text-subtitle1 text-grey-7">Olá, {{ authStore.user?.full_name }}. Aqui está seu resumo.</div>
        </div>

        <div class="row q-col-gutter-lg q-mt-sm" v-if="dashboardStore.driverDashboard">
          <div class="col-12 col-md-7">
            <div class="column q-gutter-y-lg">
              <q-card class="dashboard-card">
                <q-card-section>
                  <div class="text-h6">Minhas Métricas (Este Mês)</div>
                </q-card-section>
                <q-card-section class="row q-col-gutter-md">
                  <div class="col-6"><StatCard label="Distância Percorrida" :value="`${driverMetrics?.distance.toFixed(0) ?? 0} ${terminologyStore.distanceUnit}`" icon="route" color="primary" :loading="false"/></div>
                  <div class="col-6"><StatCard label="Horas em Viagem" :value="`${driverMetrics?.hours.toFixed(1) ?? 0}h`" icon="timer" color="teal" :loading="false"/></div>
                  <div class="col-6"><StatCard label="Consumo Médio" :value="`${driverMetrics?.fuel_efficiency.toFixed(1) ?? 0} km/l`" icon="local_gas_station" color="amber" :loading="false"/></div>
                  <div class="col-6"><StatCard label="Alertas Recebidos" :value="driverMetrics?.alerts ?? 0" icon="warning" color="negative" :loading="false"/></div>
                </q-card-section>
              </q-card>

              <q-card class="dashboard-card">
                <q-card-section>
                  <div class="text-h6">Minha Posição no Ranking</div>
                </q-card-section>
                <q-list separator>
                    <q-item v-for="entry in driverRanking" :key="entry.rank" :active="entry.is_current_user" active-class="bg-blue-1 text-primary">
                      <q-item-section avatar><span class="text-h6 text-weight-bold">{{ entry.rank }}º</span></q-item-section>
                      <q-item-section>
                        <q-item-label>{{ entry.name }}</q-item-label>
                      </q-item-section>
                        <q-item-section side class="text-weight-bold">{{ entry.metric.toFixed(0) }} {{ terminologyStore.distanceUnit }}</q-item-section>
                    </q-item>
                </q-list>
              </q-card>
            </div>
          </div>

          <div class="col-12 col-md-5">
              <div class="column q-gutter-y-lg">
                <q-card class="dashboard-card">
                  <q-card-section>
                    <div class="text-h6">Minhas Conquistas</div>
                  </q-card-section>
                  <q-card-section class="flex q-gutter-md">
                      <div v-for="achiev in driverAchievements" :key="achiev.title">
                        <q-avatar :icon="achiev.icon" :color="achiev.unlocked ? 'amber' : 'grey-5'" text-color="white" font-size="32px"/>
                        <q-tooltip>{{ achiev.title }} - {{ achiev.unlocked ? 'Desbloqueado' : 'Bloqueado' }}</q-tooltip>
                      </div>
                  </q-card-section>
                </q-card>

                <q-card class="dashboard-card">
                    <q-card-section>
                    <div class="text-h6">Minhas Próximas Jornadas</div>
                  </q-card-section>
                  <q-list separator>
                    <q-item>
                      <q-item-section class="text-center text-grey-6">Nenhuma jornada agendada.</q-item-section>
                    </q-item>
                  </q-list>
                </q-card>
              </div>
          </div>
        </div>
      </template>

        <template v-else-if="dashboardStore.isLoading">
        <div class="flex flex-center" style="height: 80vh">
          <q-spinner-dots color="primary" size="4em"/>
        </div>
      </template>

    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar, colors } from 'quasar';
import { useDashboardStore } from 'stores/dashboard-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import type { KmPerDay, CostByCategory } from 'src/models/report-models';
import ApexChart from 'vue3-apexcharts';
import StatCard from 'components/StatCard.vue';
import PremiumWidget from 'components/PremiumWidget.vue';
import PodiumDriverCard from 'components/PodiumDriverCard.vue';

// --- Importações do Leaflet ---
import "leaflet/dist/leaflet.css";
import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup,
  LIcon,
} from "@vue-leaflet/vue-leaflet";



// --- LÓGICA DOS ÍCONES DO MAPA ---
/**
  * Gera um ícone de pino de mapa em SVG como uma data URI,
  * contendo um ícone do Material Design no centro.
  * @param pinColor Cor de fundo do pino (ex: '#21BA45').
  * @param iconPath String do path SVG para o ícone interno.
  * @returns Uma string de data URI para ser usada em `iconUrl`.
  */
function createQuasarIconPin(pinColor: string, iconPath: string): string {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="38" height="48">
      <path fill="${pinColor}" stroke="#fff" stroke-width="1.5"
        d="M16 2C9.925 2 5 6.925 5 13c0 7.75 11 18 11 18s11-10.25 11-18C27 6.925 22.075 2 16 2z"/>
      <path fill="white" transform="translate(8, 8) scale(0.7)"
        d="${iconPath}"/>
    </svg>
  `;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

// Paths dos ícones do Material Design (viewport 24x24)
const iconPaths = {
  checkCircle: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z',
  altRoute: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-4 14h-2v-4H9V9h4V5h2v4h2v4h-2v4z',
  build: 'M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z',
};

// Gera os ícones uma vez para reutilização
const iconAvailable = createQuasarIconPin('#21BA45', iconPaths.checkCircle);
const iconInUse = createQuasarIconPin('#F2C037', iconPaths.altRoute);
const iconMaintenance = createQuasarIconPin('#C10015', iconPaths.build);
const fuelCostTotal = computed(() => {
  const costs = managerData.value?.costs_by_category || [];
  
  // A correção está em comparar a string em minúsculas com 'combustível' (também em minúsculas).
  const fuel = costs.find((cost: CostByCategory) => cost.cost_type.toLowerCase() === 'combustível');
  
  return fuel ? fuel.total_amount : 0;
});
// INICIALIZAÇÃO
const dashboardStore = useDashboardStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const $q = useQuasar();
const router = useRouter();

// === CONTROLO DE VISUALIZAÇÃO E DADOS ===
const isManager = computed(() => authStore.isManager);
const isDriver = computed(() => authStore.isDriver);

const selectedPeriod = ref({ label: 'Últimos 30 dias', value: 'last_30_days' });
const periodOptions = [
  { label: 'Últimos 7 dias', value: 'last_7_days' },
  { label: 'Últimos 30 dias', value: 'last_30_days' },
  { label: 'Este Mês', value: 'this_month' },
];
let positionInterval: ReturnType<typeof setInterval> | null = null;

// === Configurações do Mapa ===
const mapRef = ref<typeof LMap | null>(null);
const zoom = ref(4);
// CORRIGIDO: Tipagem explícita para o `center` para resolver o erro do vue-tsc
const center = ref<[number, number]>([-15.793889, -47.882778]); // Centro do Brasil

function getVehicleIcon(status: string) {
  if (status === 'Disponível') return iconAvailable;
  if (status === 'Em uso') return iconInUse;
  if (status === 'Em manutenção') return iconMaintenance;
  return iconAvailable;
}

// === COMPUTED PROPERTIES PARA LIMPAR O TEMPLATE ===
// Gestor
const managerData = computed(() => dashboardStore.managerDashboard);
const kpis = computed(() => managerData.value?.kpis);
const efficiencyKpis = computed(() => managerData.value?.efficiency_kpis);
const recentAlerts = computed(() => managerData.value?.recent_alerts);
const upcomingMaintenances = computed(() => managerData.value?.upcoming_maintenances);
const activeGoal = computed(() => managerData.value?.active_goal);
const podiumDrivers = computed(() => managerData.value?.podium_drivers);
const goalProgress = computed(() => {
  if (!activeGoal.value) return 0;
  // Se o objetivo é reduzir, o progresso é o inverso
  if (activeGoal.value.current_value > activeGoal.value.target_value) {
      const progress = activeGoal.value.target_value / activeGoal.value.current_value;
      return Math.min(progress, 1);
  }
  const progress = activeGoal.value.current_value / activeGoal.value.target_value;
  return Math.min(progress, 1);
});

// Motorista
const driverData = computed(() => dashboardStore.driverDashboard);
const driverMetrics = computed(() => driverData.value?.metrics);
const driverRanking = computed(() => driverData.value?.ranking_context);
const driverAchievements = computed(() => driverData.value?.achievements);


// === WATCHERS ===
watch(() => dashboardStore.vehiclePositions, (newPositions) => {
  if (newPositions && newPositions.length > 0 && mapRef.value?.leafletObject) {
    const bounds = newPositions.map(p => [p.latitude, p.longitude] as [number, number]);
    void nextTick(() => {
      mapRef.value?.leafletObject.fitBounds(bounds);
    });
  }
}, { deep: true });

watch(selectedPeriod, (newPeriod) => {
  if (isManager.value && newPeriod) {
    void dashboardStore.fetchManagerDashboard(newPeriod.value);
  }
});

// === CICLO DE VIDA DO COMPONENTE ===
onMounted(async () => {
  if (isManager.value) {
    await dashboardStore.fetchManagerDashboard(selectedPeriod.value.value);
    await dashboardStore.fetchVehiclePositions();
    positionInterval = setInterval(() => {
      void dashboardStore.fetchVehiclePositions();
    }, 30000);
  } else if (isDriver.value) {
    await dashboardStore.fetchDriverDashboard();
  }
});

onUnmounted(() => {
  if (positionInterval) {
    clearInterval(positionInterval);
  }
  dashboardStore.clearDashboardData();
});


// === FUNÇÕES DE AÇÃO ===
function scheduleMaintenance(vehicleInfo: string) {
  $q.notify({
    color: 'primary',
    icon: 'event',
    message: `Ação para agendar manutenção para ${vehicleInfo} foi disparada.`,
  });
}

// === LÓGICA DE TERMINOLOGIA E GRÁFICOS ===
// CORRIGIDO: Acessa a store diretamente, supondo que journeyNoun é uma string
const journeyNounInProgress = computed(() => `Em ${terminologyStore.journeyNoun}`);

const costAnalysisChart = computed(() => {
  // CORRIGIDO: Acessa os dados diretamente do objeto principal, removendo o aninhamento.
  const data = managerData.value?.costs_by_category || [];
  const series = [{ name: 'Custo Total', data: data.map((item: CostByCategory) => parseFloat(item.total_amount.toFixed(2))) }];
  const options = {
    chart: { type: 'bar', toolbar: { show: false } },
    xaxis: { categories: data.map((item: CostByCategory) => item.cost_type), labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } } },
    yaxis: { labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' }, formatter: (val: number) => `R$ ${val.toLocaleString('pt-BR')}` } },
    plotOptions: { bar: { horizontal: false, columnWidth: '55%', distributed: true } },
    colors: [colors.getPaletteColor('blue-grey-5'), colors.getPaletteColor('blue-5'), colors.getPaletteColor('teal-5'), colors.getPaletteColor('indigo-5'), colors.getPaletteColor('red-5'), colors.getPaletteColor('orange-5')],
    dataLabels: { enabled: false },
    legend: { show: false },
    tooltip: { y: { formatter: (val: number) => `R$ ${val.toFixed(2)}` } },
    theme: { mode: $q.dark.isActive ? 'dark' : 'light' }
  };
  return { series, options };
});

const lineChart = computed(() => {
  // CORRIGIDO: Acessa os dados diretamente do objeto principal, removendo o aninhamento.
  const data = managerData.value?.km_per_day_last_30_days || [];
  const series = [{ name: `${terminologyStore.distanceUnit} Rodados`, data: data.map((item: KmPerDay) => item.total_km) }];
  const options = {
    chart: { id: 'km-per-day-chart', toolbar: { show: false }, zoom: { enabled: false } },
    xaxis: { categories: data.map((item: KmPerDay) => new Date(item.date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })), labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } } },
    yaxis: { labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } } },
    stroke: { curve: 'smooth', width: 3 },
    colors: [colors.getPaletteColor('primary')],
    dataLabels: { enabled: false },
    tooltip: { x: { format: 'dd/MM/yy' } },
    theme: { mode: $q.dark.isActive ? 'dark' : 'light' }
  };
  return { series, options };
});
</script>

<style scoped lang="scss">
.dashboard-page {
  background-color: $grey-1;
  .body--dark & {
    background-color: $dark-page;
  }
}
.page-content-container {
  max-width: 1800px;
  margin: 0 auto;
}
.dashboard-card {
  border-radius: $generic-border-radius;
  box-shadow: none;
  border: 1px solid $grey-3;
  transition: all 0.2s ease-in-out;
  
  .body--dark & {
    border-color: $grey-8;
  }
}
</style>