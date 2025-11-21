<template>
  <q-page padding>
    
    <div v-if="isDemo" class="q-mb-lg animate-fade">
      <div class="row">
        <div class="col-12">
          <q-card flat bordered class="">
            <q-card-section>
              <div class="row items-center justify-between no-wrap">
                <div class="col">
                  <div class="text-subtitle2 text-uppercase text-grey-8">Chamados Mensais</div>
                  <div class="text-h4 text-primary text-weight-bold q-mt-sm">
                    {{ demoUsageCount }} <span class="text-h6 text-grey-6">/ {{ demoUsageLimitLabel }}</span>
                  </div>
                  <div class="text-caption text-grey-7 q-mt-sm">
                    <q-icon name="info" />
                    Você utilizou {{ usagePercentage }}% da sua franquia de chamados de manutenção.
                  </div>
                </div>
                <div class="col-auto q-ml-md">
                  <q-circular-progress
                    show-value
                    font-size="16px"
                    :value="usagePercentage"
                    size="70px"
                    :thickness="0.22"
                    :color="usageColor"
                    track-color="grey-3"
                  >
                    {{ usagePercentage }}%
                  </q-circular-progress>
                </div>
              </div>
              <q-linear-progress :value="usagePercentage / 100" class="q-mt-md" :color="usageColor" rounded />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Chamados de Manutenção</h1>
      
      <div class="d-inline-block relative-position">
        <q-btn
          @click="openCreateRequestDialog" 
          color="primary"
          icon="add_circle"
          label="Abrir Novo Chamado"
          unelevated
          :disable="isLimitReached"
        />
        <q-tooltip 
          v-if="isLimitReached" 
          class="bg-negative text-body2 shadow-4" 
          anchor="bottom middle" 
          self="top middle"
          :offset="[10, 10]"
        >
          <div class="row items-center no-wrap">
              <q-icon name="lock" size="sm" class="q-mr-sm" />
              <div>
                  <div class="text-weight-bold">Limite Atingido</div>
                  <div class="text-caption">O plano Demo permite até {{ demoUsageLimitLabel }} chamados/mês.</div>
                  <div class="text-caption q-mt-xs text-yellow-2 cursor-pointer" @click="showComparisonDialog = true">Clique para saber mais</div>
              </div>
          </div>
        </q-tooltip>
      </div>
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

    <MaintenanceDetailsDialog 
      v-model="isDetailsDialogOpen" 
      :request="selectedRequest" 
    />
    
    <CreateRequestDialog 
      v-model="isCreateDialogOpen" 
      @request-created="refreshData" 
    />

    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 700px; max-width: 95vw;">
        <q-card-section class="bg-primary text-white q-py-lg">
          <div class="text-h5 text-weight-bold text-center">Gestão de Manutenção Profissional</div>
          <div class="text-subtitle1 text-center text-blue-2">Reduza custos com o Plano PRO</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat separator="horizontal">
            <thead>
              <tr class="bg-grey-1 text-uppercase text-grey-7">
                <th class="text-left q-pa-md">Funcionalidade</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="build" color="grey-6" size="xs" /> Chamados Mensais</td>
                <td class="text-center bg-amber-1 text-amber-10">{{ demoUsageLimitLabel }}</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="calendar_month" color="grey-6" size="xs" /> Plano de Preventivas</td>
                <td class="text-center bg-amber-1 text-amber-10">Básico</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Automático</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="inventory" color="grey-6" size="xs" /> Controle de Peças</td>
                <td class="text-center bg-amber-1 text-amber-10">Manual</td>
                <td class="text-center text-primary text-weight-bold">Integrado ao Estoque</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg bg-grey-1">
          <div class="text-center full-width">
            <div class="text-grey-7 q-mb-md">Precisa de mais controle sobre a oficina?</div>
            <q-btn color="primary" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width" />
            <q-btn flat color="grey-7" label="Continuar no Demo" class="q-mt-sm" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useAuthStore } from 'stores/auth-store';
import { useDemoStore } from 'stores/demo-store';
import { MaintenanceStatus, type MaintenanceRequest } from 'src/models/maintenance-models';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import MaintenanceRequestCard from 'components/maintenance/MaintenanceRequestCard.vue';

const maintenanceStore = useMaintenanceStore();
const authStore = useAuthStore();
const demoStore = useDemoStore();
const usageColor = computed(() => {
  if (usagePercentage.value >= 100) return 'negative';
  if (usagePercentage.value >= 80) return 'warning';
  return 'primary';
});

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');
const showComparisonDialog = ref(false);

// --- LÓGICA DEMO ---
const demoUsageCount = computed(() => demoStore.stats?.maintenance_count ?? 0);
const demoUsageLimit = computed(() => 5);
const demoUsageLimitLabel = computed(() => demoUsageLimit.value.toString());

const isLimitReached = computed(() => {
  if (!isDemo.value) return false;
  return demoUsageCount.value >= demoUsageLimit.value;
});

const usagePercentage = computed(() => {
  if (!isDemo.value || demoUsageLimit.value <= 0) return 0;
  const pct = Math.round((demoUsageCount.value / demoUsageLimit.value) * 100);
  return Math.min(pct, 100);
});
// -------------------

const searchTerm = ref('');
const tab = ref('open');
const isCreateDialogOpen = ref(false);
const isDetailsDialogOpen = ref(false);
const selectedRequest = ref<MaintenanceRequest | null>(null);

const openRequests = computed(() => maintenanceStore.maintenances.filter(r => r.status !== MaintenanceStatus.CONCLUIDA && r.status !== MaintenanceStatus.REJEITADA));
const closedRequests = computed(() => maintenanceStore.maintenances.filter(r => r.status === MaintenanceStatus.CONCLUIDA || r.status === MaintenanceStatus.REJEITADA));

function openCreateRequestDialog() {
  if (isLimitReached.value) {
      showComparisonDialog.value = true;
      return;
  }
  isCreateDialogOpen.value = true;
}

function openDetailsDialog(request: MaintenanceRequest) {
  selectedRequest.value = request;
  isDetailsDialogOpen.value = true;
}

function refreshData() {
    isCreateDialogOpen.value = false;
    void maintenanceStore.fetchMaintenanceRequests();
    if (authStore.isDemo) {
        void demoStore.fetchDemoStats(true);
    }
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
  if (authStore.isDemo) {
      // CORREÇÃO: Passar 'true' para forçar o refresh
      void demoStore.fetchDemoStats(true);
  }
});
</script>