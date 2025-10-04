<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)" >
    <q-card style="width: 500px; max-width: 90vw;" v-if="part">
      <q-form @submit.prevent="handleSubmit">
        <q-card-section>
          <div class="text-h6">{{ part.name }}</div>
          <div class="text-subtitle2">Gerenciar Estoque (Atual: {{ part.stock }})</div>
        </q-card-section>

        <q-card-section class="q-gutter-y-md">
          <q-select outlined v-model="formData.transaction_type" :options="transactionOptions" label="Tipo de Movimentação *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model.number="formData.quantity" type="number" label="Quantidade *" :rules="[val => val > 0 || 'Deve ser maior que zero']" />
          
          <q-select v-if="formData.transaction_type === 'Saída para Uso'" outlined v-model="formData.related_vehicle_id" :options="vehicleOptions" label="Atribuir ao Veículo (Opcional)" emit-value map-options clearable use-input @filter="filterVehicles" />

          <q-input outlined v-model="formData.notes" type="textarea" label="Notas / Motivo (Opcional)" autogrow />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn type="submit" unelevated color="primary" label="Confirmar Movimentação" :loading="partStore.isLoading || componentStore.isLoading" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { usePartStore } from 'stores/part-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store'; // <-- IMPORTAR
import type { Part } from 'src/models/part-models';
import type { TransactionCreate, TransactionType } from 'src/models/inventory-transaction-models';
import { Notify } from 'quasar';

const props = defineProps<{ modelValue: boolean, part: Part | null }>();
const emit = defineEmits(['update:modelValue']);

const partStore = usePartStore();
const vehicleStore = useVehicleStore();
const componentStore = useVehicleComponentStore(); // <-- USAR A STORE

const transactionOptions: TransactionType[] = ["Entrada", "Saída para Uso", "Fim de Vida", "Retorno", "Ajuste Manual"];
const formData = ref<Partial<TransactionCreate>>({});

const vehicleOptions = ref<{label: string, value: number}[]>([]);

// Carrega os veículos quando o diálogo abre
watch(() => props.modelValue, (isOpening) => {
  if (isOpening) {
    formData.value = { quantity: 1 };
    void vehicleStore.fetchAllVehicles({rowsPerPage: 9999});
  }
});

// Filtro para a lista de veículos
function filterVehicles (val: string, update: (callbackFn: () => void) => void) {
  update(() => {
    if (val === '') {
      vehicleOptions.value = vehicleStore.vehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id }));
    } else {
      const needle = val.toLowerCase();
      vehicleOptions.value = vehicleStore.vehicles
        .filter(v => JSON.stringify(v).toLowerCase().includes(needle))
        .map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id }));
    }
  });
}


async function handleSubmit() {
  if (!props.part) return;

  let success = false;

  // Cenário 1: Instalação em um veículo. Usa a store de componentes.
  if (formData.value.transaction_type === 'Saída para Uso' && formData.value.related_vehicle_id) {
    if (props.part.stock < (formData.value.quantity ?? 1)) {
        Notify.create({ type: 'negative', message: 'Estoque insuficiente para esta operação.' });
        return;
    }
    success = await componentStore.installComponent(formData.value.related_vehicle_id, {
        part_id: props.part.id,
        quantity: formData.value.quantity ?? 1,
    });
    
    // Se a instalação for bem-sucedida, a store de componentes já busca seus próprios dados.
    // Agora, também mandamos a partStore buscar os dados dela, garantindo a reatividade.
    if (success) {
      await partStore.fetchParts();
    }
  } else {
    // Cenário 2: TODAS as outras transações de estoque.
    // Usam a mesma ação centralizada na partStore.
    success = await partStore.addTransaction(props.part.id, formData.value as TransactionCreate);
  }

  // Se qualquer uma das operações tiver sucesso, fecha o diálogo.
  if (success) {
    emit('update:modelValue', false);
  }
}
</script>