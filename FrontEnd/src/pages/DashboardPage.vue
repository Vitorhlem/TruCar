<template>
  <q-page padding class="q-gutter-y-lg">
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

    <div class="row">
      <div class="col-12">
        <q-card flat bordered class="floating-card">
          <q-card-section>
            <div class="text-h6">{{ terminologyStore.distanceUnit }} Rodados (Últimos 30 Dias)</div>
          </q-card-section>
          <q-separator />
          <q-card-section v-if="!dashboardStore.isLoading">
            <ApexChart type="area" height="250" :options="lineChart.options" :series="lineChart.series" />
          </q-card-section>
          <q-skeleton v-else height="250px" square />
        </q-card>
      </div>
    </div>
    
    <div class="row q-col-gutter-lg">
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
        <div class="col-12 col-md-6">
            <q-card flat bordered class="floating-card">
              <q-table
                flat
                title="Próximas Manutenções"
                :rows="dashboardStore.summary?.upcoming_maintenances || []"
                :columns="maintenanceColumns"
                row-key="vehicle_info"
                hide-pagination
                :loading="dashboardStore.isLoading"
              />
            </q-card>
        </div>
      </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useDashboardStore } from 'stores/dashboard-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { colors, type QTableColumn } from 'quasar';
import type { KmPerDay, Journey, UpcomingMaintenance } from 'src/models/report-models';

const dashboardStore = useDashboardStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();

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
    chart: { id: 'km-per-day-chart', toolbar: { show: false } },
    xaxis: { categories: data.map((item: KmPerDay) => new Date(item.date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })) },
    stroke: { curve: 'smooth', width: 3 },
    colors: [colors.getPaletteColor('secondary')],
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