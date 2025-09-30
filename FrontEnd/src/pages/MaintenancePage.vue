<template>
  <q-page class="q-pa-md">
    <div class="row items-start q-col-gutter-md">
      <div class="col-12 col-md-4">
        <div class="flex items-center justify-between q-mb-md">
          <h1 class="text-h5 text-weight-bold q-my-none">Manutenções</h1>
          <q-btn
            @click="openCreateRequestDialog"
            color="primary"
            icon="add"
            label="Novo Pedido"
            unelevated
          />
        </div>

        <q-input
          v-model="searchTerm"
          dense
          outlined
          placeholder="Procurar por título ou veículo..."
          class="q-mb-md"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>

        <q-list bordered separator>
          <q-item-label header>Pedidos Abertos</q-item-label>
          <MaintenanceRequestCard
            v-for="request in openRequests"
            :key="request.id"
            :request="request"
            :is-selected="selectedRequestId === request.id"
            @click="selectRequest(request.id)"
          />
          <q-item v-if="openRequests.length === 0" class="text-grey">
            <q-item-section>Nenhum pedido de manutenção aberto.</q-item-section>
          </q-item>

          <q-separator spaced />

          <q-item-label header>Pedidos Fechados</q-item-label>
          <MaintenanceRequestCard
            v-for="request in closedRequests"
            :key="request.id"
            :request="request"
            :is-selected="selectedRequestId === request.id"
            @click="selectRequest(request.id)"
          />
           <q-item v-if="closedRequests.length === 0" class="text-grey">
            <q-item-section>Nenhum pedido de manutenção fechado.</q-item-section>
          </q-item>
        </q-list>
      </div>

      <div class="col-12 col-md-8">
        <q-card flat bordered class="flex flex-center text-center text-grey" style="height: 100%;">
          <div>
            <q-icon name="inbox" size="lg" />
            <p>Selecione um pedido na lista para ver os detalhes.</p>
          </div>
        </q-card>
      </div>
    </div>

    <CreateRequestDialog v-model="isCreateDialogOpen" />
    
    <!-- O diálogo de detalhes agora é chamado aqui e controlado pelo v-model -->
    <MaintenanceDetailsDialog v-model="isDetailsDialogOpen" :request="selectedRequest" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { MaintenanceStatus, type MaintenanceRequest } from 'src/models/maintenance-models';
import MaintenanceRequestCard from 'components/maintenance/MaintenanceRequestCard.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';

const maintenanceStore = useMaintenanceStore();
const searchTerm = ref('');
const isCreateDialogOpen = ref(false);
const isDetailsDialogOpen = ref(false); // Variável para controlar o diálogo de detalhes

const selectedRequestId = ref<number | null>(null);

function selectRequest(id: number) {
  selectedRequestId.value = id;
  isDetailsDialogOpen.value = true; // Abre o diálogo ao selecionar um item
}

const selectedRequest = computed(() => {
  if (!selectedRequestId.value) return null;
  return maintenanceStore.maintenances.find((r: MaintenanceRequest) => r.id === selectedRequestId.value) || null;
});

const openRequests = computed(() => maintenanceStore.maintenances.filter((r: MaintenanceRequest) => r.status !== MaintenanceStatus.COMPLETED && r.status !== MaintenanceStatus.REJECTED));
const closedRequests = computed(() => maintenanceStore.maintenances.filter((r: MaintenanceRequest) => r.status === MaintenanceStatus.COMPLETED || r.status === MaintenanceStatus.REJECTED));

function openCreateRequestDialog() {
  isCreateDialogOpen.value = true;
}

watch(searchTerm, (newValue) => {
  void maintenanceStore.fetchMaintenanceRequests({search: newValue});
});

onMounted(() => {
  void maintenanceStore.fetchMaintenanceRequests();
});
</script>
