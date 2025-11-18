<template>
  <q-page padding class="dashboard-page">
    <div class="page-content-container">

      <template v-if="isManager">
        <div class="flex items-center justify-between q-mb-md">
          <div>
            <h1 class="text-h4 text-weight-bold q-my-none">Dashboard de Gestão</h1>
            <div class="text-subtitle1 text-grey-7">
              Visão geral da operação • {{ authStore.user?.full_name }}
            </div>
          </div>
          
          <div class="flex items-center q-gutter-md">
            <q-select 
              v-model="selectedPeriod" 
              :options="periodOptions" 
              label="Período de Análise" 
              dense 
              outlined 
              :bg-color="$q.dark.isActive ? 'grey-10' : 'white'"
              style="min-width: 200px;" 
              class=""
            >
              <template v-slot:prepend><q-icon name="calendar_today" /></template>
            </q-select>

            <q-btn 
              outline 
              color="primary" 
              icon="tune" 
              label="Personalizar" 
              :class="['gt-xs', $q.dark.isActive ? 'bg-grey-10' : 'bg-white']"
              @click="showCustomizationDialog = true"
            >
              <q-tooltip>Mostrar/Ocultar Widgets</q-tooltip>
            </q-btn>

            <q-btn-dropdown color="primary" icon="flash_on" label="Ações" unelevated class="gt-xs">
              <q-list dense style="min-width: 200px">
                <q-item clickable v-close-popup @click="router.push('/vehicles')"><q-item-section avatar><q-icon name="local_shipping" color="primary"/></q-item-section><q-item-section>Novo Veículo</q-item-section></q-item>
                <q-item clickable v-close-popup @click="router.push('/users')"><q-item-section avatar><q-icon name="person_add" color="primary"/></q-item-section><q-item-section>Novo Motorista</q-item-section></q-item>
                <q-item clickable v-close-popup @click="router.push('/journeys')"><q-item-section avatar><q-icon name="route" color="primary"/></q-item-section><q-item-section>Lançar Jornada</q-item-section></q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="scheduleMaintenanceGeneral"><q-item-section avatar><q-icon name="build" color="negative"/></q-item-section><q-item-section>Abrir Chamado</q-item-section></q-item>
              </q-list>
            </q-btn-dropdown>
          </div>
        </div>

        <div v-if="dashboardStore.isLoading" class="row q-col-gutter-md">
           <div class="col-12 col-md-3" v-for="n in 4" :key="n"><q-skeleton type="rect" height="120px" class="rounded-borders" /></div>
           <div class="col-12 col-md-8"><q-skeleton type="rect" height="400px" class="rounded-borders" /></div>
           <div class="col-12 col-md-4"><q-skeleton type="rect" height="400px" class="rounded-borders" /></div>
        </div>

        <div v-else class="fade-in">
          <div v-if="visibleWidgets.kpis" class="row q-col-gutter-md q-mb-lg">
            <div class="col-12 col-sm-6 col-md-4 col-lg-3">
              <StatCard label="Total da Frota" :value="kpis?.total_vehicles ?? 0" :limit="authStore.isDemo ? (authStore.user?.organization?.vehicle_limit ?? -1) : -1" icon="local_shipping" color="primary" :loading="dashboardStore.isLoading" to="/vehicles" class="full-height" />
            </div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-3">
              <StatCard label="Disponíveis" :value="kpis?.available_vehicles ?? 0" icon="check_circle_outline" color="positive" :loading="dashboardStore.isLoading" to="/vehicles?status=available" class="full-height" />
            </div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-3">
              <StatCard :label="journeyNounInProgress" :value="kpis?.in_use_vehicles ?? 0" icon="alt_route" color="warning" :loading="dashboardStore.isLoading" to="/vehicles?status=in_use" class="full-height" />
            </div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-3">
              <StatCard label="Em Manutenção" :value="kpis?.maintenance_vehicles ?? 0" icon="build" color="negative" :loading="dashboardStore.isLoading" to="/maintenance" class="full-height" />
            </div>
          </div>

          <div v-if="visibleWidgets.financialKpis" class="row q-col-gutter-md q-mb-lg">
             <div class="col-12 col-sm-6 col-lg-4">
                <MetricCard title="Custo por KM Rodado" :value="efficiencyKpis?.cost_per_km ?? 0" unit="R$/km" icon="paid" color="deep-purple" trend="+2.5%" trend-color="negative" tooltip="Baseado nos últimos 30 dias" />
             </div>
             <div class="col-12 col-sm-6 col-lg-4">
                <MetricCard title="Gasto Total Combustível" :value="fuelCostTotal" unit="R$" icon="local_gas_station" color="orange-9" :formatter="(v) => `R$ ${v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`" />
             </div>
             <div class="col-12 col-sm-6 col-lg-4">
                <MetricCard title="Taxa de Utilização da Frota" :value="efficiencyKpis?.utilization_rate ?? 0" unit="%" icon="pie_chart" color="teal" :formatter="(v) => `${v.toFixed(1)}%`" tooltip="% de veículos em uso vs total" />
             </div>
          </div>

          <div class="row q-col-gutter-lg">
            <div class="col-12 col-lg-8 column q-gutter-y-lg">
              <div v-if="visibleWidgets.costChart">
                <PremiumWidget title="Análise Detalhada de Custos" icon="insights" :description="`Distribuição de gastos no período (${selectedPeriod.label}).`">
                  <ApexChart 
                    v-if="(costAnalysisChart.series[0]?.data.length || 0) > 0"
                    type="bar" 
                    height="350" 
                    :options="costAnalysisChart.options" 
                    :series="costAnalysisChart.series" 
                  />
                </PremiumWidget>
              </div>
              <div v-if="visibleWidgets.activityChart">
                <PremiumWidget title="Volume de Atividade" icon="show_chart" :description="`Histórico de ${terminologyStore.distanceUnit} rodados por dia.`">
                   <ApexChart 
                    v-if="(lineChart.series[0]?.data.length || 0) > 0"
                    type="area" 
                    height="300" 
                    :options="lineChart.options" 
                    :series="lineChart.series" 
                  />
                </PremiumWidget>
              </div>
              <div v-if="visibleWidgets.maintenance">
                <q-card class="dashboard-card">
                  <q-card-section><div class="text-h6">Próximas Manutenções</div></q-card-section>
                  <q-list separator>
                      <q-item v-for="maint in upcomingMaintenances" :key="maint.vehicle_id">
                      <q-item-section avatar><q-icon name="engineering" color="grey-7" /></q-item-section>
                      <q-item-section>
                        <q-item-label class="text-weight-bold">{{ maint.vehicle_info }}</q-item-label>
                        <q-item-label caption class="text-negative"><q-icon name="event_busy" size="xs"/> Vence em {{ maint.due_date ? new Date(maint.due_date).toLocaleDateString() : `${maint.due_km} km` }}</q-item-label>
                      </q-item-section>
                      <q-item-section side><q-btn outline dense size="sm" color="primary" label="Agendar" @click="scheduleMaintenance(maint.vehicle_id)" /></q-item-section>
                    </q-item>
                    <q-item v-if="!upcomingMaintenances?.length"><q-item-section class="text-center text-grey-6 q-pa-md">Nenhuma manutenção próxima.</q-item-section></q-item>
                  </q-list>
                </q-card>
             </div>
            </div>

            <div class="col-12 col-lg-4 column q-gutter-y-lg">
              <div v-if="visibleWidgets.goal && activeGoal">
                <q-card class="dashboard-card bg-gradient-primary text-white">
                    <q-card-section><div class="text-overline text-blue-1">OBJETIVO DA ORGANIZAÇÃO</div><div class="text-h5 text-weight-bold">{{ activeGoal.title }}</div></q-card-section>
                    <q-card-section class="q-pt-none">
                        <div class="flex justify-between items-end q-mb-sm">
                           <div class="text-h4">{{ activeGoal.current_value.toFixed(0) }} <span class="text-body1">{{ activeGoal.unit }}</span></div>
                           <div class="text-subtitle1">Meta: {{ activeGoal.target_value }}</div>
                        </div>
                        <q-linear-progress size="15px" :value="goalProgress" color="white" track-color="blue-8" class="rounded-borders">
                           <div class="absolute-full flex flex-center"><q-badge color="transparent" text-color="primary" class="text-weight-bold" :label="`${(goalProgress * 100).toFixed(1)}%`" /></div>
                        </q-linear-progress>
                    </q-card-section>
                </q-card>
              </div>
              <div v-if="visibleWidgets.fleetStatusChart">
                <PremiumWidget title="Status da Frota" icon="donut_large" description="Distribuição atual.">
                  <div class="flex flex-center" style="min-height: 300px">
                    <ApexChart 
                        v-if="fleetStatusChart.series.length > 0" 
                        type="donut" 
                        height="280" 
                        :options="fleetStatusChart.options" 
                        :series="fleetStatusChart.series" 
                    />
                  </div>
                </PremiumWidget>
              </div>
              <div v-if="visibleWidgets.alerts">
                 <q-card class="dashboard-card">
                  <q-card-section class="row items-center justify-between"><div class="text-h6 flex items-center"><q-icon name="notifications_active" color="warning" class="q-mr-sm"/> Alertas</div><q-btn flat round icon="refresh" color="grey-7" size="sm" @click="refreshData" /></q-card-section>
                  <q-separator />
                  <q-scroll-area style="height: 300px;">
                    <q-list separator>
                      <q-item v-for="alert in recentAlerts" :key="alert.id" class="q-py-md hover-bg">
                        <q-item-section avatar><q-avatar :icon="alert.icon" :color="alert.color + '-1'" :text-color="alert.color" size="md"/></q-item-section>
                        <q-item-section><q-item-label class="text-weight-medium">{{ alert.title }}</q-item-label><q-item-label caption lines="2">{{ alert.subtitle }}</q-item-label></q-item-section>
                        <q-item-section side top><q-item-label caption>{{ alert.time }}</q-item-label></q-item-section>
                      </q-item>
                        <q-item v-if="!recentAlerts?.length" class="q-pa-lg"><q-item-section class="text-center text-grey-6"><q-icon name="check_circle" size="3em" color="positive" class="q-mb-sm self-center"/> Nenhum alerta.</q-item-section></q-item>
                    </q-list>
                  </q-scroll-area>
                </q-card>
              </div>
              <div v-if="visibleWidgets.podium">
                <PremiumWidget title="Top Motoristas" icon="emoji_events" description="Melhor performance.">
                  <div class="column q-pa-md q-gutter-y-sm">
                    <PodiumDriverCard v-for="(driver, index) in podiumDrivers" :key="driver.full_name" :driver="driver" :rank="index + 1" :unit="terminologyStore.distanceUnit" />
                  </div>
                </PremiumWidget>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="isDriver">
        
        <div class="q-mb-lg">
          <h1 class="text-h5 text-weight-bold q-my-none">
            Olá, {{ authStore.user?.full_name?.split(' ')[0] }}
          </h1>
          <div class="text-subtitle2 text-grey-7">
            {{ authStore.user?.organization?.name }} • {{ authStore.user?.organization?.sector || 'Operação' }}
          </div>
        </div>

        <div class="q-mb-lg">
           <q-banner v-if="activeJourney" class="bg-green-1 text-positive rounded-borders q-pa-md border-positive shadow-1 body--dark-bg-adjust">
             <template v-slot:avatar>
               <q-spinner-radio color="positive" size="2em" />
             </template>
             <div class="text-h6 text-weight-bold q-mb-xs">
                 Em Operação: {{ activeJourney.vehicle_identifier }}
             </div>
             <div class="text-body2">
                 Iniciado às {{ new Date(activeJourney.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}
             </div>
             <template v-slot:action>
                 <q-btn unelevated color="positive" label="Acessar Painel" to="/journeys" />
             </template>
           </q-banner>

           <q-banner v-else class="bg-blue-1 text-primary rounded-borders q-pa-md border-primary shadow-1 body--dark-bg-adjust">
             <template v-slot:avatar>
               <q-icon name="info" color="primary" />
             </template>
             <div class="text-body1 text-weight-medium">
               Você não possui nenhuma {{ terminologyStore.journeyNoun }} ativa no momento.
             </div>
             <template v-slot:action>
               <q-btn flat label="Ver Histórico" :to="`/users/${authStore.user?.id}/stats`" />
             </template>
           </q-banner>
        </div>

        <div class="text-h6 q-mb-sm">Ações Rápidas</div>
        
        <div class="row q-col-gutter-md">
          
          <div class="col-12 col-sm-6">
            <q-btn 
              v-if="activeJourney"
              color="positive" 
              class="full-width full-height q-pa-lg dashboard-card action-btn-large" 
              style="min-height: 120px"
              to="/journeys" 
              unelevated
            >
               <div class="column items-center">
                <q-icon name="stop_circle" size="3.5em" class="q-mb-sm" />
                <div class="text-h6">Gerenciar {{ terminologyStore.journeyNoun }}</div>
                <div class="text-caption text-green-2 text-center">
                   Toque para encerrar ou ver detalhes
                </div>
              </div>
            </q-btn>

            <q-btn 
              v-else
              color="primary" 
              class="full-width full-height q-pa-lg dashboard-card action-btn-large" 
              style="min-height: 120px"
              to="/journeys" 
              unelevated
            >
              <div class="column items-center">
                <q-icon name="play_circle_filled" size="3.5em" class="q-mb-sm" />
                <div class="text-h6">Iniciar {{ terminologyStore.journeyNoun }}</div>
                <div class="text-caption text-blue-2 text-center">
                   Selecione {{ terminologyStore.vehicleNoun }} disponível ou em uso
                </div>
              </div>
            </q-btn>
          </div>

          <div class="col-6 col-sm-3">
            <q-btn color="orange-9" class="full-width full-height q-pa-md dashboard-card" style="min-height: 120px" to="/fuel-logs" unelevated>
              <div class="column items-center"><q-icon name="local_gas_station" size="2.5em" class="q-mb-sm" /><div class="text-subtitle1">Abastecer</div></div>
            </q-btn>
          </div>
          <div class="col-6 col-sm-3">
            <q-btn color="negative" class="full-width full-height q-pa-md dashboard-card" style="min-height: 120px" to="/maintenance" unelevated>
              <div class="column items-center"><q-icon name="build" size="2.5em" class="q-mb-sm" /><div class="text-subtitle1">Problema</div></div>
            </q-btn>
          </div>
          <div class="col-6 col-sm-3">
             <q-btn color="blue-grey-8" class="full-width full-height q-pa-md dashboard-card" style="min-height: 100px" to="/fines" unelevated>
              <div class="column items-center"><q-icon name="gavel" size="2em" class="q-mb-xs" /><div class="text-body2">Multas</div></div>
            </q-btn>
          </div>
          <div class="col-6 col-sm-3">
             <q-btn color="teal" class="full-width full-height q-pa-md dashboard-card" style="min-height: 100px" to="/documents" unelevated>
              <div class="column items-center"><q-icon name="folder_shared" size="2em" class="q-mb-xs" /><div class="text-body2">Documentos</div></div>
            </q-btn>
          </div>
        </div>

        <div class="row q-col-gutter-md q-mt-lg">
          <div class="col-12">
             <q-card class="dashboard-card">
                <q-card-section><div class="text-h6">Seu Desempenho (30 Dias)</div></q-card-section>
                <q-separator />
                <q-card-section class="row text-center">
                   <div class="col-4">
                      <div class="text-h5 text-weight-bold text-primary">{{ driverMetrics?.distance.toFixed(0) || 0 }}</div>
                      <div class="text-caption text-grey">km Percorridos</div>
                   </div>
                   <div class="col-4">
                      <div class="text-h5 text-weight-bold text-teal">{{ driverMetrics?.hours.toFixed(1) || 0 }}h</div>
                      <div class="text-caption text-grey">Em Operação</div>
                   </div>
                   <div class="col-4">
                      <div class="text-h5 text-weight-bold text-orange">{{ driverMetrics?.fuel_efficiency.toFixed(1) || 0 }}</div>
                      <div class="text-caption text-grey">Média (km/l)</div>
                   </div>
                </q-card-section>
             </q-card>
          </div>
        </div>

        <div class="q-mt-lg" v-if="driverAchievements && driverAchievements.length > 0">
            <div class="text-h6 q-mb-sm">Conquistas</div>
            <q-scroll-area style="height: 100px; max-width: 100%;" class="dashboard-card q-pa-sm" horizontal>
              <div class="row no-wrap q-gutter-md items-center" style="height: 100%">
                 <div v-for="achiev in driverAchievements" :key="achiev.title" class="column flex-center q-mx-sm" style="width: 80px">
                    <q-avatar :icon="achiev.icon" :color="achiev.unlocked ? 'amber' : 'grey-3'" :text-color="achiev.unlocked ? 'white' : 'grey-6'" size="md" class="shadow-1"/>
                    <div class="text-caption text-center ellipsis full-width q-mt-xs" style="font-size: 10px; line-height: 1.1;">{{ achiev.title }}</div>
                 </div>
              </div>
            </q-scroll-area>
        </div>

      </template>

      <template v-else-if="dashboardStore.isLoading">
        <div class="flex flex-center" style="height: 80vh"><q-spinner-dots color="primary" size="4em"/></div>
      </template>

    </div>

    <q-dialog v-model="showCustomizationDialog">
      <q-card style="min-width: 350px">
        <q-card-section><div class="text-h6">Personalizar Dashboard</div></q-card-section>
        <q-card-section class="q-pt-none">
          <div class="column q-gutter-sm">
            <q-toggle v-model="visibleWidgets.kpis" label="Indicadores Gerais" color="primary" />
            <q-toggle v-model="visibleWidgets.financialKpis" label="Indicadores Financeiros" color="primary" />
            <q-toggle v-model="visibleWidgets.costChart" label="Gráfico de Custos" color="primary" />
            <q-toggle v-model="visibleWidgets.fleetStatusChart" label="Status da Frota" color="primary" />
            <q-toggle v-model="visibleWidgets.activityChart" label="Atividade" color="primary" />
            <q-toggle v-model="visibleWidgets.alerts" label="Alertas" color="primary" />
            <q-toggle v-model="visibleWidgets.maintenance" label="Manutenções" color="primary" />
            <q-toggle v-model="visibleWidgets.goal" label="Meta" color="primary" />
            <q-toggle v-model="visibleWidgets.podium" label="Pódio" color="primary" />
          </div>
        </q-card-section>
        <q-card-actions align="right"><q-btn flat label="Fechar" color="primary" v-close-popup /></q-card-actions>
      </q-card>
    </q-dialog>
    
    <CreateRequestDialog 
      v-model="showCreateMaintenanceDialog"
      :pre-selected-vehicle-id="selectedVehicleIdForMaintenance"
      :maintenance-type="createDialogType"
      @request-created="refreshData"
    />

  </q-page>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref, watch, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar, colors } from 'quasar';
import { useDashboardStore } from 'stores/dashboard-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import type { KmPerDay, CostByCategory } from 'src/models/report-models';
import ApexChart from 'vue3-apexcharts';

import StatCard from 'components/StatCard.vue';
import MetricCard from 'components/MetricCard.vue'; 
import PremiumWidget from 'components/PremiumWidget.vue';
import PodiumDriverCard from 'components/PodiumDriverCard.vue';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';

const dashboardStore = useDashboardStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const $q = useQuasar();
const router = useRouter();

const isManager = computed(() => authStore.isManager);
const isDriver = computed(() => authStore.isDriver);

const selectedPeriod = ref({ label: 'Últimos 30 dias', value: 'last_30_days' });
const periodOptions = [
  { label: 'Últimos 7 dias', value: 'last_7_days' },
  { label: 'Últimos 30 dias', value: 'last_30_days' },
  { label: 'Este Mês', value: 'this_month' },
];

// === ESTADO ===
const showCustomizationDialog = ref(false);
const showCreateMaintenanceDialog = ref(false); 
const selectedVehicleIdForMaintenance = ref<number | null>(null);
const createDialogType = ref<'PREVENTIVA' | 'CORRETIVA'>('CORRETIVA');

const visibleWidgets = reactive({
  kpis: true, financialKpis: true, costChart: true, fleetStatusChart: true,
  activityChart: true, alerts: true, maintenance: true, goal: true, podium: true
});

const managerData = computed(() => dashboardStore.managerDashboard);
const kpis = computed(() => managerData.value?.kpis);
const efficiencyKpis = computed(() => managerData.value?.efficiency_kpis);
const recentAlerts = computed(() => managerData.value?.recent_alerts);
const upcomingMaintenances = computed(() => managerData.value?.upcoming_maintenances);
const activeGoal = computed(() => managerData.value?.active_goal);
const podiumDrivers = computed(() => managerData.value?.podium_drivers);

const fuelCostTotal = computed(() => {
  const costs = managerData.value?.costs_by_category || [];
  const fuel = costs.find((cost: CostByCategory) => cost.cost_type.toLowerCase() === 'combustível');
  return fuel ? fuel.total_amount : 0;
});

const goalProgress = computed(() => {
  if (!activeGoal.value) return 0;
  if (activeGoal.value.current_value > activeGoal.value.target_value && activeGoal.value.unit === 'R$') {
      const progress = activeGoal.value.current_value / activeGoal.value.target_value;
      return Math.min(progress, 1.2); 
  }
  const progress = activeGoal.value.current_value / activeGoal.value.target_value;
  return Math.min(progress, 1);
});

// Motorista Data
const driverData = computed(() => dashboardStore.driverDashboard);
const driverMetrics = computed(() => driverData.value?.metrics);
const driverAchievements = computed(() => driverData.value?.achievements);
const activeJourney = computed(() => driverData.value?.active_journey);
const journeyNounInProgress = computed(() => `Em ${terminologyStore.journeyNoun}`);

// === GRÁFICOS ===
const costAnalysisChart = computed(() => {
  const data = managerData.value?.costs_by_category || [];
  const series = [{ name: 'Custo Total', data: data.map((item: CostByCategory) => parseFloat(item.total_amount.toFixed(2))) }];
  
  const options = {
    chart: { 
      type: 'bar', toolbar: { show: false },
      events: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        dataPointSelection: (_e: any, _chart: any, config: any) => {
           const index = config.dataPointIndex as number;
           if (typeof index === 'number' && data[index]) {
             const categoryName = data[index].cost_type; 
             void router.push({ path: '/costs', query: { category: categoryName } });
             $q.notify({ message: `Filtrando custos por: ${categoryName}`, color: 'primary', icon: 'filter_alt', timeout: 1000 });
           }
        }
      }
    },
    // Adapta as cores das labels para Dark Mode
    xaxis: { categories: data.map((item: CostByCategory) => item.cost_type), labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } } },
    yaxis: { labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' }, formatter: (val: number) => `R$ ${val.toLocaleString('pt-BR')}` } },
    plotOptions: { bar: { horizontal: false, columnWidth: '55%', distributed: true, borderRadius: 4 } },
    colors: [colors.getPaletteColor('primary'), colors.getPaletteColor('secondary'), colors.getPaletteColor('accent'), colors.getPaletteColor('positive'), colors.getPaletteColor('warning')],
    dataLabels: { enabled: false },
    legend: { show: false },
    tooltip: { theme: $q.dark.isActive ? 'dark' : 'light', y: { formatter: (val: number) => `R$ ${val.toFixed(2)}` } },
    theme: { mode: $q.dark.isActive ? 'dark' : 'light' }
  };
  return { series, options };
});

