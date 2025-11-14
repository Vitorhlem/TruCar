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

const isEnRoute = computed(() => props.order?.status === 'Em Trânsito');
const nextStop = computed((): StopPoint | null => props.order?.stop_points.find(s => s.status === 'Pendente') || null);
const stopIndex = computed(() => props.order?.stop_points.findIndex(s => s.id === nextStop.value?.id) ?? 0);

watch(() => props.order, (newOrder) => {
  if (newOrder?.journeys) {
    activeJourney.value = newOrder.journeys.find(j => j.is_active) || null;
  }
  if (newOrder?.status === 'Entregue') {
    setTimeout(() => emit('close'), 1500);
  }
}, { immediate: true, deep: true });

function validateEndMileage(val: number | null): boolean | string {
  if (val === null || val === undefined) return 'Campo obrigatório';
  const startKm = activeJourney.value?.start_mileage ?? 0;
  if (val < startKm) return `O KM final não pode ser menor que o inicial (${startKm} km)`;
  return true;
}

async function handleStart() {
  if (!props.order || !nextStop.value) return;
  isSubmitting.value = true;
  try {
    const newJourney = await freightOrderStore.startJourneyForStop(props.order.id, nextStop.value.id);
    activeJourney.value = newJourney; // Atualiza o estado local
    // Força a atualização da lista na página principal
    await freightOrderStore.fetchMyPendingOrders();
  } finally { isSubmitting.value = false; }
}

async function handleComplete() {
  if (!props.order || !nextStop.value || endMileage.value === null || !activeJourney.value) return;
  isSubmitting.value = true;
  try {
    await freightOrderStore.completeStop(props.order.id, nextStop.value.id, activeJourney.value.id, endMileage.value);
    endMileage.value = null;
    await freightOrderStore.fetchMyPendingOrders();
  } finally { isSubmitting.value = false; }
}
</script>