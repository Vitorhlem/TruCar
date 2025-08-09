<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Registro de Viagens</h1>
      <q-btn
        v-if="!journeyStore.currentUserActiveJourney"
        @click="openStartDialog"
        color="primary"
        icon="add_road"
        label="Iniciar Nova Viagem"
        unelevated
      />
    </div>

    <q-card v-if="journeyStore.currentUserActiveJourney" class="bg-blue-1 q-mb-lg" flat bordered>
      <q-card-section>
        <div class="text-h6">Você tem uma viagem em andamento</div>
        <div class="text-subtitle2">
          Veículo: {{ journeyStore.currentUserActiveJourney.vehicle.brand }} {{ journeyStore.currentUserActiveJourney.vehicle.model }}
        </div>
      </q-card-section>
      <q-separator />
      <q-card-actions align="right">
        <q-btn @click="openEndDialog()" color="primary" label="Finalizar Minha Viagem" unelevated />
      </q-card-actions>
    </q-card>

    <q-card flat bordered class="q-mb-md">
      <q-card-section><div class="text-h6">Filtros e Relatórios</div></q-card-section>
      <q-separator />
      <q-card-section class="row q-col-gutter-md items-center">
        <div class="col-12 col-md-3">
          <q-select outlined v-model="filters.vehicle_id" :options="vehicleOptions" label="Filtrar por Veículo" emit-value map-options clearable />
        </div>
        <div v-if="authStore.isManager" class="col-12 col-md-3">
          <q-select outlined v-model="filters.driver_id" :options="userOptions" label="Filtrar por Motorista" emit-value map-options clearable />
        </div>
        <div class="col-12 col-md-4">
           <q-input outlined v-model="dateRangeText" label="Filtrar por Período" readonly>
            <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover transition-show="scale" transition-hide="scale"><q-date v-model="dateRange" range /></q-popup-proxy></q-icon></template>
          </q-input>
        </div>
        <div class="col-12 col-md-2">
           <q-btn @click="applyFilters" color="primary" label="Filtrar" class="full-width" unelevated/>
        </div>
      </q-card-section>
       <q-separator />
       <q-card-actions>
         <q-btn @click="exportTable" color="secondary" icon="archive" label="Exportar para CSV" flat/>
       </q-card-actions>
    </q-card>

    <q-card flat bordered>
      <q-table
        title="Histórico de Viagens"
        :rows="journeyStore.journeys"
        :columns="columns"
        row-key="id"
        :loading="journeyStore.isLoading"
        no-data-label="Nenhuma viagem encontrada para os filtros aplicados"
      >
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="props.row.is_active ? 'orange-8' : 'grey-7'" :label="props.row.is_active ? 'Ativa' : 'Finalizada'" />
          </q-td>
        </template>
        <template v-if="authStore.isManager" v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn v-if="props.row.is_active" @click="openEndDialog(props.row)" flat round dense icon="event_busy" color="primary" title="Finalizar Viagem de Outro Usuário" class="q-mr-sm" />
            <q-btn @click="promptToDeleteJourney(props.row)" flat round dense icon="delete" color="negative" title="Excluir Viagem do Histórico" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isStartDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Iniciar Nova Viagem</div></q-card-section>
        <q-form @submit.prevent="handleStartJourney">
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="startForm.vehicle_id" :options="vehicleOptions" label="Veículo *" emit-value map-options :rules="[val => !!val || 'Selecione um veículo']" />
            <q-input outlined v-model.number="startForm.start_mileage" type="number" label="KM Inicial *" :rules="[val => val > 0 || 'KM deve ser positivo']" />
            <q-option-group v-model="startForm.trip_type" :options="tripTypeOptions" inline />
            <q-input v-if="startForm.trip_type === 'specific_destination'" outlined v-model="startForm.destination_address" label="Endereço de Destino" />
            <q-input v-else outlined v-model="startForm.trip_description" label="Descrição da Viagem" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup /><q-btn type="submit" unelevated color="primary" label="Iniciar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isEndDialogOpen">
       <q-card style="width: 400px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Finalizar Viagem</div></q-card-section>
        <q-form @submit.prevent="handleEndJourney">
          <q-card-section>
            <q-input autofocus outlined v-model.number="endForm.end_mileage" type="number" label="KM Final *" :rules="[val => val >= (editingJourney?.start_mileage || 0) || 'KM final inválido']"/>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup /><q-btn type="submit" unelevated color="primary" label="Finalizar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useJourneyStore } from 'stores/journey-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useUserStore } from 'stores/user-store';
import { useAuthStore } from 'stores/auth-store';
import { exportFile, useQuasar, type QTableColumn } from 'quasar';
import type { Journey, JourneyCreate, JourneyUpdate } from 'src/models/journey-models';

const $q = useQuasar();
const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();
const userStore = useUserStore();
const authStore = useAuthStore();

const isStartDialogOpen = ref(false);
const isEndDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingJourney = ref<Journey | null>(null);