const lineChart = computed(() => {
  const data = managerData.value?.km_per_day_last_30_days || [];
  const series = [{ name: `${terminologyStore.distanceUnit} Rodados`, data: data.map((item: KmPerDay) => item.total_km) }];
  
  const options = {
    chart: { 
      id: 'km-per-day-chart', toolbar: { show: false }, zoom: { enabled: false },
      events: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        markerClick: (_e: any, _c: any, { dataPointIndex }: any) => {
           if (typeof dataPointIndex === 'number' && data[dataPointIndex]) {
              const clickedDate = data[dataPointIndex].date;
              void router.push({ path: '/journeys', query: { date: clickedDate.toString() } });
              $q.notify({ message: `Ver jornadas de: ${new Date(clickedDate).toLocaleDateString()}`, color: 'secondary', icon: 'event', timeout: 1000 });
           }
        }
      }
    },
    xaxis: { categories: data.map((item: KmPerDay) => new Date(item.date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })), labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } } },
    yaxis: { labels: { style: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } } },
    stroke: { curve: 'smooth', width: 3 },
    colors: [colors.getPaletteColor('secondary')],
    dataLabels: { enabled: false },
    tooltip: { theme: $q.dark.isActive ? 'dark' : 'light', x: { format: 'dd/MM/yy' } },
    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.9, stops: [0, 90, 100] } },
    theme: { mode: $q.dark.isActive ? 'dark' : 'light' }
  };
  return { series, options };
});

