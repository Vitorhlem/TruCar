<template>
  <q-page padding>

    <div v-if="isDemo" class="q-mb-lg animate-fade">
      <q-banner class=" rounded-borders border-left-primary">
        <template v-slot:avatar>
          <q-icon name="history_edu" color="primary" />
        </template>
        <div class="text-subtitle1 text-weight-bold">Criação de Jornadas Ilimitada</div>
        <div class="text-body2">
          Você pode registrar quantas operações quiser. No entanto, o histórico detalhado exibe apenas os <strong>5 últimos registros</strong>. O restante é arquivado com segurança.
        </div>
        <template v-slot:action>
          <q-btn flat label="Desbloquear Histórico Completo" color="primary" @click="showComparisonDialog = true" />
        </template>
      </q-banner>
    </div>

    <div v-if="authStore.userSector === 'frete'" class="row q-col-gutter-lg">
      <div class="col-12 col-md-6">
        </div>
      <div class="col-12 col-md-6">
        </div>
    </div>

    <div v-else>
      <div class="flex items-center justify-between q-mb-md">
        <h1 class="text-h5 text-weight-bold q-my-none">{{ terminologyStore.journeyPageTitle }}</h1>
        <div class="flex items-center q-gutter-x-sm">
           <q-btn 
            v-if="!journeyStore.currentUserActiveJourney" 
            @click="openStartDialog" 
            color="primary" 
            icon="add_road" 
            :label="terminologyStore.startJourneyButtonLabel" 
            unelevated 
          />
        </div>
      </div>

      <q-card v-if="journeyStore.currentUserActiveJourney" class="bg-grey-10 text-white q-mb-lg border-l-primary" flat bordered>
        <q-card-section>
          <div class="row items-center">
            <q-icon name="directions_car" size="md" class="q-mr-md text-primary" />
            <div>
              <div class="text-h6">Viagem em Andamento</div>
              <div class="text-subtitle2 text-grey-4" v-if="journeyStore.currentUserActiveJourney.vehicle">
                {{ terminologyStore.vehicleNoun }}: {{ journeyStore.currentUserActiveJourney.vehicle.brand }} {{ journeyStore.currentUserActiveJourney.vehicle.model }}
              </div>
            </div>
          </div>
        </q-card-section>
        <q-separator dark />
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
          :pagination="{ rowsPerPage: 10 }"
          :row-class="getRowClass"
        >
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <div v-if="!isRowBlurred(props.rowIndex)">
                <q-btn v-if="props.row.is_active" @click="openEndDialog(props.row)" flat round dense icon="event_busy" color="primary" :title="`Finalizar ${terminologyStore.journeyNoun}`" />
                <q-btn v-if="authStore.isManager" @click="promptToDeleteJourney(props.row)" flat round dense icon="delete" color="negative" :title="`Excluir ${terminologyStore.journeyNoun}`" />
              </div>
              <div v-else>
                <q-icon name="lock" color="grey-5" />
              </div>
            </q-td>
          </template>
        </q-table>
      </q-card>
    </div>
    
    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 700px; max-width: 95vw;">
        <q-card-section class="bg-primary text-white q-py-lg">
          <div class="text-h5 text-weight-bold text-center">Histórico Vitalício</div>
          <div class="text-subtitle1 text-center text-blue-2">Não perca nenhum dado da sua operação</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat separator="horizontal">
            <thead>
              <tr class=" text-uppercase text-grey-7">
                <th class="text-left text-white q-pa-md">Funcionalidade</th>
                <th class="text-center text-weight-bold  text-amber-10 q-pa-md ">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="history" color="grey" size="xs" /> Histórico Visível</td>
                <td class="text-center  text-amber-10">Últimos 5 registros</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Completo e Vitalício</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="speed" color="" size="xs" /> Limite de Viagens</td>
                <td class="text-center text-amber-10">Ilimitado</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg ">
          <div class="text-center full-width">
            <q-btn color="primary" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width" />
            <q-btn flat color="grey" label="Continuar no Demo" class="q-mt-sm" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isClaimDialogOpen" @hide="onClaimDialogClose">
        <ClaimFreightDialog v-if="selectedOrderForAction" :order="selectedOrderForAction" @close="isClaimDialogOpen = false" />
    </q-dialog>
    <q-dialog v-model="isDriverDialogOpen"><DriverFreightDialog :order="freightOrderStore.activeOrderDetails" @close="isDriverDialogOpen = false" /></q-dialog>
    
    <q-dialog v-model="isStartDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Iniciar Nova {{ terminologyStore.journeyNoun }}</div></q-card-section>
        <q-form @submit.prevent="handleStartJourney">
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="startForm.vehicle_id" :options="vehicleOptions" :label="`${terminologyStore.vehicleNoun} *`" emit-value map-options :rules="[val => !!val || 'Selecione um item']" />
            <q-select v-if="authStore.userSector === 'agronegocio'" outlined v-model="startForm.implement_id" :options="implementOptions" label="Implemento (Opcional)" emit-value map-options clearable :loading="implementStore.isLoading" />
            
            <q-input v-if="authStore.userSector === 'agronegocio'" outlined v-model.number="startForm.start_engine_hours" type="number" label="Horas Iniciais *" :rules="[val => val !== null && val !== undefined && val >= 0 || 'Valor deve ser positivo']" />
            <q-input v-else outlined v-model.number="startForm.start_mileage" type="number" label="KM Inicial *" :rules="[val => val !== null && val !== undefined && val >= 0 || 'Valor deve ser positivo']" />
            
            <q-input outlined v-model="startForm.trip_description" :label="`Descrição da ${terminologyStore.journeyNoun} (Opcional)`" />
            
            <q-separator class="q-my-md" />
            <div class="text-subtitle1 text-grey-8">Destino (Opcional)</div>

            <q-input 
              outlined 
              v-model="startForm.destination_cep" 
              label="CEP do Destino" 
              mask="#####-###"
              unmasked-value
              :loading="isCepLoading"
              @blur="handleJourneyCepBlur"
            >
              <template v-slot:prepend><q-icon name="location_pin" /></template>
            </q-input>

            <q-input outlined v-model="startForm.destination_street" label="Rua / Logradouro" />

            <div class="row q-col-gutter-md">
                <div class="col-8"><q-input outlined v-model="startForm.destination_neighborhood" label="Bairro" /></div>
                <div class="col-4"><q-input outlined v-model="startForm.destination_number" label="Nº" /></div>
            </div>
            
            <div class="row q-col-gutter-md">
                <div class="col-8"><q-input outlined v-model="startForm.destination_city" label="Cidade" /></div>
                <div class="col-4"><q-input outlined v-model="startForm.destination_state" label="UF" /></div>
            </div>
          </q-card-section>
          <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup /><q-btn type="submit" unelevated color="primary" label="Iniciar" :loading="isSubmitting" /></q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isEndDialogOpen">
      <q-card style="width: 400px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Finalizar {{ terminologyStore.journeyNoun }}</div></q-card-section>
        <q-form @submit.prevent="handleEndJourney">
          <q-card-section>
            <q-input v-if="authStore.userSector === 'agronegocio'" autofocus outlined v-model.number="endForm.end_engine_hours" type="number" label="Horas Finais *" :rules="[val => val !== null && val !== undefined && val >= (editingJourney?.start_engine_hours || 0) || 'Valor final inválido']" />
            <q-input v-else autofocus outlined v-model.number="endForm.end_mileage" type="number" label="KM Final *" :rules="[val => val !== null && val !== undefined && val >= (editingJourney?.start_mileage || 0) || 'Valor final inválido']" />
          </q-card-section>
          <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup /><q-btn type="submit" unelevated color="primary" label="Finalizar" :loading="isSubmitting" /></q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { isAxiosError } from 'axios';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useJourneyStore } from 'stores/journey-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useImplementStore } from 'stores/implement-store';
