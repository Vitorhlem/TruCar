<template>
  <q-card style="width: 500px; max-width: 90vw;">
    <q-toolbar v-if="order" class="bg-primary text-white">
      <q-toolbar-title class="ellipsis">{{ order.description || 'Detalhes do Frete' }}</q-toolbar-title>
      <q-btn flat round dense icon="close" @click="$emit('close')" />
    </q-toolbar>


    <q-card-section v-if="order">
      <div class="text-overline">Cliente</div>
      <div class="text-body1 q-mb-md">{{ order.client.name }}</div>

      <div class="text-overline">Rota</div>
      <q-timeline color="secondary" layout="dense">
        <q-timeline-entry
          v-for="stop in order.stop_points"
          :key="stop.id"
          :title="`${stop.type}: ${stop.address}`"
          :icon="stop.type === 'Coleta' ? 'archive' : 'unarchive'"
        />
      </q-timeline>
    </q-card-section>
    
    <q-separator />

    <q-card-section>
      <div class="text-h6 q-mb-sm">Atribuir a Mim</div>
      <q-form @submit.prevent="handleClaim">
        <q-select
          outlined
          v-model="selectedVehicleId"
          :options="vehicleOptions"
          label="Selecione um veículo disponível *"
          emit-value map-options
          :rules="[val => !!val || 'É necessário selecionar um veículo']"
          :loading="vehicleStore.isLoading"
        />
        <q-btn
          type="submit"
          label="Confirmar e Pegar Frete"
          color="primary"
          unelevated
          class="full-width q-mt-md"
          :loading="isSubmitting"
        />
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useFreightOrderStore } from 'stores/freight-order-store';
import { useVehicleStore } from 'stores/vehicle-store';
import type { FreightOrder, FreightOrderClaim } from 'src/models/freight-order-models';

const props = defineProps<{
  order: FreightOrder;
}>();

const emit = defineEmits(['close']);

const freightOrderStore = useFreightOrderStore();
const vehicleStore = useVehicleStore();

const isSubmitting = ref(false);
const selectedVehicleId = ref<number | null>(null);

const vehicleOptions = computed(() =>
  vehicleStore.availableVehicles.map(v => ({
    label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`,
    value: v.id
  }))
);

async function handleClaim() {
  if (!selectedVehicleId.value) return;
  isSubmitting.value = true;
  try {
    const payload: FreightOrderClaim = { vehicle_id: selectedVehicleId.value };
    await freightOrderStore.claimFreightOrder(props.order.id, payload);
    emit('close');
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  void vehicleStore.fetchAllVehicles();
});
</script>