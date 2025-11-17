<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Chamados de Manutenção</h1>
      <q-btn
        @click="openCreateRequestDialog" color="primary"
        icon="add_circle"
        label="Abrir Novo Chamado"
        unelevated
      />
    </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <q-input
          outlined
          dense
          debounce="300"
          v-model="searchTerm"
          placeholder="Buscar por ID, veículo, solicitante, problema..."
        >
          <template v-slot:append><q-icon name="search" /></template>
        </q-input>
      </q-card-section>
    </q-card>

    <q-tabs v-model="tab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify" narrow-indicator>
      <q-tab name="open" label="Chamados Abertos" />
      <q-tab name="closed" label="Histórico (Finalizados)" />
    </q-tabs>
    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="open">
        <div v-if="maintenanceStore.isLoading" class="row q-col-gutter-md">
          <div v-for="n in 4" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3"><q-card flat bordered><q-skeleton height="150px" square /></q-card></div>
        </div>
        <div v-else-if="openRequests.length > 0" class="row q-col-gutter-md">
          <div v-for="req in openRequests" :key="req.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
            <MaintenanceRequestCard :request="req" @click="openDetailsDialog(req)" />
          </div>
        </div>
        <div v-else class="text-center q-pa-xl text-grey-2">
          <q-icon name="check_circle_outline" size="4em" />
          <p class="q-mt-md">Nenhum chamado aberto no momento.</p>
        </div>
      </q-tab-panel>

      <q-tab-panel name="closed">
        <div v-if="closedRequests.length === 0 && !maintenanceStore.isLoading" class="text-center q-pa-xl text-grey-7">
          <q-icon name="inbox" size="4em" />
          <p class="q-mt-md">Nenhum chamado finalizado no histórico.</p>
        </div>
        <q-list v-else bordered separator>
          <q-item v-for="req in closedRequests" :key="req.id" clickable v-ripple @click="openDetailsDialog(req)">
            <q-item-section>
              <q-item-label>{{ req.vehicle?.brand }} {{ req.vehicle?.model }} ({{ req.vehicle?.license_plate || req.vehicle?.identifier }})</q-item-label>
              <q-item-label caption>{{ req.problem_description }}</q-item-label>
            </q-item-section>
            <q-item-section side top>
              <q-badge :color="getStatusColor(req.status)" :label="req.status" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-tab-panel>
    </q-tab-panels>

    <MaintenanceDetailsDialog v
      v-model="isDetailsDialogOpen" 
      :request="selectedRequest" 
    />
    <CreateRequestDialog v-model="isCreateDialogOpen" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { MaintenanceStatus, type MaintenanceRequest } from 'src/models/maintenance-models';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';

import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';

import MaintenanceRequestCard from 'components/maintenance/MaintenanceRequestCard.vue';

const maintenanceStore = useMaintenanceStore();

const searchTerm = ref('');
const tab = ref('open');
const isCreateDialogOpen = ref(false);
const isDetailsDialogOpen = ref(false);
const selectedRequest = ref<MaintenanceRequest | null>(null);

const openRequests = computed(() => maintenanceStore.maintenances.filter(r => r.status !== MaintenanceStatus.CONCLUIDA && r.status !== MaintenanceStatus.REJEITADA));
const closedRequests = computed(() => maintenanceStore.maintenances.filter(r => r.status === MaintenanceStatus.CONCLUIDA || r.status === MaintenanceStatus.REJEITADA));

function openCreateRequestDialog() {
  isCreateDialogOpen.value = true;
}

function openDetailsDialog(request: MaintenanceRequest) {
  selectedRequest.value = request;
  isDetailsDialogOpen.value = true;
}

function getStatusColor(status: MaintenanceStatus): string {
  const colorMap: Record<MaintenanceStatus, string> = {
    [MaintenanceStatus.PENDENTE]: 'orange',
    [MaintenanceStatus.APROVADA]: 'primary',
    [MaintenanceStatus.REJEITADA]: 'negative',
    [MaintenanceStatus.EM_ANDAMENTO]: 'info',
    [MaintenanceStatus.CONCLUIDA]: 'positive',
  };
  return colorMap[status] || 'grey';
}

watch(searchTerm, (newValue) => {
  void maintenanceStore.fetchMaintenanceRequests({ search: newValue });
});

onMounted(() => {
  void maintenanceStore.fetchMaintenanceRequests();
});
</script>