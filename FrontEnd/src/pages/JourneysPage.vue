<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">{{ terminologyStore.journeyPageTitle }}</h1>
      <q-btn
        v-if="!journeyStore.currentUserActiveJourney"
        @click="openStartDialog"
        color="primary"
        icon="add_road"
        :label="terminologyStore.startJourneyButtonLabel"
        unelevated
      />
    </div>

    <q-card v-if="journeyStore.currentUserActiveJourney" class="bg-blue-1 q-mb-lg" flat bordered>
      <q-card-section>
        <div class="text-h6">Você tem uma {{ terminologyStore.journeyNoun.toLowerCase() }} em andamento</div>
        <div class="text-subtitle2" v-if="journeyStore.currentUserActiveJourney.vehicle">
          {{ terminologyStore.vehicleNoun }}: {{ journeyStore.currentUserActiveJourney.vehicle.brand }} {{ journeyStore.currentUserActiveJourney.vehicle.model }}
        </div>
      </q-card-section>
      <q-separator />
      <q-card-actions align="right">
        <q-btn @click="openEndDialog()" color="primary" :label="`Finalizar Minha ${terminologyStore.journeyNoun}`" unelevated />
      </q-card-actions>
    </q-card>

    <q-card flat bordered>
      <q-table
        :title="terminologyStore.journeyHistoryTitle"
        :rows="journeyStore.journeys"
        :columns="columns"
        row-key="id"
        :loading="journeyStore.isLoading"
        no-data-label="Nenhuma operação encontrada"
      >
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn v-if="props.row.is_active" @click="openEndDialog(props.row)" flat round dense icon="event_busy" color="primary" :title="`Finalizar ${terminologyStore.journeyNoun}`" />
            <q-btn v-if="authStore.isManager" @click="promptToDeleteJourney(props.row)" flat round dense icon="delete" color="negative" :title="`Excluir ${terminologyStore.journeyNoun}`" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isStartDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Iniciar Nova {{ terminologyStore.journeyNoun }}</div></q-card-section>
        <q-form @submit.prevent="handleStartJourney">
          <q-card-section class="q-gutter-y-md">
            <q-select
              outlined
              v-model="startForm.vehicle_id"
              :options="vehicleOptions"
              :label="`${terminologyStore.vehicleNoun} *`"
              emit-value
              map-options
              :rules="[val => !!val || 'Selecione um item']"
            />
            
            <q-select
              v-if="authStore.userSector === 'agronegocio'"
              outlined
              v-model="startForm.implement_id"
              :options="implementOptions"
              label="Implemento (Opcional)"
              emit-value
              map-options
              clearable
              :loading="implementStore.isLoading"
            />
            
            <q-input
              v-if="authStore.userSector === 'agronegocio'"
              outlined v-model.number="startForm.start_engine_hours"
              type="number"
              label="Horas Iniciais *"
              :rules="[val => val !== null && val !== undefined && val >= 0 || 'Valor deve ser positivo']"
            />
            <q-input
              v-else
              outlined v-model.number="startForm.start_mileage"
              type="number"
              label="KM Inicial *"
              :rules="[val => val !== null && val !== undefined && val >= 0 || 'Valor deve ser positivo']"
            />
            
            <q-input outlined v-model="startForm.trip_description" :label="`Descrição da ${terminologyStore.journeyNoun}`" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Iniciar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isEndDialogOpen">
       <q-card style="width: 400px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Finalizar {{ terminologyStore.journeyNoun }}</div></q-card-section>
        <q-form @submit.prevent="handleEndJourney">
          <q-card-section>
            <q-input
              v-if="authStore.userSector === 'agronegocio'"
              autofocus outlined v-model.number="endForm.end_engine_hours"
              type="number"
              label="Horas Finais *"
              :rules="[val => val !== null && val !== undefined && val >= (editingJourney?.start_engine_hours || 0) || 'Valor final inválido']"
            />
            <q-input
              v-else
              autofocus outlined v-model.number="endForm.end_mileage"
              type="number"
              label="KM Final *"
              :rules="[val => val !== null && val !== undefined && val >= (editingJourney?.start_mileage || 0) || 'Valor final inválido']"
            />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Finalizar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { isAxiosError } from 'axios';
import { useJourneyStore } from 'stores/journey-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useImplementStore } from 'stores/implement-store';
import { JourneyType, type Journey, type JourneyCreate, type JourneyUpdate } from 'src/models/journey-models';

const $q = useQuasar();
const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const implementStore = useImplementStore();

const isStartDialogOpen = ref(false);
const isEndDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingJourney = ref<Journey | null>(null);
const startForm = ref<Partial<JourneyCreate>>({});
const endForm = ref<Partial<JourneyUpdate>>({});

const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({
  label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id
})));

const implementOptions = computed(() => implementStore.availableImplements.map(i => ({
  label: `${i.name} (${i.brand} ${i.model})`, value: i.id
})));