import { useFreightOrderStore } from 'stores/freight-order-store';
import { useDemoStore } from 'stores/demo-store';
import { JourneyType, type Journey, type JourneyCreate, type JourneyUpdate } from 'src/models/journey-models';
import type { FreightOrder } from 'src/models/freight-order-models';
import ClaimFreightDialog from 'components/ClaimFreightDialog.vue';
import DriverFreightDialog from 'components/DriverFreightDialog.vue';
import { useCepApi } from 'src/composables/useCepApi';

const $q = useQuasar();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();
const implementStore = useImplementStore();
const freightOrderStore = useFreightOrderStore();
const demoStore = useDemoStore();
const { isCepLoading, fetchAddressByCep } = useCepApi();

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');
const showComparisonDialog = ref(false);

// --- FUNÇÕES DE CENSURA DEMO ---
function isRowBlurred(rowIndex: number) {
  if (!isDemo.value) return false;
  return rowIndex >= 5; // Bloqueia a partir do 6º item (índice 5)
}

function getRowClass(row: Journey, rowIndex: number) {
  if (isRowBlurred(rowIndex)) {
    return 'demo-blur';
  }
  return '';
}
// -------------------------------

const isSubmitting = ref(false);
const isStartDialogOpen = ref(false);
const isEndDialogOpen = ref(false);
const editingJourney = ref<Journey | null>(null);
const startForm = ref<Partial<JourneyCreate>>({});
const endForm = ref<Partial<JourneyUpdate>>({});

