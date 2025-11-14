<template>
  <q-card flat bordered class="column no-wrap cursor-pointer q-hoverable" @click="emit('click')">
    <span class="q-focus-helper"></span>
    <q-card-section>
      <div class="row items-center no-wrap">
        <div class="col">
          <div class="text-caption text-grey-8">Chamado #{{ request.id }} • {{ request.category }}</div>
          <div class="text-subtitle1 text-weight-bold ellipsis">{{ request.vehicle?.brand }} {{ request.vehicle?.model }}</div>
        </div>
        <q-badge :color="getStatusColor(request.status)" text-color="white" class="q-pa-xs text-body2">
          {{ request.status }}
        </q-badge>
      </div>
    </q-card-section>

    <q-card-section class="q-pt-none" style="flex-grow: 1;">
      <div class="text-caption ellipsis-3-lines">{{ request.problem_description }}</div>
    </q-card-section>

    <q-separator />

    <q-card-section class="row justify-between items-center q-pa-sm text-caption text-grey-7">
      <div>{{ request.reporter?.full_name }}</div>
      <div>{{ new Date(request.created_at).toLocaleDateString('pt-BR') }}</div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { MaintenanceStatus, type MaintenanceRequest } from 'src/models/maintenance-models';

defineProps<{ request: MaintenanceRequest }>();
const emit = defineEmits(['click']);

function getStatusColor(status: MaintenanceStatus) {
  const colorMap: Record<MaintenanceStatus, string> = {
    [MaintenanceStatus.PENDENTE]: 'orange',
    [MaintenanceStatus.APROVADA]: 'primary',
    [MaintenanceStatus.REJEITADA]: 'negative',
    [MaintenanceStatus.EM_ANDAMENTO]: 'info',
    [MaintenanceStatus.CONCLUIDA]: 'positive',
  };
  return colorMap[status];
}
</script>

<style lang="scss" scoped>
.ellipsis-3-lines {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  min-height: 48px;
}
</style>