const columns = computed<QTableColumn[]>(() => {
  const baseColumns: QTableColumn[] = [
    { name: 'status', label: 'Status', field: (row: Journey) => row.is_active ? 'Ativa' : 'Finalizada', align: 'left', sortable: true },
    { name: 'vehicle', label: terminologyStore.vehicleNoun, field: (row: Journey) => `${row.vehicle?.brand || ''} ${row.vehicle?.model || ''}`, align: 'left', sortable: true },
    { name: 'driver', label: 'Motorista', field: (row: Journey) => row.driver?.full_name || '', align: 'left', sortable: true },
    { name: 'startTime', label: 'Início', field: 'start_time', align: 'center', format: (val: string) => new Date(val).toLocaleString('pt-BR'), sortable: true },
    { name: 'endTime', label: 'Fim', field: 'end_time', align: 'center', format: (val: string | null) => val ? new Date(val).toLocaleString('pt-BR') : '---', sortable: true },
    {
      name: 'distance',
      label: `${terminologyStore.distanceUnit} Rodados`,
      align: 'center',
      field: (row: Journey) => {
        if (authStore.userSector === 'agronegocio' && row.end_engine_hours != null && row.start_engine_hours != null) {
          return (row.end_engine_hours - row.start_engine_hours).toFixed(1);
        }
        if (row.end_mileage != null && row.start_mileage != null) {
          return row.end_mileage - row.start_mileage;
        }
        return '---';
      },
      sortable: true
    },
     { 
      name: 'implement', 
      label: 'Implemento', 
      align: 'left', 
      field: (row: Journey) => row.implement ? `${row.implement.name} (${row.implement.model})` : '---',
      sortable: true
    },
  ];
  if (authStore.isManager) {
    baseColumns.push({ name: 'actions', label: 'Ações', field: 'actions', align: 'right' });
  }
  return baseColumns;
});

watch(() => startForm.value.vehicle_id, (newVehicleId) => {
  if (newVehicleId) {
    const selectedVehicle = vehicleStore.availableVehicles.find(v => v.id === newVehicleId);
    if (selectedVehicle) {
      if (authStore.userSector === 'agronegocio') {
        startForm.value.start_engine_hours = selectedVehicle.current_engine_hours ?? 0;
      } else {
        startForm.value.start_mileage = selectedVehicle.current_km ?? 0;
      }
    }
  }
}, { deep: true });

async function openStartDialog() {
  const promisesToFetch = [vehicleStore.fetchAllVehicles()];

  // Só busca os implementos se o setor for 'agronegocio'
  if (authStore.userSector === 'agronegocio') {
    promisesToFetch.push(implementStore.fetchAvailableImplements());
  }

  await Promise.all(promisesToFetch);

  startForm.value = {
    vehicle_id: null,
    trip_type: JourneyType.FREE_ROAM,
    trip_description: '',
    implement_id: null,
  };
  isStartDialogOpen.value = true;
}

function openEndDialog(journey?: Journey) {
  const journeyToEnd = journey || journeyStore.currentUserActiveJourney;
  if (!journeyToEnd) return;
  editingJourney.value = journeyToEnd;
  endForm.value = {};
  if (authStore.userSector === 'agronegocio') {
    endForm.value.end_engine_hours = journeyToEnd.vehicle.current_engine_hours ?? journeyToEnd.start_engine_hours ?? 0;
  } else {
    endForm.value.end_mileage = journeyToEnd.vehicle.current_km ?? journeyToEnd.start_mileage ?? 0;
  }
  isEndDialogOpen.value = true;
}

async function handleStartJourney() {
  isSubmitting.value = true;
  try {
    await journeyStore.startJourney(startForm.value as JourneyCreate);
    $q.notify({ type: 'positive', message: terminologyStore.journeyStartSuccessMessage });
    isStartDialogOpen.value = false;
  } catch (error: unknown) {
    let message = 'Erro desconhecido ao iniciar operação.';
    if (isAxiosError(error) && error.response?.data?.detail) { message = error.response.data.detail as string; }
    $q.notify({ type: 'negative', message });
  } finally {
    isSubmitting.value = false;
  }
}

async function handleEndJourney() {
  if (!editingJourney.value) return;
  isSubmitting.value = true;
  try {
    const updatedVehicle = await journeyStore.endJourney(editingJourney.value.id, endForm.value);
    $q.notify({ type: 'positive', message: terminologyStore.journeyEndSuccessMessage });
    if (updatedVehicle) {
      await vehicleStore.fetchAllVehicles();
    }
    isEndDialogOpen.value = false;
        await journeyStore.fetchAllJourneys();
            await vehicleStore.fetchAllVehicles(); 


  } catch (error: unknown) {
    let message = 'Erro desconhecido ao finalizar operação.';
    if (isAxiosError(error) && error.response?.data?.detail) { message = error.response.data.detail as string; }
    $q.notify({ type: 'negative', message });
  } finally {
    isSubmitting.value = false;
    editingJourney.value = null;
  }
}

function promptToDeleteJourney(journey: Journey) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem a certeza que deseja excluir esta ${terminologyStore.journeyNoun.toLowerCase()}? Esta ação não pode ser desfeita.`,
    cancel: true,
    persistent: true,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
  }).onOk(() => {
    void journeyStore.deleteJourney(journey.id);
  });
}

onMounted(async () => {
  await journeyStore.fetchAllJourneys();
});
</script>