<template>
  <q-page padding>
    <div class="page-content-container">
      <div class="row q-col-gutter-lg">
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="dashboard-card">
            <q-card-section class="flex items-center no-wrap">
              <q-icon :name="vehicleIcon" color="primary" size="44px" class="q-mr-md" />
              <div>
                <div class="text-grey-8">Total de {{ terminologyStore.vehicleNounPlural }}</div>
                <div v-if="!dashboardStore.isLoading" class="text-h4 text-weight-bolder">{{ dashboardStore.summary?.kpis.total_vehicles ?? 0 }}</div>
                <q-skeleton v-else type="text" width="50px" class="text-h4" />
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="dashboard-card">
            <q-card-section class="flex items-center no-wrap">
              <q-icon name="event_available" color="positive" size="44px" class="q-mr-md" />
              <div>
                <div class="text-grey-8">Disponíveis</div>
                <div v-if="!dashboardStore.isLoading" class="text-h4 text-weight-bolder">{{ dashboardStore.summary?.kpis.available_vehicles ?? 0 }}</div>
                <q-skeleton v-else type="text" width="50px" class="text-h4" />
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="dashboard-card">
            <q-card-section class="flex items-center no-wrap">
              <q-icon name="map" color="warning" size="44px" class="q-mr-md" />
              <div>
                <div class="text-grey-8">Em {{ journeyNounInProgress }}</div>
                <div v-if="!dashboardStore.isLoading" class="text-h4 text-weight-bolder">{{ dashboardStore.summary?.kpis.in_use_vehicles ?? 0 }}</div>
                <q-skeleton v-else type="text" width="50px" class="text-h4" />
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="dashboard-card">
            <q-card-section class="flex items-center no-wrap">
              <q-icon name="build" color="negative" size="44px" class="q-mr-md" />
              <div>
                <div class="text-grey-8">Em Manutenção</div>
                <div v-if="!dashboardStore.isLoading" class="text-h4 text-weight-bolder">{{ dashboardStore.summary?.kpis.maintenance_vehicles ?? 0 }}</div>
                <q-skeleton v-else type="text" width="50px" class="text-h4" />
              </div>
              <q-space />
              <q-btn
                v-if="(dashboardStore.summary?.kpis.maintenance_vehicles ?? 0) > 0"
                @click="showMaintenanceDetails"
                flat
                round
                dense
                icon="more_vert"
              >
                <q-tooltip>Ver detalhes</q-tooltip>
              </q-btn>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <div class="row q-col-gutter-lg q-mt-none">
        <div class="col-12 col-lg-7">
            <q-card v-if="!isDemo && dashboardStore.summary?.km_per_day_last_30_days" class="dashboard-card full-height">
              <q-card-section>
                <div class="text-h6">{{ terminologyStore.distanceUnit }} Rodados (Últimos 30 Dias)</div>
              </q-card-section>
              <q-separator />
              <q-card-section v-if="!dashboardStore.isLoading">
                <ApexChart type="area" height="300" :options="lineChart.options" :series="lineChart.series" />
              </q-card-section>
              <q-skeleton v-else height="300px" square />
            </q-card>
            <q-card v-else-if="isDemo" class="dashboard-card premium-placeholder column flex-center full-height">
                <q-icon name="insights" color="amber" size="60px" />
                <div class="text-h6 q-mt-sm">Análise de Atividade</div>
                <div class="text-body2 text-center q-mt-xs">
                  Acompanhe a evolução da sua frota com gráficos detalhados.<br/>Funcionalidade exclusiva do plano completo.
                </div>
                <q-btn @click="showUpgradeDialog" color="primary" label="Saber Mais" unelevated dense class="q-mt-md" />
            </q-card>
        </div>

        <div class="col-12 col-lg-5">
           <div class="column q-gutter-y-lg">
              <q-card class="dashboard-card">
                <q-table
                  flat
                  :title="`${terminologyStore.journeyNounPlural} em Andamento`"
                  :rows="dashboardStore.summary?.active_journeys || []"
                  :columns="activeJourneysColumns"
                  row-key="id"
                  hide-pagination
                  :loading="dashboardStore.isLoading"
                />
              </q-card>
              <q-card v-if="!isDemo && dashboardStore.summary?.upcoming_maintenances" class="dashboard-card">
                <q-table
                  flat
                  title="Próximas Manutenções"
                  :rows="dashboardStore.summary.upcoming_maintenances"
                  :columns="maintenanceColumns"
                  row-key="vehicle_info"
                  hide-pagination
                  :loading="dashboardStore.isLoading"
                />
              </q-card>
              <q-card v-else-if="isDemo" class="dashboard-card premium-placeholder column flex-center">
                <q-icon name="calendar_month" color="amber" size="60px" />
                <div class="text-h6 q-mt-sm">Previsão de Manutenções</div>
                <div class="text-body2 text-center q-mt-xs">
                  Antecipe as suas manutenções e evite paragens inesperadas.<br/>Funcionalidade exclusiva do plano completo.
                </div>
                <q-btn @click="showUpgradeDialog" color="primary" label="Saber Mais" unelevated dense class="q-mt-md" />
              </q-card>
           </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useQuasar, type QTableColumn, colors } from 'quasar';
