<template>
  <q-card v-if="order" style="width: 500px; max-width: 90vw;">
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title class="ellipsis">{{ order.description || 'Detalhes do Frete' }}</q-toolbar-title>
      <q-btn flat round dense icon="close" @click="emit('close')" />
    </q-toolbar>

    <div v-if="isSubmitting" class="q-pa-xl text-center">
      <q-spinner color="primary" size="3em" />
    </div>

    <div v-else-if="nextStop">
      <q-card-section>
        <div class="text-overline">PRÓXIMA TAREFA ({{ stopIndex + 1 }}/{{ order.stop_points.length }})</div>
        <div class="text-h6 q-mt-xs">{{ nextStop.type }}: {{ nextStop.address }}</div>
        <div class="text-caption text-grey-7" v-if="nextStop.cargo_description">{{ nextStop.cargo_description }}</div>
      </q-card-section>
      
      <q-card-actions v-if="!isEnRoute" class="q-pa-md">
        <q-btn unelevated color="primary" class="full-width" label="Iniciar Viagem para esta Parada" icon="play_arrow" @click="handleStart" />
      </q-card-actions>
      
      <q-card-section v-if="isEnRoute">
        <q-form @submit.prevent="handleComplete" ref="completeForm">
          <q-input
            outlined
            v-model.number="endMileage"
            type="number"
            label="KM Final do Veículo *"
            :rules="[validateEndMileage]"
            autofocus
            lazy-rules
          />
          <q-btn unelevated color="positive" class="full-width q-mt-md" label="Confirmar Chegada e Concluir Parada" icon="check_circle" type="submit" />
        </q-form>
      </q-card-section>
    </div>
    
    <div v-else class="q-pa-xl text-center">
      <q-icon name="task_alt" size="3em" color="positive" />
      <div class="text-h6 q-mt-md">Frete Concluído!</div>
      <q-btn flat color="primary" class="q-mt-sm" label="Fechar" @click="emit('close')" />
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useFreightOrderStore } from 'stores/freight-order-store';
import type { FreightOrder, StopPoint } from 'src/models/freight-order-models';
import type { Journey } from 'src/models/journey-models';

const props = defineProps<{
  order: FreightOrder | null;
}>();

const emit = defineEmits(['close']);
const freightOrderStore = useFreightOrderStore();

const isSubmitting = ref(false);
const endMileage = ref<number | null>(null);
const activeJourney = ref<Journey | null>(null);
const completeForm = ref<any>(null); // Ref para o formulário

const order = computed(() => freightOrderStore.activeOrderDetails);
const isEnRoute = computed(() => order.value?.status === 'Em Trânsito');
const nextStop = computed((): StopPoint | null => order.value?.stop_points.find(s => s.status === 'Pendente') || null);
const stopIndex = computed(() => order.value?.stop_points.findIndex(s => s.id === nextStop.value?.id) ?? 0);

watch(order, (newOrder) => {
  if (newOrder?.journeys) {
    activeJourney.value = newOrder.journeys.find(j => j.is_active) || null;
  }
  if (newOrder?.status === 'Entregue') {
    setTimeout(() => emit('close'), 1500);
  }
}, { immediate: true, deep: true });

// --- FUNÇÃO DE VALIDAÇÃO COM LOGS ---
function validateEndMileage(val: number | null): boolean | string {
  console.log("--- Validando KM Final ---");
  if (val === null || val === undefined) {
    console.log("Resultado: Falhou (valor nulo/undefined)");
    return 'Campo obrigatório';
  }

  const startKm = activeJourney.value?.start_mileage;
  console.log(`Valor digitado (val): ${val}, Tipo: ${typeof val}`);
  console.log(`KM Inicial da Jornada Ativa (startKm): ${startKm}, Tipo: ${typeof startKm}`);

  if (startKm === undefined || startKm === null) {
      console.log("Resultado: Passou (não foi possível encontrar KM inicial para comparar)");
      return true; // Não podemos validar se não temos um ponto de partida
  }

  if (val < startKm) {
    console.log(`Resultado: Falhou (${val} < ${startKm})`);
    return `O KM final não pode ser menor que o inicial do trecho (${startKm} km)`;
  }
  
  console.log("Resultado: Passou!");
  return true;
}

async function handleStart() {
  if (!order.value || !nextStop.value) return;
  isSubmitting.value = true;
  try {
    const newJourney = await freightOrderStore.startJourneyForStop(order.value.id, nextStop.value.id);
    activeJourney.value = newJourney;
  } finally { isSubmitting.value = false; }
}

async function handleComplete() {
  console.log("--- handleComplete FOI CHAMADA! ---");
  // Adiciona uma validação explícita do formulário
  const isValid = await completeForm.value?.validate();
  if (!isValid) {
    console.log("Formulário inválido, submissão cancelada.");
    return;
  }

  if (!order.value || !nextStop.value || endMileage.value === null || !activeJourney.value) {
    return;
  }
  isSubmitting.value = true;
  try {
    await freightOrderStore.completeStop(order.value.id, nextStop.value.id, activeJourney.value.id, endMileage.value);
    endMileage.value = null;
  } finally { isSubmitting.value = false; }
}
</script>