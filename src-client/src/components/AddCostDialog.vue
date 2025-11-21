<template>
  <q-card style="width: 500px; max-width: 90vw;" :dark="$q.dark.isActive">
    <q-card-section>
      <div class="text-h6">Adicionar Novo Custo</div>
    </q-card-section>

    <q-form @submit.prevent="handleSubmit">
      <q-card-section class="q-gutter-y-md">
        
        <q-select
          v-if="!vehicleId"
          outlined
          v-model="localVehicleId"
          :options="vehicleOptions"
          label="Selecione o Veículo *"
          emit-value
          map-options
          :rules="[val => !!val || 'Selecione um veículo']"
          :loading="isLoadingVehicles"
        />

        <q-select
          outlined
          v-model="formData.cost_type"
          :options="costTypeOptions"
          label="Tipo de Custo *"
          :rules="[val => !!val || 'Campo obrigatório']"
        />
        <q-input
          outlined
          v-model="formData.description"
          label="Descrição *"
          :rules="[val => !!val || 'Campo obrigatório']"
        />
        <q-input
          outlined
          v-model.number="formData.amount"
          type="number"
          label="Valor (R$) *"
          prefix="R$"
          :step="0.01"
          :rules="[val => val > 0 || 'O valor deve ser maior que zero']"
        />
        <q-input
          outlined
          v-model="formData.date"
          type="date"
          stack-label
          label="Data do Custo *"
          :rules="[val => !!val || 'Campo obrigatório']"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancelar" v-close-popup />
        <q-btn
          type="submit"
          unelevated
          color="primary"
          label="Adicionar Custo"
          :loading="isSubmitting"
        />
      </q-card-actions>
    </q-form>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleStore } from 'stores/vehicle-store'; // Store de veículos
import type { VehicleCostCreate, CostType } from 'src/models/vehicle-cost-models';

// Tornamos o vehicleId opcional (?)
const props = defineProps<{
  vehicleId?: number;
}>();

const emit = defineEmits(['close', 'cost-added']);
const $q = useQuasar();

const costStore = useVehicleCostStore();
const vehicleStore = useVehicleStore();

const isSubmitting = ref(false);
const isLoadingVehicles = ref(false);
const localVehicleId = ref<number | null>(null); // Para o select

// Opções para o select de veículos
const vehicleOptions = computed(() => 
  vehicleStore.vehicles.map(v => ({
    label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`,
    value: v.id
  }))
);

const costTypeOptions: CostType[] = ['Manutenção', 'Combustível', 'Pedágio', 'Seguro', 'Pneu', 'Outros'];

const formData = ref<VehicleCostCreate>({
  description: '',
  amount: 0,
  date: new Date().toISOString().split('T')[0] || '',
  cost_type: 'Outros',
});

onMounted(async () => {
  // Se não veio ID pela prop, precisamos carregar a lista de veículos
  if (!props.vehicleId) {
    isLoadingVehicles.value = true;
    await vehicleStore.fetchAllVehicles({ page: 1, rowsPerPage: 1000 }); // Pega todos
    isLoadingVehicles.value = false;
  }
});

async function handleSubmit() {
  const targetVehicleId = props.vehicleId || localVehicleId.value;

  if (!targetVehicleId) {
    $q.notify({ type: 'warning', message: 'Selecione um veículo.' });
    return;
  }

  isSubmitting.value = true;
  try {
    await costStore.addCost(targetVehicleId, formData.value);
    $q.notify({ type: 'positive', message: 'Custo registrado com sucesso!' });
    emit('cost-added');
    emit('close'); // Fecha o diálogo
  } catch (error) {
    console.error(error);
    $q.notify({ type: 'negative', message: 'Erro ao registrar custo.' });
  } finally {
    isSubmitting.value = false;
  }
}
</script>