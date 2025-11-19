<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h4 text-weight-bold q-my-none">
        {{ isFreightSector ? 'Meu Dia' : terminologyStore.journeyPageTitle }}
      </h1>
      <q-btn flat round dense icon="refresh" :loading="isLoading" @click="refreshData" />
    </div>

    <div v-if="isFreightSector">
      <q-card v-if="freightStore.activeFreightOrder" class="bg-primary text-white q-mb-lg floating-card">
        <q-card-section>
          <div class="text-overline">EM ROTA</div>
          <div class="text-h6 ellipsis">{{ freightStore.activeFreightOrder.description || 'Frete sem descrição' }}</div>
        </q-card-section>
        <q-separator dark />
        <q-card-actions>
          <q-btn flat class="full-width" @click="openDriverDialog(freightStore.activeFreightOrder!)">
            Ver Próxima Parada / Concluir
          </q-btn>
        </q-card-actions>
      </q-card>

      <div class="q-mb-lg">
        <div class="text-h5 q-mb-sm">Próximas Tarefas ({{ freightStore.claimedFreightOrders.length }})</div>
        <q-card flat bordered>
          <q-list separator>
            <q-item v-if="freightStore.isLoading && freightStore.claimedFreightOrders.length === 0"><q-item-section><q-skeleton type="text" /></q-item-section></q-item>
            <q-item v-if="!freightStore.isLoading && freightStore.claimedFreightOrders.length === 0" class="text-grey-7 q-pa-md">Nenhuma tarefa na fila.</q-item>
            <q-item v-else v-for="order in freightStore.claimedFreightOrders" :key="order.id" clickable @click="openDriverDialog(order)">
              <q-item-section avatar><q-icon name="assignment_turned_in" color="secondary" /></q-item-section>
              <q-item-section>
                <q-item-label>{{ order.description || 'Frete sem descrição' }}</q-item-label>
                <q-item-label caption>{{ order.stop_points.length }} paradas. Cliente: {{ order.client.name }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <div>
        <div class="text-h5 q-mb-sm">Mural de Oportunidades ({{ freightStore.openOrders.length }})</div>
        <q-card flat bordered>
          <q-list separator>
            <q-item v-if="freightStore.isLoading && freightStore.openOrders.length === 0"><q-item-section><q-skeleton type="text" /></q-item-section></q-item>
            <q-item v-if="!freightStore.isLoading && freightStore.openOrders.length === 0" class="text-grey-7 q-pa-md">Nenhuma oportunidade disponível.</q-item>
            <q-item v-else v-for="order in freightStore.openOrders" :key="order.id" clickable @click="openClaimDialog(order)">
              <q-item-section avatar><q-icon name="add_shopping_cart" color="positive" /></q-item-section>
              <q-item-section>
                <q-item-label>{{ order.description || 'Frete sem descrição' }}</q-item-label>
                <q-item-label caption>{{ order.stop_points.length }} paradas. Cliente: {{ order.client.name }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>

    <div v-else>
      
      <div v-if="activeJourney" class="column items-center justify-center q-py-lg">
        <q-card class="my-card bg-blue-1" flat bordered style="width: 100%; max-width: 500px">
          <q-card-section class="text-center">
            <q-avatar size="80px" color="primary" text-color="white" icon="timer" class="q-mb-md shadow-3" />
            <div class="text-h5 text-primary text-weight-bold">{{ terminologyStore.journeyNoun }} em Andamento</div>
            <div class="text-subtitle1 text-grey-8 q-mt-sm">
              {{ activeJourney.vehicle.brand }} {{ activeJourney.vehicle.model }}
            </div>
            <div class="text-caption text-grey-7">
              {{ terminologyStore.plateOrIdentifierLabel }}: {{ activeJourney.vehicle.license_plate || activeJourney.vehicle.identifier }}
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="row q-col-gutter-md">
              <div class="col-6 text-center">
                <div class="text-caption text-grey">Início</div>
                <div class="text-body1 text-weight-bold">{{ formatTime(activeJourney.start_time) }}</div>
              </div>
              <div class="col-6 text-center">
                <div class="text-caption text-grey">{{ terminologyStore.odometerLabel }} Inicial</div>
                <div class="text-body1 text-weight-bold">{{ getStartValue(activeJourney) }}</div>
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="center" class="q-pa-md">
            <q-btn 
              color="negative" 
              size="lg" 
              :label="`Encerrar ${terminologyStore.journeyNoun}`" 
              icon="stop" 
              class="full-width"
              unelevated
              @click="openEndJourneyDialog"
            />
          </q-card-actions>
        </q-card>
      </div>

      <div v-else class="column items-center justify-center q-py-md">
        <q-card flat bordered style="width: 100%; max-width: 500px">
          <q-card-section>
            <div class="text-h6 text-center q-mb-md">Nova {{ terminologyStore.journeyNoun }}</div>
            
            <q-form @submit.prevent="startSimpleJourney" class="q-gutter-md">
              <q-select
                outlined
                v-model="newJourneyForm.vehicle_id"
                :options="availableVehicleOptions"
                :label="`Selecione o ${terminologyStore.vehicleNoun}`"
                emit-value
                map-options
                :rules="[val => !!val || 'Seleção obrigatória']"
                @update:model-value="onVehicleSelect"
              >
                <template v-slot:prepend><q-icon name="directions_car" /></template>
              </q-select>

              <q-input
                outlined
                type="number"
                v-model.number="newJourneyForm.initial_odometer"
                :label="`${terminologyStore.odometerLabel} Inicial`"
                :rules="[val => val !== null && val !== '' || 'Campo obrigatório']"
              >
                <template v-slot:prepend><q-icon name="speed" /></template>
              </q-input>

              <div class="q-mt-lg">
                <q-btn 
                  type="submit" 
                  color="primary" 
                  size="lg" 
                  :label="terminologyStore.startJourneyButtonLabel" 
                  icon="play_arrow" 
                  class="full-width" 
                  unelevated
                  :loading="journeyStore.isLoading"
                />
              </div>
            </q-form>
          </q-card-section>
        </q-card>

        <div class="q-mt-xl text-center text-grey-6">
          <q-icon name="info" size="sm" />
          <p>Selecione o {{ terminologyStore.vehicleNoun.toLowerCase() }} que irá operar hoje.</p>
        </div>
      </div>

      <q-dialog v-model="isEndJourneyDialogOpen">
        <q-card style="min-width: 350px">
          <q-card-section>
            <div class="text-h6">Encerrar {{ terminologyStore.journeyNoun }}</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
             <q-input
                outlined
                type="number"
                v-model.number="endJourneyForm.final_odometer"
                :label="`${terminologyStore.odometerLabel} Final`"
                autofocus
                :rules="[
                  val => !!val || 'Obrigatório',
                  val => (activeJourney && val >= getStartValue(activeJourney)) || `Deve ser maior ou igual a ${activeJourney ? getStartValue(activeJourney) : 0}`
                ]"
              />
          </q-card-section>

          <q-card-actions align="right" class="text-primary">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn color="primary" label="Confirmar Encerramento" @click="submitEndJourney" :loading="journeyStore.isLoading" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>

    <q-dialog v-model="isClaimDialogOpen">
      <ClaimFreightDialog v-if="selectedOrderForAction" :order="selectedOrderForAction" @close="isClaimDialogOpen = false" />
    </q-dialog>
    <q-dialog v-model="isDriverDialogOpen">
      <DriverFreightDialog v-if="selectedOrderForAction" :order="selectedOrderForAction" @close="handleDriverDialogClose" />
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { useQuasar } from 'quasar';
import { format } from 'date-fns';

// Stores
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useFreightOrderStore } from 'stores/freight-order-store';
import { useJourneyStore } from 'stores/journey-store';
import { useVehicleStore } from 'stores/vehicle-store';

