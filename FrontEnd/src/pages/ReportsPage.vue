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

        <template v-if="filters.reportType === 'vehicle_consolidated'">
          <div class="col-12 col-md-3">
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
          <div class="col-12 col-md-4">
            <q-input outlined v-model="dateRangeText" label="3. Selecione o Período" readonly dense>
              <template v-slot:prepend><q-icon name="event" class="cursor-pointer" /></template>
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-date v-model="filters.dateRange" range mask="YYYY-MM-DD" />
              </q-popup-proxy>
            </q-input>
          </div>
        </template>
        
        <div class="col-12 col-md-2 text-right">
          <q-btn
            @click="generateReport"
            color="primary"
            label="Gerar Relatório"
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

    <div v-else class="flex flex-center column text-center q-pa-xl text-grey">
      <q-icon name="insights" size="6em" />
      <p class="text-h6 q-mt-md">Selecione os filtros acima para gerar um relatório.</p>
    </div>

  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { format } from 'date-fns';

// Stores e Modelos
import { useReportStore } from 'stores/report-store';
import { useVehicleStore } from 'stores/vehicle-store';
import type { Vehicle } from 'src/models/vehicle-models';

// Componente de Visualização
import VehicleReportDisplay from 'components/reports/VehicleReportDisplay.vue';

const $q = useQuasar();
const reportStore = useReportStore();
const vehicleStore = useVehicleStore();

// Estado dos Filtros
const filters = ref({
  reportType: null as 'vehicle_consolidated' | null,
  vehicleId: null as number | null,
  dateRange: null as { from: string, to: string } | null,
});

const reportOptions = [
  { label: 'Relatório Consolidado de Veículo', value: 'vehicle_consolidated' },
  // Futuramente, poderemos adicionar mais relatórios aqui
];

// Opções do seletor de veículos (lista reativa)
const vehicleOptions = ref<{ label: string, value: number }[]>([]);

const dateRangeText = computed(() => {
  if (filters.value.dateRange) {
    // Usa replace para evitar problemas com fuso horário no new Date()
    const from = format(new Date(filters.value.dateRange.from.replace(/-/g, '/')), 'dd/MM/yyyy');
    const to = format(new Date(filters.value.dateRange.to.replace(/-/g, '/')), 'dd/MM/yyyy');
    return `${from} - ${to}`;
  }
  return '';
});

const isFormValid = computed(() => {
  if (filters.value.reportType === 'vehicle_consolidated') {
    return !!(filters.value.vehicleId && filters.value.dateRange);
  }
  return false;
});

// Função para filtrar a lista de veículos conforme o usuário digita
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

// Função principal que aciona a geração do relatório
async function generateReport() {
  if (!isFormValid.value) {
    $q.notify({ type: 'warning', message: 'Por favor, preencha todos os filtros.' });
    return;
  }
  
  if (filters.value.reportType === 'vehicle_consolidated' && filters.value.vehicleId && filters.value.dateRange) {
    await reportStore.generateVehicleConsolidatedReport(
      filters.value.vehicleId,
      filters.value.dateRange.from,
      filters.value.dateRange.to
    );
  }
}

// Lógica executada quando o componente é montado
onMounted(() => {
  // Limpa qualquer relatório anterior para começar do zero
  reportStore.clearReport();
  
  // Busca a lista completa de veículos para popular o seletor
  if (vehicleStore.vehicles.length === 0) {
    // Usamos um truque de paginação para buscar todos os itens de uma vez
    void vehicleStore.fetchAllVehicles({ page: 1, rowsPerPage: 9999 });
  } else {
    // Se os veículos já estão na store, apenas popula as opções do filtro
    filterVehicles('', (fn) => fn());
  }
});
</script>