const startForm = ref<JourneyCreate>({ vehicle_id: 0, start_mileage: 0, trip_type: 'specific_destination' });
const endForm = ref<JourneyUpdate>({ end_mileage: 0 });

const filters = ref<{ vehicle_id: number | null, driver_id: number | null, date_from: string | null, date_to: string | null }>({ vehicle_id: null, driver_id: null, date_from: null, date_to: null });
const dateRange = ref<{from: string, to: string} | string | null>(null);
const dateRangeText = computed(() => {
  if (typeof dateRange.value === 'string') return dateRange.value;
  if (dateRange.value?.from && dateRange.value?.to) return `${dateRange.value.from} - ${dateRange.value.to}`;
  return '';
});

const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate})`, value: v.id })));
const userOptions = computed(() => userStore.users.map(u => ({ label: u.full_name, value: u.id })));
const tripTypeOptions = [ { label: 'Destino Específico', value: 'specific_destination' }, { label: 'Livre', value: 'free_roam' } ];

const columns = computed<QTableColumn[]>(() => [
    { name: 'status', label: 'Status', field: 'is_active', align: 'center' },
    { name: 'vehicle', label: 'Veículo', field: (row: Journey) => `${row.vehicle.brand} ${row.vehicle.model}`, align: 'left' },
    { name: 'driver', label: 'Motorista', field: (row: Journey) => row.driver.full_name, align: 'left' },
    { name: 'startTime', label: 'Início', field: 'start_time', align: 'center', format: (val: string) => new Date(val).toLocaleString('pt-BR') },
    { name: 'endTime', label: 'Fim', field: 'end_time', align: 'center', format: (val: string | null) => val ? new Date(val).toLocaleString('pt-BR') : '---' },
    { name: 'km', label: 'KM Rodados', align: 'center', field: (row: Journey) => (row.end_mileage && row.end_mileage > 0) ? row.end_mileage - row.start_mileage : '---' },
    ...(authStore.isManager ? [{ name: 'actions', label: 'Ações', field: 'actions', align: 'right' }] as QTableColumn[] : [])
]);

function applyFilters() {
  if (typeof dateRange.value === 'object' && dateRange.value) {
    filters.value.date_from = dateRange.value.from;
    filters.value.date_to = dateRange.value.to;
  } else {
    filters.value.date_from = null;
    filters.value.date_to = null;
  }
  void journeyStore.fetchAllJourneys(filters.value);
}

// --- FUNÇÃO EXPORTAR CORRIGIDA E MELHORADA ---
function exportTable() {
  const exportableColumns = columns.value.filter(col => col.name !== 'actions');
  const header = exportableColumns.map(col => col.label).join(',');

  const rows = journeyStore.journeys.map(row => {
    return exportableColumns.map(col => {
      const rawValue = col.field instanceof Function ? col.field(row) : row[col.field as keyof typeof row];
      const formattedValue = col.format ? col.format(rawValue, row) : rawValue;
      
      // Converte para string de forma segura, tratando nulos e indefinidos
      const sanitizedValue = String(formattedValue ?? '').replace(/"/g, '""');
      
      return `"${sanitizedValue}"`;
    }).join(',');
  }).join('\r\n');

  const content = `${header}\r\n${rows}`;
  const status = exportFile('historico-viagens.csv', '\uFEFF' + content, 'text/csv');

  if (status !== true) {
    $q.notify({ message: 'O navegador bloqueou o download...', color: 'negative' });
  }
}

function openStartDialog() {
  startForm.value = { vehicle_id: 0, start_mileage: 0, trip_type: 'specific_destination' };
  isStartDialogOpen.value = true;
}

function openEndDialog(journey?: Journey) {
  const journeyToEnd = journey || journeyStore.currentUserActiveJourney;
  if (!journeyToEnd) return;
  editingJourney.value = journeyToEnd;
  endForm.value.end_mileage = journeyToEnd.start_mileage || 0;
  isEndDialogOpen.value = true;
}

async function handleStartJourney() {
  isSubmitting.value = true;
  try {
    await journeyStore.startJourney(startForm.value);
    isStartDialogOpen.value = false;
  } finally {
    isSubmitting.value = false;
  }
}

async function handleEndJourney() {
  if (!editingJourney.value) return;
  isSubmitting.value = true;
  try {
    await journeyStore.endJourney(editingJourney.value.id, endForm.value);
    isEndDialogOpen.value = false;
  } finally {
    isSubmitting.value = false;
    editingJourney.value = null;
  }
}

function promptToDeleteJourney(journey: Journey) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja excluir permanentemente a viagem do motorista ${journey.driver.full_name} com o veículo ${journey.vehicle.model}?`,
    cancel: { label: 'Cancelar', flat: true },
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
    persistent: true,
  }).onOk(() => {
    void journeyStore.deleteJourney(journey.id);
  });
}

onMounted(async () => {
  await journeyStore.fetchAllJourneys();
  await vehicleStore.fetchAllVehicles();
  if (authStore.isManager) {
    await userStore.fetchAllUsers();
  }
});
</script>