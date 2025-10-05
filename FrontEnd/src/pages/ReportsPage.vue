<template>
  <q-page padding>
    <h1 class="text-h4 text-weight-bold q-my-md">Central de Relatórios</h1>

    <q-card flat bordered>
      <q-card-section class="row q-col-gutter-md items-center">
        <div class="col-12 col-md-3">
          <q-select
            outlined
            v-model="filters.reportType"
            :options="reportOptions"
            label="1. Selecione o Tipo de Relatório"
            emit-value
            map-options
            dense
          />
        </div>

        <div v-if="filters.reportType === 'vehicle_consolidated'" class="col-12 col-md-3">
          <q-select
            outlined
            v-model="filters.vehicleId"
            :options="vehicleOptions"
            label="2. Selecione o Veículo"
            emit-value
            map-options
            dense
            use-input
            @filter="filterVehicles"
            :loading="vehicleStore.isLoading"
          >
            <template v-slot:no-option>
              <q-item><q-item-section class="text-grey">Nenhum veículo encontrado</q-item-section></q-item>
            </template>
          </q-select>
        </div>

        <div v-if="filters.reportType" class="col-12 col-md-4">
          <q-input
            outlined
            v-model="dateRangeText"
            :label="filters.reportType === 'vehicle_consolidated' ? '3. Selecione o Período' : '2. Selecione o Período'"
            readonly
            dense
          >
            <template v-slot:prepend><q-icon name="event" class="cursor-pointer" /></template>
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <q-date v-model="filters.dateRange" range mask="YYYY-MM-DD" />
            </q-popup-proxy>
          </q-input>
        </div>

        <div class="col-12 col-md-2 text-right">
          <q-btn
            @click="generateReport"
            color="primary"
            label="Gerar"
            icon="summarize"
            unelevated
            :loading="reportStore.isLoading"
            :disable="!isFormValid"
            class="full-width"
          />
        </div>
      </q-card-section>
    </q-card>

    <div v-if="reportStore.isLoading" class="flex flex-center q-mt-xl">
      <q-spinner-dots color="primary" size="3em" />
      <div class="q-ml-md text-grey">Gerando dados...</div>
    </div>

    <div v-else-if="reportStore.vehicleReport" class="q-mt-md">
      <VehicleReportDisplay :report="reportStore.vehicleReport" />
    </div>

    <div v-else-if="reportStore.driverPerformanceReport" class="q-mt-md">
      <DriverPerformanceReportDisplay :report="reportStore.driverPerformanceReport" />
    </div>

    <div v-else class="flex flex-center column text-center q-pa-xl text-grey">
      <q-icon name="insights" size="6em" />
      <p class="text-h6 q-mt-md">Selecione os filtros acima para gerar um relatório.</p>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { format } from 'date-fns';
import { useReportStore } from 'stores/report-store';
import { useVehicleStore } from 'stores/vehicle-store';
import type { Vehicle } from 'src/models/vehicle-models';

// Importa ambos os componentes de visualização
import VehicleReportDisplay from 'components/reports/VehicleReportDisplay.vue';
import DriverPerformanceReportDisplay from 'components/reports/DriverPerformanceReportDisplay.vue';

const $q = useQuasar();
const reportStore = useReportStore();
const vehicleStore = useVehicleStore();

const filters = ref({
  reportType: null as 'vehicle_consolidated' | 'driver_performance' | null,
  vehicleId: null as number | null,
  dateRange: null as { from: string, to: string } | null,
});

// Reseta filtros secundários e limpa relatórios ao trocar o tipo
watch(() => filters.value.reportType, () => {
  filters.value.vehicleId = null;
  filters.value.dateRange = null;
  reportStore.clearReports();
});

const reportOptions = [
  { label: 'Relatório Consolidado de Veículo', value: 'vehicle_consolidated' },
  { label: 'Relatório de Desempenho de Motoristas', value: 'driver_performance' },
];

const vehicleOptions = ref<{ label: string, value: number }[]>([]);

const dateRangeText = computed(() => {
  if (filters.value.dateRange) {
    const from = format(new Date(filters.value.dateRange.from.replace(/-/g, '/')), 'dd/MM/yyyy');
    const to = format(new Date(filters.value.dateRange.to.replace(/-/g, '/')), 'dd/MM/yyyy');
    return `${from} - ${to}`;
  }
  return '';
});

const isFormValid = computed(() => {
  if (!filters.value.reportType || !filters.value.dateRange) return false;

  if (filters.value.reportType === 'vehicle_consolidated') {
    return !!filters.value.vehicleId;
  }
  if (filters.value.reportType === 'driver_performance') {
    return true; // Para este relatório, só o período é obrigatório
  }
  return false;
});

function filterVehicles(val: string, update: (callback: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    vehicleOptions.value = vehicleStore.vehicles
      .filter((v: Vehicle) =>
        (v.license_plate?.toLowerCase().includes(needle) ||
         v.identifier?.toLowerCase().includes(needle) ||
         `${v.brand} ${v.model}`.toLowerCase().includes(needle))
      )
      .map((v: Vehicle) => ({
        label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`,
        value: v.id,
      }));
  });
}

async function generateReport() {
  if (!isFormValid.value) {
    $q.notify({ type: 'warning', message: 'Por favor, preencha todos os filtros obrigatórios.' });
    return;
  }
  
  // Garante que dateRange não é nulo antes de desestruturar
  const dateRange = filters.value.dateRange;
  if (!dateRange) return;

  const { from, to } = dateRange;

  if (filters.value.reportType === 'vehicle_consolidated' && filters.value.vehicleId) {
    await reportStore.generateVehicleConsolidatedReport(filters.value.vehicleId, from, to);
  } else if (filters.value.reportType === 'driver_performance') {
    await reportStore.generateDriverPerformanceReport(from, to);
  }
}

onMounted(() => {
  // --- CORREÇÃO APLICADA AQUI ---
  // A função se chama 'clearReports' (plural) na store.
  reportStore.clearReports();
  // --- FIM DA CORREÇÃO ---
  
  if (vehicleStore.vehicles.length === 0) {
    void vehicleStore.fetchAllVehicles({ page: 1, rowsPerPage: 9999 });
  } else {
    filterVehicles('', (fn) => fn());
  }
});
</script>