<template>
  <q-page padding>

    <div v-if="authStore.userSector === 'frete'" class="row q-col-gutter-lg">
      <div class="col-12 col-md-6">
        <div class="flex items-center justify-between q-mb-sm">
          <h1 class="text-h5 text-weight-bold q-my-none">Mural de Fretes Abertos</h1>
          <q-btn flat round dense icon="refresh" :loading="freightOrderStore.isLoading" @click="refreshFreightData" />
        </div>
        <q-card flat bordered>
          <q-list separator>
            <q-item v-if="freightOrderStore.isLoading && freightOrderStore.openOrders.length === 0" class="q-pa-md"><q-item-section><q-skeleton type="text" width="80%" /><q-skeleton type="text" width="50%" /></q-item-section></q-item>
            <q-item v-if="!freightOrderStore.isLoading && freightOrderStore.openOrders.length === 0" class="text-center text-grey-7 q-pa-md">
              Nenhum frete aberto no momento.
            </q-item>
            <q-item v-else v-for="order in freightOrderStore.openOrders" :key="order.id" clickable @click="openClaimDialog(order)">
              <q-item-section avatar><q-icon name="add_shopping_cart" color="primary" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-medium">{{ order.description || 'Frete sem descrição' }}</q-item-label>
                <q-item-label caption>{{ order.stop_points.length }} paradas. Cliente: {{ order.client.name }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <div class="col-12 col-md-6">
        <div class="flex items-center justify-between q-mb-sm">
          <h1 class="text-h5 text-weight-bold q-my-none">Minhas Tarefas</h1>
          <q-btn flat round dense icon="refresh" :loading="freightOrderStore.isLoading" @click="refreshFreightData" />
        </div>
        <q-card flat bordered>
          <q-list separator>
            <q-item v-if="freightOrderStore.isLoading && freightOrderStore.myPendingOrders.length === 0" class="q-pa-md"><q-item-section><q-skeleton type="text" width="80%" /><q-skeleton type="text" width="50%" /></q-item-section></q-item>
            <q-item v-if="!freightOrderStore.isLoading && freightOrderStore.myPendingOrders.length === 0" class="text-center text-grey-7 q-pa-md">
              Você não tem tarefas ativas.
            </q-item>
            <q-item v-else v-for="order in freightOrderStore.myPendingOrders" :key="order.id" clickable @click="openDriverDialog(order)" :active="order.status === 'Em Trânsito'" active-class="bg-blue-1 text-primary">
              <q-item-section avatar><q-icon :name="order.status === 'Em Trânsito' ? 'local_shipping' : 'assignment_turned_in'" /></q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-medium">{{ order.description || 'Frete sem descrição' }}</q-item-label>
                <q-item-label caption>Status: {{ order.status }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>

    <div v-else>
      <div class="flex items-center justify-between q-mb-md">
        <h1 class="text-h5 text-weight-bold q-my-none">{{ terminologyStore.journeyPageTitle }}</h1>
        <q-btn v-if="!journeyStore.currentUserActiveJourney" @click="openStartDialog" color="primary" icon="add_road" :label="terminologyStore.startJourneyButtonLabel" unelevated />
      </div>

      <q-banner v-if="isDemo" inline-actions rounded class="bg-amber-2 text-black q-mb-lg">
        <template v-slot:avatar>
          <q-icon name="history_toggle_off" color="amber-8" />
        </template>
        <div class="text-weight-medium">
          No Plano Demo, o histórico de jornadas é limitado aos últimos 7 dias.
          <q-btn flat dense color="primary" label="Faça o upgrade" @click="showUpgradeDialog" class="q-ml-sm" />
          para aceder a todos os dados.
        </div>
      </q-banner>
      <q-card v-if="journeyStore.currentUserActiveJourney" class="bg-blue-1 q-mb-lg" flat bordered>
        <q-card-section>
          <div class="text-h6">Você tem uma {{ terminologyStore.journeyNoun.toLowerCase() }} em andamento</div>
          <div class="text-subtitle2" v-if="journeyStore.currentUserActiveJourney.vehicle">{{ terminologyStore.vehicleNoun }}: {{ journeyStore.currentUserActiveJourney.vehicle.brand }} {{ journeyStore.currentUserActiveJourney.vehicle.model }}</div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right"><q-btn @click="openEndDialog()" color="primary" :label="`Finalizar Minha ${terminologyStore.journeyNoun}`" unelevated /></q-card-actions>
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
    </div>

    <q-dialog v-model="isClaimDialogOpen"><ClaimFreightDialog v-if="selectedOrderForAction" :order="selectedOrderForAction" @close="isClaimDialogOpen = false" /></q-dialog>
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
            <q-input outlined v-model="startForm.trip_description" :label="`Descrição da ${terminologyStore.journeyNoun}`" />
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
import { JourneyType, type Journey, type JourneyCreate, type JourneyUpdate } from 'src/models/journey-models';
import type { FreightOrder } from 'src/models/freight-order-models';
import ClaimFreightDialog from 'components/ClaimFreightDialog.vue';
import DriverFreightDialog from 'components/DriverFreightDialog.vue';

const $q = useQuasar();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();
const implementStore = useImplementStore();
const freightOrderStore = useFreightOrderStore();

// --- LÓGICA DE DEMO ADICIONADA ---
const isDemo = computed(() => authStore.user?.role === 'cliente_demo');
function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para aceder ao histórico completo e outras funcionalidades premium, entre em contato com nossa equipe comercial.',
    ok: {
      label: 'Entendido',
      color: 'primary',
      unelevated: true
    },
    persistent: true
  });
}
// --- FIM DA ADIÇÃO ---