const isClaimDialogOpen = ref(false);
const isDriverDialogOpen = ref(false);
const selectedOrderForAction = ref<FreightOrder | null>(null);



function onClaimDialogClose() {
  if (authStore.isDemo) { void demoStore.fetchDemoStats(true); }
  void freightOrderStore.fetchMyPendingOrders();
}

function refreshFreightData() {
  void freightOrderStore.fetchOpenOrders();
  void freightOrderStore.fetchMyPendingOrders();
}

const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id })));
const implementOptions = computed(() => implementStore.availableImplements.map(i => ({ label: `${i.name} (${i.brand} ${i.model})`, value: i.id })));

const columns = computed<QTableColumn[]>(() => {
  const cols: QTableColumn[] = [
    { name: 'status', label: 'Status', field: (row: Journey) => row.is_active ? 'Ativa' : 'Finalizada', align: 'left', sortable: true },
    { name: 'vehicle', label: terminologyStore.vehicleNoun, field: (row: Journey) => `${row.vehicle?.brand || ''} ${row.vehicle?.model || ''}`, align: 'left', sortable: true },
    { name: 'driver', label: 'Motorista', field: (row: Journey) => row.driver?.full_name || '', align: 'left', sortable: true },
    { name: 'startTime', label: 'Início', field: 'start_time', align: 'center', format: (val: string) => new Date(val).toLocaleString('pt-BR'), sortable: true },
    { name: 'endTime', label: 'Fim', field: 'end_time', align: 'center', format: (val: string | null) => val ? new Date(val).toLocaleString('pt-BR') : '---', sortable: true },
    { name: 'distance', label: `${terminologyStore.distanceUnit} Rodados`, align: 'center', field: (row: Journey) => {
        if (authStore.userSector === 'agronegocio' && row.end_engine_hours != null && row.start_engine_hours != null) return (row.end_engine_hours - row.start_engine_hours).toFixed(1);
        if (row.end_mileage != null && row.start_mileage != null) return row.end_mileage - row.start_mileage;
        return '---';
      }, sortable: true
    },
  ];

  if (authStore.userSector === 'agronegocio') {
    cols.push({ name: 'implement', label: 'Implemento', align: 'left', field: (row: Journey) => row.implement ? `${row.implement.name} (${row.implement.model})` : '---', sortable: true });
  }

  if (authStore.isManager) {
    cols.push({ name: 'actions', label: 'Ações', field: 'actions', align: 'right' });
  }
  return cols;
});

watch(() => startForm.value.vehicle_id, (newVehicleId) => {
  if (!newVehicleId) return;
  const selectedVehicle = vehicleStore.availableVehicles.find(v => v.id === newVehicleId);
  if (selectedVehicle) {
    if (authStore.userSector === 'agronegocio') startForm.value.start_engine_hours = selectedVehicle.current_engine_hours ?? 0;
    else startForm.value.start_mileage = selectedVehicle.current_km ?? 0;
  }
});

