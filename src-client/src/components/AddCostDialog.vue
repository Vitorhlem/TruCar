<template>
  <q-card style="width: 500px; max-width: 90vw;" :dark="$q.dark.isActive">
    <q-card-section>
      <div class="text-h6">Adicionar Novo Custo</div>
    </q-card-section>

    <q-form @submit.prevent="handleSubmit">
      <q-card-section class="q-gutter-y-md">
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
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import type { VehicleCostCreate, CostType } from 'src/models/vehicle-cost-models';

const props = defineProps<{
  vehicleId: number;
}>();

const emit = defineEmits(['close']);
const $q = useQuasar();

const costStore = useVehicleCostStore();
const isSubmitting = ref(false);

const costTypeOptions: CostType[] = ['Manutenção', 'Combustível', 'Pedágio', 'Seguro', 'Pneu', 'Outros'];

const formData = ref<VehicleCostCreate>({
  description: '',
  amount: 0,

  date: new Date().toISOString().split('T')[0] || '',
  cost_type: 'Outros',
});

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    await costStore.addCost(props.vehicleId, formData.value);
    emit('close');
  } finally {
    isSubmitting.value = false;
  }
}
</script>