// --- ESTADO COMUM A TODOS OS SETORES ---
const isSubmitting = ref(false);

// --- ESTADO PARA AGRO/SERVIÇOS ---
const isStartDialogOpen = ref(false);
const isEndDialogOpen = ref(false);
const editingJourney = ref<Journey | null>(null);
const startForm = ref<Partial<JourneyCreate>>({});
const endForm = ref<Partial<JourneyUpdate>>({});

// --- ESTADO PARA FRETES ---
const isClaimDialogOpen = ref(false);
const isDriverDialogOpen = ref(false);
const selectedOrderForAction = ref<FreightOrder | null>(null);

// --- FUNÇÕES PARA FRETES ---
function openClaimDialog(order: FreightOrder) {
  selectedOrderForAction.value = order;
  isClaimDialogOpen.value = true;
}
function openDriverDialog(order: FreightOrder) {
  void freightOrderStore.fetchOrderDetails(order.id);
  isDriverDialogOpen.value = true;
}
function refreshFreightData() {
  void freightOrderStore.fetchOpenOrders();
  void freightOrderStore.fetchMyPendingOrders();
}

// --- COMPUTEDS E FUNÇÕES PARA AGRO/SERVIÇOS ---
const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id })));
const implementOptions = computed(() => implementStore.availableImplements.map(i => ({ label: `${i.name} (${i.brand} ${i.model})`, value: i.id })));

const columns = computed<QTableColumn[]>(() => {
  const baseColumns: QTableColumn[] = [
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
    { name: 'implement', label: 'Implemento', align: 'left', field: (row: Journey) => row.implement ? `${row.implement.name} (${row.implement.model})` : '---', sortable: true },
  ];
  if (authStore.isManager) {
    baseColumns.push({ name: 'actions', label: 'Ações', field: 'actions', align: 'right' });
  }
  return baseColumns;
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
  startForm.value = { vehicle_id: null, trip_type: JourneyType.FREE_ROAM, trip_description: '', implement_id: null };
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
    await journeyStore.startJourney(startForm.value as JourneyCreate);
    $q.notify({ type: 'positive', message: terminologyStore.journeyStartSuccessMessage });
    isStartDialogOpen.value = false;
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
    title: 'Confirmar Exclusão', message: `Tem certeza que deseja excluir esta ${terminologyStore.journeyNoun.toLowerCase()}?`,
    cancel: true, persistent: true,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
  }).onOk(() => {
    void journeyStore.deleteJourney(journey.id);
  });
}

// --- LÓGICA DE CARREGAMENTO PRINCIPAL (CONDICIONAL) ---
onMounted(() => {
  if (authStore.userSector === 'frete') {
    refreshFreightData();
  } else {
    void journeyStore.fetchAllJourneys();
  }
});
</script>