// Componentes e Tipos
import ClaimFreightDialog from 'components/ClaimFreightDialog.vue';
import DriverFreightDialog from 'components/DriverFreightDialog.vue';
import type { FreightOrder } from 'src/models/freight-order-models';
import type { Journey, JourneyCreate, JourneyType, JourneyUpdate } from 'src/models/journey-models';

const $q = useQuasar();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const freightStore = useFreightOrderStore();
const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();

// --- DETECÇÃO DE MODO ---
const isFreightSector = computed(() => authStore.userSector === 'frete');
const isLoading = computed(() => freightStore.isLoading || journeyStore.isLoading || vehicleStore.isLoading);

// --- HELPER: Determina se o sistema usa Horas ou KM ---
const isHoursUnit = computed(() => terminologyStore.distanceUnit.toLowerCase().includes('horas'));

// ===========================================================================
// LÓGICA DE FRETES
// ===========================================================================
const isClaimDialogOpen = ref(false);
const isDriverDialogOpen = ref(false);
const selectedOrderForAction = ref<FreightOrder | null>(null);

function openClaimDialog(order: FreightOrder) {
  selectedOrderForAction.value = order;
  isClaimDialogOpen.value = true;
}

function openDriverDialog(order: FreightOrder) {
  selectedOrderForAction.value = order;
  isDriverDialogOpen.value = true;
}