import { useDashboardStore } from 'stores/dashboard-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import type { KmPerDay, Journey, UpcomingMaintenance } from 'src/models/report-models';
import ApexChart from 'vue3-apexcharts';

const dashboardStore = useDashboardStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const $q = useQuasar();

function showMaintenanceDetails() {
  const maintenanceList = dashboardStore.summary?.upcoming_maintenances || [];
  let message = 'Nenhum detalhe de manutenção disponível.';

  if (maintenanceList.length > 0) {
    message = '<ul>' + maintenanceList.map(item => `<li>${item.vehicle_info} - Próxima em ${item.due_km || 'N/A'} km</li>`).join('') + '</ul>';
  }

  $q.dialog({
    title: 'Veículos com Manutenção Próxima',
    message: message,
    html: true,
    ok: { label: 'Fechar', color: 'primary', unelevated: true }
  });
}

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');
function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para aceder a esta e outras funcionalidades premium, entre em contato com nossa equipe comercial.',
    ok: { label: 'Entendido', color: 'primary', unelevated: true },
    persistent: true
  });
}

const vehicleIcon = computed(() => {
  return authStore.userSector === 'agronegocio' ? 'agriculture' : 'local_shipping';
});

const journeyNounInProgress = computed(() => {
  return authStore.userSector === 'agronegocio' ? 'Operação' : 'Viagem';
});

const lineChart = computed(() => {
  const data = dashboardStore.summary?.km_per_day_last_30_days || [];
  const series = [{
    name: `${terminologyStore.distanceUnit} Rodados`,
    data: data.map((item: KmPerDay) => item.total_km)
  }];
  const options = {
    chart: { id: 'km-per-day-chart', toolbar: { show: false }, zoom: { enabled: false } },
    xaxis: {
      categories: data.map((item: KmPerDay) => new Date(item.date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })),
      labels: {
        style: {
          colors: $q.dark.isActive ? '#FFFFFF' : '#000000'
        }
      }
    },
    yaxis: {
      labels: {
        style: {
          colors: $q.dark.isActive ? '#FFFFFF' : '#000000'
        }
      }
    },
    stroke: { curve: 'smooth', width: 3 },
    colors: [colors.getPaletteColor('primary')],
    dataLabels: { enabled: false },
    tooltip: { x: { format: 'dd/MM/yy' } },
    theme: {
      mode: $q.dark.isActive ? 'dark' : 'light'
    }
  };
  return { series, options };
});

const activeJourneysColumns = computed<QTableColumn[]>(() => [
  { name: 'vehicle', label: terminologyStore.vehicleNoun, field: (row: Journey) => `${row.vehicle.brand} ${row.vehicle.model}`, align: 'left' },
  { name: 'driver', label: 'Motorista', field: (row: Journey) => row.driver.full_name, align: 'left' },
]);

const maintenanceColumns = computed<QTableColumn[]>(() => [
  { name: 'vehicle', label: terminologyStore.vehicleNoun, field: (row: UpcomingMaintenance) => row.vehicle_info, align: 'left' },
  { name: 'due_date', label: 'Data Limite', field: 'due_date', format: (val: string | null) => val ? new Date(val).toLocaleDateString('pt-BR', { timeZone: 'UTC' }) : 'N/A', align: 'right' },
  { name: 'due_km', label: `${terminologyStore.distanceUnit} Limite`, field: 'due_km', align: 'right' },
]);

onMounted(async () => {
  await dashboardStore.fetchSummary();
});
</script>

<style scoped lang="scss">
.page-content-container {
  max-width: 1600px;
  margin: 0 auto;
}

.dashboard-card {
  border: 1px solid $grey-3; // Borda mais suave
  border-radius: $generic-border-radius; // Usa a sua variável de borda
  box-shadow: none;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.07);
  }

  // Adaptação para o Tema Escuro
  .body--dark & {
    border-color: $grey-8;
  }
}

.premium-placeholder {
  min-height: 220px;
  background-color: rgba($grey-5, 0.1);
  border: 1px dashed $grey-7;
  color: $grey-5;

  .body--dark & {
    background-color: rgba($grey-8, 0.2);
    border-color: $grey-7;
    color: $grey-5;
  }
}
</style>