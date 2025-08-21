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
        :loading="vehicleStore.isLoading"
      />
    </div>

    <q-card v-if="journeyStore.currentUserActiveJourney" class="bg-blue-1 q-mb-lg" flat bordered>
      <q-card-section>
        <div class="text-h6">Você tem uma {{ terminologyStore.journeyNoun.toLowerCase() }} em andamento</div>
      </q-card-section>
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
            <q-btn v-if="props.row.is_active && authStore.isManager" @click="openEndDialog(props.row)" flat round dense icon="event_busy" color="primary" :title="`Finalizar ${terminologyStore.journeyNoun}`" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isStartDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Iniciar Nova {{ terminologyStore.journeyNoun }}</div></q-card-section>
        <q-form @submit.prevent="handleStartJourney">
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="startForm.vehicle_id" :options="vehicleOptions" :label="`${terminologyStore.vehicleNoun} *`" emit-value map-options :rules="[val => !!val || 'Selecione um item']" />
            <q-input outlined v-model.number="startForm.start_mileage" type="number" :label="`${terminologyStore.distanceUnit} Inicial *`" :rules="[val => val >= 0 || 'Valor deve ser positivo']" />
            <q-input outlined v-model="startForm.trip_description" :label="`Descrição da ${terminologyStore.journeyNoun}`" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup /><q-btn type="submit" unelevated color="primary" label="Iniciar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isEndDialogOpen">
       <q-card style="width: 400px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Finalizar {{ terminologyStore.journeyNoun }}</div></q-card-section>
        <q-form @submit.prevent="handleEndJourney">
          <q-card-section>
            <q-input autofocus outlined v-model.number="endForm.end_mileage" type="number" :label="`${terminologyStore.distanceUnit} Final *`" :rules="[val => val >= (editingJourney?.start_mileage || 0) || 'Valor final inválido']"/>
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
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
// A LINHA QUE FALTAVA: Importamos a ferramenta para verificar o tipo do erro
import { isAxiosError } from 'axios';

import { useJourneyStore } from 'stores/journey-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { JourneyType, type Journey, type JourneyCreate, type JourneyUpdate } from 'src/models/journey-models';

const $q = useQuasar();
const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();

const isStartDialogOpen = ref(false);
const isEndDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingJourney = ref<Journey | null>(null);
const startForm = ref<Partial<JourneyCreate>>({});
const endForm = ref<JourneyUpdate>({ end_mileage: 0 });

const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({ 
  label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id 
})));

const columns = computed<QTableColumn[]>(() => [
    { name: 'status', label: 'Status', field: (row: Journey) => row.is_active ? 'Ativa' : 'Finalizada', align: 'left' },
    { name: 'vehicle', label: terminologyStore.vehicleNoun, field: (row: Journey) => `${row.vehicle.brand} ${row.vehicle.model}`, align: 'left' },
    { name: 'driver', label: 'Motorista', field: (row: Journey) => row.driver.full_name, align: 'left' },
    { name: 'startTime', label: 'Início', field: 'start_time', align: 'center', format: (val: string) => new Date(val).toLocaleString('pt-BR') },
    { name: 'endTime', label: 'Fim', field: 'end_time', align: 'center', format: (val: string | null) => val ? new Date(val).toLocaleString('pt-BR') : '---' },
    { name: 'distance', label: `${terminologyStore.distanceUnit} Rodados`, align: 'center', field: (row: Journey) => (row.end_mileage && row.end_mileage > 0) ? row.end_mileage - row.start_mileage : '---' },
    ...(authStore.isManager ? [{ name: 'actions', label: 'Ações', field: 'actions', align: 'right' }] as QTableColumn[] : [])
]);

watch(() => startForm.value.vehicle_id, (newVehicleId) => {
  if (newVehicleId) {
    const selectedVehicle = vehicleStore.vehicles.find(v => v.id === newVehicleId);
    if (selectedVehicle) {
      if (authStore.userSector === 'agronegocio') {
        startForm.value.start_mileage = selectedVehicle.current_engine_hours ?? 0;
      } else {
        startForm.value.start_mileage = selectedVehicle.current_km ?? 0;
      }
    }
  }
});

async function openStartDialog() {
  await vehicleStore.fetchAllVehicles();
  startForm.value = {
    vehicle_id: null,
    start_mileage: 0,
    trip_type: JourneyType.FREE_ROAM,
    trip_description: '',
  };
  isStartDialogOpen.value = true;
}

function openEndDialog(journey?: Journey) {
  const journeyToEnd = journey || journeyStore.currentUserActiveJourney;
  if (!journeyToEnd) return;
  editingJourney.value = journeyToEnd;
  if (authStore.userSector === 'agronegocio') {
    endForm.value.end_mileage = journeyToEnd.vehicle.current_engine_hours ?? journeyToEnd.start_mileage ?? 0;
  } else {
    endForm.value.end_mileage = journeyToEnd.vehicle.current_km ?? journeyToEnd.start_mileage ?? 0;
  }
  isEndDialogOpen.value = true;
}

async function handleStartJourney() {
  isSubmitting.value = true;
  try {
    await journeyStore.startJourney(startForm.value as JourneyCreate);
    $q.notify({
      type: 'positive',
      message: terminologyStore.journeyStartSuccessMessage,
    });
    isStartDialogOpen.value = false;
  } catch (error: unknown) { // 'error' é do tipo unknown
    let message = 'Erro desconhecido.';
    // Agora o isAxiosError é reconhecido e o TypeScript sabe que 'error' é um AxiosError dentro do 'if'
    if (isAxiosError(error) && error.response?.data?.detail) {
      message = error.response.data.detail;
    }
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
    $q.notify({
      type: 'positive',
      message: terminologyStore.journeyEndSuccessMessage,
    });
    if (updatedVehicle) {
      await vehicleStore.fetchAllVehicles();
    }
    isEndDialogOpen.value = false;
  } catch (error: unknown) {
    let message = 'Erro desconhecido.';
    if (isAxiosError(error) && error.response?.data?.detail) {
      message = error.response.data.detail;
    }
    $q.notify({ type: 'negative', message });
  } finally {
    isSubmitting.value = false;
    editingJourney.value = null;
  }
}

onMounted(async () => {
  await journeyStore.fetchAllJourneys();
});
</script>