const fleetStatusChart = computed(() => {
  if (!kpis.value) return { series: [], options: {} };
   const isDark = $q.dark.isActive;
  const textColor = isDark ? '#FFFFFF' : '#373d3f';
  const series = [kpis.value.available_vehicles, kpis.value.in_use_vehicles, kpis.value.maintenance_vehicles];
  const cardBgColor = isDark ? '#1d1d1d' : '#ffffff';
  const options = {
    labels: ['Disponíveis', 'Em Uso', 'Manutenção'],
    colors: [colors.getPaletteColor('positive'), colors.getPaletteColor('warning'), colors.getPaletteColor('negative')],
    chart: { 
        type: 'donut',
        background: 'transparent', // Fundo transparente essencial
        foreColor: textColor // Cor global do texto
    },
    stroke: {
        show: true,
        colors: [cardBgColor], 
        width: 2
    },
    legend: { position: 'bottom', labels: { colors: $q.dark.isActive ? '#FFFFFF' : '#000000' } },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            total: {
              show: true,
              label: 'Total',
              color: $q.dark.isActive ? '#FFFFFF' : '#000000',
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter: function (w: any) {
                return w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0)
              }
            }
          }
        }
      }
    },
    dataLabels: { enabled: false },
    tooltip: { theme: $q.dark.isActive ? 'dark' : 'light' },
    theme: { mode: $q.dark.isActive ? 'dark' : 'light' }
  };
  return { series, options };
});