async function openStartDialog() {
  const promisesToFetch = [vehicleStore.fetchAllVehicles()];
  if (authStore.userSector === 'agronegocio') promisesToFetch.push(implementStore.fetchAvailableImplements());
  await Promise.all(promisesToFetch);
  
  startForm.value = { 
    vehicle_id: null, 
    trip_type: JourneyType.FREE_ROAM, 
    trip_description: '', 
    implement_id: null,
    destination_cep: '',
    destination_street: '',
    destination_number: '',
    destination_neighborhood: '',
    destination_city: '',
    destination_state: '',
  };
  isStartDialogOpen.value = true;
}

function openEndDialog(journey?: Journey) {
  const journeyToEnd = journey || journeyStore.currentUserActiveJourney;
  if (!journeyToEnd) return;
  editingJourney.value = journeyToEnd;
  endForm.value = {};
  if (authStore.userSector === 'agronegocio') endForm.value.end_engine_hours = journeyToEnd.vehicle?.current_engine_hours ?? journeyToEnd.start_engine_hours ?? 0;
  else endForm.value.end_mileage = journeyToEnd.vehicle?.current_km ?? journeyToEnd.start_mileage ?? 0;
  isEndDialogOpen.value = true;
}

async function handleStartJourney() {
  isSubmitting.value = true;
  try {
    if (startForm.value.destination_street) {
        startForm.value.destination_address = [
            startForm.value.destination_street,
            startForm.value.destination_number,
            startForm.value.destination_neighborhood,
            startForm.value.destination_city,
            startForm.value.destination_state
        ].filter(Boolean).join(', ');
    }

    await journeyStore.startJourney(startForm.value as JourneyCreate);
    $q.notify({ type: 'positive', message: terminologyStore.journeyStartSuccessMessage });
    isStartDialogOpen.value = false;
    if (isDemo.value) { void demoStore.fetchDemoStats(true); }
  } catch (error) {
    let message = 'Erro ao iniciar operação.';
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
    await journeyStore.endJourney(editingJourney.value.id, endForm.value);
    $q.notify({ type: 'positive', message: terminologyStore.journeyEndSuccessMessage });
    isEndDialogOpen.value = false;
    await journeyStore.fetchAllJourneys();
    await vehicleStore.fetchAllVehicles();
    if (isDemo.value) { void demoStore.fetchDemoStats(true); }
  } catch (error) {
    let message = 'Erro ao finalizar operação.';
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
    message: `Tem certeza que deseja excluir esta ${terminologyStore.journeyNoun.toLowerCase()}?`,
    cancel: true, persistent: false,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
  }).onOk(() => { // <--- Função síncrona
    void (async () => { // <--- Função assíncrona auto-executável (IIFE)
        await journeyStore.deleteJourney(journey.id);
        if (isDemo.value) { await demoStore.fetchDemoStats(true); }
    })();
  });
}

async function handleJourneyCepBlur() {
  if (startForm.value.destination_cep) {
    const address = await fetchAddressByCep(startForm.value.destination_cep);
    if (address) {
      startForm.value.destination_street = address.street;
      startForm.value.destination_neighborhood = address.neighborhood;
      startForm.value.destination_city = address.city;
      startForm.value.destination_state = address.state;
    }
  }
}

onMounted(() => {
  if (authStore.userSector === 'frete') {
    refreshFreightData();
  } else {
    void journeyStore.fetchAllJourneys();
  }
  if (isDemo.value) {
    void demoStore.fetchDemoStats();
  }
});
</script>

<style scoped>
.border-l-primary {
  border-left: 5px solid var(--q-primary);
}
.border-left-primary {
  border-left: 4px solid var(--q-primary);
}

/* ESTILO DE CENSURA (BLUR) */
:deep(.demo-blur) {
  filter: blur(4px);
  opacity: 0.6;
  pointer-events: none;
  user-select: none;
}
</style>