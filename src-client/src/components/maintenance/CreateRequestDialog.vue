<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)">
    <q-card style="width: 500px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h6">Solicitar Manutenção</div>
      </q-card-section>

      <q-form @submit.prevent="handleSubmit">
        <q-card-section class="q-gutter-y-md">
          <q-select
            outlined
            v-model="formData.vehicle_id"
            :options="vehicleOptions"
            label="Veículo *"
            emit-value map-options
            :rules="[val => !!val || 'Selecione um veículo']"
          />
          <q-select
            outlined
            v-model="formData.category"
            :options="categoryOptions"
            label="Categoria do Problema *"
            emit-value map-options
            :rules="[val => !!val || 'Selecione uma categoria']"
          />
          <q-input
            outlined
            v-model="formData.problem_description"
            type="textarea"
            label="Descrição Detalhada do Problema *"
            :rules="[val => !!val || 'Campo obrigatório']"
            autogrow
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn type="submit" unelevated color="primary" label="Enviar Solicitação" :loading="maintenanceStore.isLoading" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { MaintenanceCategory, type MaintenanceRequestCreate } from 'src/models/maintenance-models';

defineProps<{ modelValue: boolean }>();
const emit = defineEmits(['update:modelValue']);

const maintenanceStore = useMaintenanceStore();
const vehicleStore = useVehicleStore();

const formData = ref<MaintenanceRequestCreate>({
  vehicle_id: 0,
  problem_description: '',
  category: MaintenanceCategory.MECHANICAL // Valor padrão
});

const vehicleOptions = computed(() => vehicleStore.vehicles.map(v => ({
  label: `${v.brand} ${v.model} (${v.license_plate})`,
  value: v.id
})));

// Opções para o novo seletor de categoria
const categoryOptions = Object.values(MaintenanceCategory);

async function handleSubmit() {
  try {
    await maintenanceStore.createRequest(formData.value);
    emit('update:modelValue', false);
  } catch {
    // A store já notifica o erro
  }
}
</script>