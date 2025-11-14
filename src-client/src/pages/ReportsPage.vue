<template>
  <q-page padding>
    <h1 class="text-h4 text-weight-bold q-my-md">Central de Relatórios</h1>

    <q-card flat bordered>
      <q-card-section>
        <div class="row q-col-gutter-md items-center">
          <!-- Filtro 1: Tipo de Relatório -->
          <div class="col-12 col-md-4">
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

          <!-- Filtro 2: Veículo (Condicional) -->
          <div v-if="filters.reportType === 'vehicle_consolidated'" class="col-12 col-md-4">
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

          <!-- Filtro 3: Período -->
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
        </div>

        <!-- ***** NOVA SEÇÃO: Seleção de Dados do Veículo ***** -->
        <div v-if="filters.reportType === 'vehicle_consolidated'" class="q-mt-md">
          <div class="text-subtitle1 q-mb-sm">4. Selecione as seções para incluir:</div>
          <div class="row q-col-gutter-sm">
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.performance_summary" label="Resumo de Performance" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.financial_summary" label="Resumo Financeiro" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.costs_detailed" label="Custos Detalhados" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.fuel_logs_detailed" label="Abastecimentos" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.maintenance_detailed" label="Manutenções" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.fines_detailed" label="Multas" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.journeys_detailed" label="Jornadas" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.documents_detailed" label="Documentos" />
            </div>
            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
              <q-checkbox dense v-model="vehicleReportSections.tires_detailed" label="Pneus" />
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Botão Gerar -->
      <q-card-actions class=" q-pa-md" align="right">
        <q-btn
          @click="generateReport"
          color="primary"
          label="Gerar Relatório"
          icon="summarize"
          unelevated
          :loading="reportStore.isLoading"
          :disable="!isFormValid"
          class="q-px-md"
        />
      </q-card-actions>
    </q-card>

    <!-- Área de Exibição dos Relatórios -->
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

    <div v-else-if="reportStore.fleetManagementReport" class="q-mt-md">
      <FleetManagementReportDisplay :report="reportStore.fleetManagementReport" />
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

import VehicleReportDisplay from 'components/reports/VehicleReportDisplay.vue';
import DriverPerformanceReportDisplay from 'components/reports/DriverPerformanceReportDisplay.vue';
import FleetManagementReportDisplay from 'components/reports/FleetManagementReportDisplay.vue';

const $q = useQuasar();
const reportStore = useReportStore();
const vehicleStore = useVehicleStore();

const filters = ref({
  reportType: null as 'vehicle_consolidated' | 'driver_performance' | 'fleet_management' | null,
  vehicleId: null as number | null,
  dateRange: null as { from: string, to: string } | null,
});

// --- NOVO REF PARA AS SEÇÕES ---
const vehicleReportSections = ref({
  performance_summary: true,
  financial_summary: true,
  costs_detailed: true,
  fuel_logs_detailed: true,
  maintenance_detailed: false,
  fines_detailed: false,
  journeys_detailed: false,
  documents_detailed: false,
  tires_detailed: false,
});

watch(() => filters.value.reportType, () => {
  filters.value.vehicleId = null;
  filters.value.dateRange = null;
  reportStore.clearReports();
});

const reportOptions = [
  { label: 'Relatório Consolidado de Veículo', value: 'vehicle_consolidated' },
  { label: 'Relatório de Desempenho de Motoristas', value: 'driver_performance' },
  { label: 'Relatório Gerencial da Frota', value: 'fleet_management' },
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
  return true;
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

// --- FUNÇÃO ATUALIZADA ---
async function generateReport() {
  if (!isFormValid.value || !filters.value.dateRange) {
    $q.notify({ type: 'warning', message: 'Por favor, preencha todos os filtros obrigatórios.' });
    return;
  }

  const { from, to } = filters.value.dateRange;

  if (filters.value.reportType === 'vehicle_consolidated' && filters.value.vehicleId) {
    // Passa as seções selecionadas para a store
    await reportStore.generateVehicleConsolidatedReport(
      filters.value.vehicleId,
      from,
      to,
      vehicleReportSections.value
    );
  } else if (filters.value.reportType === 'driver_performance') {
    await reportStore.generateDriverPerformanceReport(from, to);
  } else if (filters.value.reportType === 'fleet_management') {
    await reportStore.generateFleetManagementReport(from, to);
  }
}

onMounted(() => {
  reportStore.clearReports();
  if (vehicleStore.vehicles.length === 0) {
    void vehicleStore.fetchAllVehicles({ page: 1, rowsPerPage: 9999 });
  } else {
    filterVehicles('', (fn) => fn());
  }
});
</script>