watch(selectedPeriod, (newPeriod) => {
  if (isManager.value && newPeriod) {
    void dashboardStore.fetchManagerDashboard(newPeriod.value);
  }
});

onMounted(async () => {
  if (isManager.value) {
    await dashboardStore.fetchManagerDashboard(selectedPeriod.value.value);
  } else if (isDriver.value) {
    await dashboardStore.fetchDriverDashboard();
  }
});

onUnmounted(() => {
  dashboardStore.clearDashboardData();
});

function refreshData() {
  if (isManager.value) {
    void dashboardStore.fetchManagerDashboard(selectedPeriod.value.value);
    $q.notify({ message: 'Dashboard atualizado', color: 'positive', icon: 'check', timeout: 1000 });
  }
}

function scheduleMaintenance(vehicleId: number) {
  selectedVehicleIdForMaintenance.value = vehicleId;
  createDialogType.value = 'PREVENTIVA';
  showCreateMaintenanceDialog.value = true;
}

function scheduleMaintenanceGeneral() {
  selectedVehicleIdForMaintenance.value = null;
  createDialogType.value = 'CORRETIVA';
  showCreateMaintenanceDialog.value = true;
}
</script>

<style scoped lang="scss">
.dashboard-page {
  background-color: #f5f7fa; 
  .body--dark & {
    // Se você tiver variáveis globais de tema, use-as. 
    // Caso contrário, use uma cor fixa escura.
    background-color: #121212; 
  }
}
.page-content-container {
  max-width: 1600px;
  margin: 0 auto;
}
.dashboard-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #000000;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: white;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.08);
  }
  
  // Ajuste para o modo escuro
  .body--dark & {
    background: #1d1d1d; // Cor de fundo para cards em modo escuro
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: none;
    color: #fff;
  }
}

// Ajuste específico para banners em modo escuro
.body--dark .body--dark-bg-adjust {
    background: #1d1d1d !important;
    color: #fff !important;
}

.action-btn-large {
   font-size: 1.1rem;
   transition: all 0.2s;
   &:active {
      transform: scale(0.98);
      opacity: 0.9;
   }
}
.border-primary {
   border: 1px solid var(--q-primary);
}
.bg-gradient-primary {
  background: linear-gradient(135deg, var(--q-primary) 0%, darken($primary, 15%) 100%);
}
.hover-bg:hover {
  background-color: rgba(0,0,0,0.03);
  cursor: default;
  .body--dark & {
      background-color: rgba(255,255,255,0.05);
  }
}
.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}
.border-positive {
   border: 1px solid var(--q-positive);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>