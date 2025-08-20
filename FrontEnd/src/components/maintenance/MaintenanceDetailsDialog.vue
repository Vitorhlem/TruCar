<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)" full-height position="right">
    <q-card style="width: 500px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h6">Detalhes do Chamado #{{ request?.id }}</div>
      </q-card-section>
      <q-separator />

      <q-card-section v-if="request" class="q-pt-none">
        <q-list bordered separator>
          <q-item><q-item-section><q-item-label caption>Solicitante</q-item-label><q-item-label>{{ request.reporter.full_name }}</q-item-label></q-item-section></q-item>
          <q-item><q-item-section><q-item-label caption>Veículo</q-item-label><q-item-label>{{ request.vehicle.brand }} {{ request.vehicle.model }} ({{ request.vehicle.license_plate }})</q-item-label></q-item-section></q-item>
           <q-item><q-item-section><q-item-label caption>Problema Reportado</q-item-label><q-item-label class="text-body2" style="white-space: pre-wrap;">{{ request.problem_description }}</q-item-label></q-item-section></q-item>
        </q-list>
      </q-card-section>
      
      <q-card-section v-if="authStore.isManager">
        <div class="text-subtitle1 q-mb-sm">Ação do Gestor</div>
        <q-input v-model="managerNotes" type="textarea" outlined label="Adicionar uma mensagem para o motorista (opcional)" />
      </q-card-section>
      
      <q-card-actions v-if="authStore.isManager" align="right">
        <q-btn flat label="Cancelar" v-close-popup />
        <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.REJECTED)" color="negative" label="Rejeitar" />
        <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.IN_PROGRESS)" color="info" label="Em Andamento" />
        <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.COMPLETED)" color="positive" label="Concluída" />
        <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.APPROVED)" color="primary" label="Aprovar" unelevated />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useAuthStore } from 'stores/auth-store';
import { MaintenanceStatus, type MaintenanceRequest, type MaintenanceRequestUpdate } from 'src/models/maintenance-models';

const props = defineProps<{
  modelValue: boolean,
  request: MaintenanceRequest | null
}>();
const emit = defineEmits(['update:modelValue']);

const maintenanceStore = useMaintenanceStore();
const authStore = useAuthStore();
const managerNotes = ref('');

watch(() => props.request, (newVal) => {
  managerNotes.value = newVal?.manager_notes || '';
});

async function handleUpdateStatus(newStatus: MaintenanceStatus) {
  if (!props.request) return;

  const payload: MaintenanceRequestUpdate = {
    status: newStatus,
    manager_notes: managerNotes.value
  };

  try {
    await maintenanceStore.updateRequest(props.request.id, payload);
    emit('update:modelValue', false);
  } catch {
    // A store já notifica o erro
  }
}
</script>