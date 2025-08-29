<!-- ARQUIVO: src/components/DriverFreightDialog.vue -->
<template>
  <q-card style="width: 500px; max-width: 90vw;">
    <q-toolbar v-if="order" class="bg-primary text-white">
      <q-toolbar-title class="ellipsis">{{ order.description || 'Detalhes do Frete' }}</q-toolbar-title>
      <q-btn flat round dense icon="close" @click="emit('close')" />
    </q-toolbar>

    <div v-if="isLoading" class="q-pa-xl text-center"><q-spinner /></div>
    <div v-else-if="!order" class="q-pa-xl text-center">Falha ao carregar dados.</div>

    <div v-else-if="nextStop">
      <q-card-section>
        <div class="text-overline">PRÓXIMA TAREFA</div>
        <div class="text-h6">{{ nextStop.type }}: {{ nextStop.address }}</div>
        <div class="text-caption text-grey-7">{{ nextStop.cargo_description }}</div>
      </q-card-section>
      
      <q-card-actions v-if="!isEnRoute" class="q-pa-md">
        <q-btn unelevated color="primary" class="full-width" label="Iniciar Viagem para esta Parada" icon="play_arrow" @click="handleStart" :loading="isSubmitting" />
      </q-card-actions>
      
      <q-card-section v-if="isEnRoute">
        <q-form @submit.prevent="handleComplete">
          <q-input outlined v-model.number="endMileage" type="number" label="KM Final do Veículo *" :rules="[val => val >= (order?.vehicle?.current_km || 0)]" />
          <q-btn unelevated color="positive" class="full-width q-mt-md" label="Confirmar Chegada e Concluir Parada" icon="check_circle" type="submit" :loading="isSubmitting" />
        </q-form>
      </q-card-section>
    </div>
    
    <div v-else class="q-pa-xl text-center">
      <q-icon name="task_alt" size="3em" color="positive" />
      <div class="text-h6 q-mt-md">Frete Concluído!</div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useFreightOrderStore } from 'stores/freight-order-store';
import type { StopPoint } from 'src/models/freight-order-models';

const emit = defineEmits(['close']);
const freightOrderStore = useFreightOrderStore();

const isSubmitting = ref(false);
const endMileage = ref<number | null>(null);

// --- CORREÇÃO: Usa o nome 'activeDriverOrder' da store ---
const order = computed(() => freightOrderStore.activeDriverOrder);
const isLoading = computed(() => freightOrderStore.isLoadingDetails);
const isEnRoute = computed(() => order.value?.status === 'Em Trânsito');

// --- CORREÇÃO: Adiciona o tipo explícito para 's' ---
const nextStop = computed((): StopPoint | null => {
  return order.value?.stop_points.find((s: StopPoint) => s.status === 'Pendente') || null;
});

async function handleStart() {
  if (!order.value || !nextStop.value) return;
  isSubmitting.value = true;
  try {
    await freightOrderStore.startJourneyForStop(order.value.id, nextStop.value.id);
  } finally { isSubmitting.value = false; }
}

async function handleComplete() {
  if (!order.value || !nextStop.value || !endMileage.value) return;
  isSubmitting.value = true;
  try {
    await freightOrderStore.completeStop(order.value.id, nextStop.value.id, endMileage.value);
    endMileage.value = null;
  } finally { isSubmitting.value = false; }
}
</script>