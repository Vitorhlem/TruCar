<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)">
    <q-card style="width: 500px; max-width: 90vw;" v-if="part">
      <q-form @submit.prevent="handleSubmit">
        <q-card-section>
          <div class="text-h6">{{ part.name }}</div>
          <div class="text-subtitle2">Gerenciar Estoque</div>
        </q-card-section>

        <q-card-section class="q-gutter-y-md">
          <q-select outlined v-model="formData.transaction_type" :options="transactionOptions" label="Tipo de Movimentação *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model.number="formData.quantity" type="number" label="Quantidade *" :rules="[val => val > 0 || 'Deve ser maior que zero']" />
          
          <q-select v-if="formData.transaction_type === 'Saída para Uso'" outlined v-model="formData.related_vehicle_id" :options="vehicleOptions" label="Atribuir ao Veículo (Opcional)" emit-value map-options clearable />
          <q-select v-if="formData.transaction_type === 'Saída para Uso'" outlined v-model="formData.related_user_id" :options="driverOptions" label="Atribuir ao Motorista (Opcional)" emit-value map-options clearable />

          <q-input outlined v-model="formData.notes" type="textarea" label="Notas / Motivo (Opcional)" autogrow />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn type="submit" unelevated color="primary" label="Confirmar Movimentação" :loading="partStore.isLoading" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
// --- CORREÇÃO 1: 'onMounted' foi removido da importação ---
import { ref, computed, watch } from 'vue';
import { usePartStore } from 'stores/part-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useUserStore } from 'stores/user-store';
import type { Part } from 'src/models/part-models';
import type { TransactionCreate, TransactionType } from 'src/models/inventory-transaction-models';

const props = defineProps<{ modelValue: boolean, part: Part | null }>();
const emit = defineEmits(['update:modelValue']);

const partStore = usePartStore();
const vehicleStore = useVehicleStore();
const userStore = useUserStore();

const transactionOptions: TransactionType[] = ["Entrada", "Saída para Uso", "Fim de Vida", "Retorno", "Ajuste Manual"];
const formData = ref<Partial<TransactionCreate>>({});

const vehicleOptions = computed(() => vehicleStore.vehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id })));
const driverOptions = computed(() => userStore.users.filter(u => u.role === 'driver').map(d => ({ label: d.full_name, value: d.id })));

watch(() => props.modelValue, (isOpening) => {
  if (isOpening) {
    formData.value = { quantity: 1 };
    // --- CORREÇÃO 2: Adicionado 'void' para suprimir os avisos do linter ---
    if (vehicleStore.vehicles.length === 0) void vehicleStore.fetchAllVehicles({rowsPerPage: 500});
    if (userStore.users.length === 0) void userStore.fetchAllUsers();
  }
});

async function handleSubmit() {
  if (!props.part) return;
  const success = await partStore.addTransaction(props.part.id, formData.value as TransactionCreate);
  if (success) {
    emit('update:modelValue', false);
  }
}
</script>