function handleDriverDialogClose() {
  isDriverDialogOpen.value = false;
  selectedOrderForAction.value = null;
  void refreshData();
}

// ===========================================================================
// LÓGICA DE JORNADA SIMPLES (Agro / Serviços)
// ===========================================================================
const activeJourney = computed(() => journeyStore.currentUserActiveJourney);
const isEndJourneyDialogOpen = ref(false);

const availableVehicleOptions = computed(() => {
  return vehicleStore.availableVehicles.map(v => ({
    label: `${v.brand} ${v.model} - ${v.license_plate || v.identifier}`,
    value: v.id,
    currentKm: v.current_km ?? v.current_engine_hours ?? 0
  }));
});

const newJourneyForm = reactive({
  vehicle_id: null as number | null,
  initial_odometer: null as number | null
});

const endJourneyForm = reactive({
  final_odometer: null as number | null
});

// --- HELPER: Abstrai se é KM ou Hora para exibição ---
function getStartValue(journey: Journey): number {
  return journey.start_mileage ?? journey.start_engine_hours ?? 0;
}

function onVehicleSelect(vehicleId: number) {
  const vehicle = availableVehicleOptions.value.find(v => v.value === vehicleId);
  if (vehicle) {
    newJourneyForm.initial_odometer = vehicle.currentKm;
  }
}

async function startSimpleJourney() {
  if (!newJourneyForm.vehicle_id || newJourneyForm.initial_odometer === null) {
    $q.notify({ type: 'warning', message: 'Preencha todos os campos.' });
    return;
  }

  // CORREÇÃO TYPESCRIPT: Inicializamos o objeto apenas com os campos obrigatórios
  const payload: JourneyCreate = {
    vehicle_id: newJourneyForm.vehicle_id,
    trip_type: 'free_roam' as JourneyType,
  };

  // Adicionamos a propriedade correta dinamicamente para evitar atribuir 'undefined'
  if (isHoursUnit.value) {
    payload.start_engine_hours = newJourneyForm.initial_odometer;
  } else {
    payload.start_mileage = newJourneyForm.initial_odometer;
  }

  try {
    await journeyStore.startJourney(payload);
    
    $q.notify({ type: 'positive', message: terminologyStore.journeyStartSuccessMessage });
    
    newJourneyForm.vehicle_id = null;
    newJourneyForm.initial_odometer = null;
    
    await journeyStore.fetchAllJourneys(); 
  } catch {
    // CORREÇÃO ESLINT: Removemos o (e) não utilizado
    // Erro já tratado no store (notify negative)
  }
}

function openEndJourneyDialog() {
  if (activeJourney.value) {
    endJourneyForm.final_odometer = getStartValue(activeJourney.value); 
  }
  isEndJourneyDialogOpen.value = true;
}

async function submitEndJourney() {
  if (!activeJourney.value || endJourneyForm.final_odometer === null) return;

  const startVal = getStartValue(activeJourney.value);
  if (endJourneyForm.final_odometer < startVal) {
    $q.notify({ type: 'negative', message: 'O valor final não pode ser menor que o inicial.' });
    return;
  }

  // CORREÇÃO TYPESCRIPT: Construção do objeto sem valores 'undefined'
  const payload: JourneyUpdate = {};
  
  if (isHoursUnit.value) {
    payload.end_engine_hours = endJourneyForm.final_odometer;
  } else {
    payload.end_mileage = endJourneyForm.final_odometer;
  }

  try {
    await journeyStore.endJourney(activeJourney.value.id, payload);
    
    $q.notify({ type: 'positive', message: terminologyStore.journeyEndSuccessMessage });
    isEndJourneyDialogOpen.value = false;
    endJourneyForm.final_odometer = null;
  } catch {
    // CORREÇÃO ESLINT: Removemos o (e) não utilizado
  }
}

function formatTime(isoString: string) {
  return format(new Date(isoString), 'HH:mm - dd/MM/yyyy');
}

// ===========================================================================
// GERAL
// ===========================================================================
// CORREÇÃO ESLINT: A função agora é async e usa 'await'
async function refreshData() {
  if (isFreightSector.value) {
    await freightStore.fetchOpenOrders();
    await freightStore.fetchMyPendingOrders();
  } else {
    // Lógica para Agro/Serviços
    await journeyStore.fetchAllJourneys(); 
    await vehicleStore.fetchAllVehicles(); 
  }
}

onMounted(() => {
  // CORREÇÃO ESLINT: Usamos 'void' para marcar a promise como tratada (ignorado retorno)
  void refreshData();
});
</script>

<style lang="scss" scoped>
.floating-card {
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  border-radius: 12px;
}
</style>