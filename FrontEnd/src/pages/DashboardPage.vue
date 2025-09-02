<template>
  <q-page padding class="q-gutter-y-lg">
    <!-- KPIs Principais (Visíveis para todos) -->
    <div class="row q-col-gutter-md">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="floating-card">
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
        <q-card flat bordered class="floating-card">
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
        <q-card flat bordered class="floating-card">
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
        <q-card flat bordered class="floating-card">
          <q-card-section class="flex items-center no-wrap">
            <q-icon name="build" color="negative" size="44px" class="q-mr-md" />
            <div>
              <div class="text-grey-8">Em Manutenção</div>
              <div v-if="!dashboardStore.isLoading" class="text-h4 text-weight-bolder">{{ dashboardStore.summary?.kpis.maintenance_vehicles ?? 0 }}</div>
              <q-skeleton v-else type="text" width="50px" class="text-h4" />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Gráfico de Atividade (Widget Premium) -->
    <div class="row">
      <div class="col-12">
        <!-- Mostra o gráfico APENAS se não for demo E se houver dados -->
        <q-card v-if="!isDemo && dashboardStore.summary?.km_per_day_last_30_days" flat bordered class="floating-card">
          <q-card-section>
            <div class="text-h6">{{ terminologyStore.distanceUnit }} Rodados (Últimos 30 Dias)</div>
          </q-card-section>
          <q-separator />
          <q-card-section v-if="!dashboardStore.isLoading">
            <ApexChart type="area" height="250" :options="lineChart.options" :series="lineChart.series" />
          </q-card-section>
          <q-skeleton v-else height="250px" square />
        </q-card>
        <!-- Mostra o placeholder se for uma conta demo -->
        <q-card v-else-if="isDemo" flat bordered class="floating-card premium-placeholder column flex-center">
            <q-icon name="insights" color="amber" size="60px" />
            <div class="text-h6 q-mt-sm">Análise de Atividade</div>
            <div class="text-body2 text-grey-8 text-center q-mt-xs">
              Acompanhe a evolução da sua frota com gráficos detalhados.<br/>Funcionalidade exclusiva do plano completo.
            </div>
            <q-btn
              @click="showUpgradeDialog"
              color="primary"
              label="Saber Mais"
              unelevated dense
              class="q-mt-md"
            />
        </q-card>
      </div>
    </div>
    
    <div class="row q-col-gutter-lg">
      <!-- Tabela de Jornadas Ativas (Visível para todos, mas pode estar vazia para contas demo) -->
      <div class="col-12 col-md-6">
          <q-card flat bordered class="floating-card">
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
      </div>
      <!-- Tabela de Manutenções (Widget Premium) -->
      <div class="col-12 col-md-6">
        <!-- Mostra a tabela APENAS se não for demo E se houver dados -->
        <q-card v-if="!isDemo && dashboardStore.summary?.upcoming_maintenances" flat bordered class="floating-card">
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
        <!-- Mostra o placeholder se for uma conta demo -->
        <q-card v-else-if="isDemo" flat bordered class="floating-card premium-placeholder column flex-center">
          <q-icon name="calendar_month" color="amber" size="60px" />
          <div class="text-h6 q-mt-sm">Previsão de Manutenções</div>
          <div class="text-body2 text-grey-8 text-center q-mt-xs">
            Antecipe as suas manutenções e evite paragens inesperadas.<br/>Funcionalidade exclusiva do plano completo.
          </div>
          <q-btn
            @click="showUpgradeDialog"
            color="primary"
            label="Saber Mais"
            unelevated dense
            class="q-mt-md"
          />
        </q-card>
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
// O ApexChart precisa de ser importado se ainda não estiver global
// import ApexChart from 'vue3-apexcharts';

const dashboardStore = useDashboardStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const $q = useQuasar();

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
    xaxis: { categories: data.map((item: KmPerDay) => new Date(item.date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })) },
    stroke: { curve: 'smooth', width: 3 },
    colors: [colors.getPaletteColor('secondary')],
    dataLabels: { enabled: false },
    tooltip: { x: { format: 'dd/MM/yy' } }
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
.premium-placeholder {
  min-height: 332px; // Garante que o placeholder tenha a mesma altura que o card do gráfico
  background-color: #fafafa;
  border: 1px dashed $grey-4;
  color: $grey-7;
}
.floating-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
}
</style>

