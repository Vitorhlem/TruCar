<template>
  <q-page class="q-pa-md q-pa-lg-xl">
    
    <div class="row items-center justify-between q-mb-lg q-col-gutter-y-md">
      <div class="col-12 col-md-auto">
        <h1 class="text-h4 text-weight-bolder q-my-none text-primary flex items-center gap-sm">
          <q-icon name="build_circle" size="md" />
          Gestão de Manutenção
        </h1>
        <div class="text-subtitle2 text-grey-7 q-mt-xs" :class="{ 'text-grey-5': $q.dark.isActive }">
          Controle de chamados, preventivas e oficina
        </div>
      </div>

      <div class="col-12 col-md-auto">
        <div class="d-inline-block relative-position">
          <q-btn 
            color="primary" 
            icon="add_circle" 
            label="Abrir Novo Chamado" 
            size="md"
            unelevated 
            class="shadow-2"
            @click="openCreateRequestDialog"
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
                    <div class="text-caption q-mt-xs text-yellow-2 cursor-pointer" @click="showComparisonDialog = true">Clique para aumentar</div>
                </div>
            </div>
          </q-tooltip>
        </div>
      </div>
    </div>

    <div v-if="isDemo" class="q-mb-xl animate-fade">
      <q-card flat bordered class="demo-card-gradient">
        <q-card-section class="q-pa-md">
          <div class="row items-center justify-between">
            <div class="col-grow row items-center q-gutter-x-md">
              <q-circular-progress
                show-value
                font-size="14px"
                :value="usagePercentage"
                size="60px"
                :thickness="0.22"
                :color="usageColor"
                track-color="white"
                class="text-white q-my-xs"
              >
                {{ usagePercentage }}%
              </q-circular-progress>
              
              <div>
                <div class="text-subtitle2 text-uppercase text-white text-opacity-80">Chamados Mensais (Demo)</div>
                <div class="text-h4 text-white text-weight-bold">
                  {{ demoUsageCount }} <span class="text-h6 text-white text-opacity-70">/ {{ demoUsageLimitLabel }}</span>
                </div>
              </div>
            </div>
            
            <div class="col-auto">
               <q-btn flat dense color="white" icon="info" round>
                 <q-tooltip>Você utilizou {{ usagePercentage }}% da sua franquia de chamados de manutenção.</q-tooltip>
               </q-btn>
            </div>
          </div>
          <q-linear-progress :value="usagePercentage / 100" class="q-mt-md rounded-borders" color="white" track-color="white-30" />
        </q-card-section>
      </q-card>
    </div>

    <div class="row q-col-gutter-md q-mb-lg">
      <div class="col-12 col-md-4">
        <q-card flat bordered class="full-height" :class="$q.dark.isActive ? '' : 'bg-white'">
          <q-card-section class="row items-center">
            <div class="col">
              <div class="text-caption text-grey text-uppercase">Chamados Abertos</div>
              <div class="text-h4 text-weight-bold text-orange-8">{{ totalOpen }}</div>
            </div>
            <div class="col-auto">
              <q-avatar color="orange-1" text-color="orange-8" icon="report_problem" size="lg" font-size="28px" />
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-4">
        <q-card flat bordered class="full-height" :class="$q.dark.isActive ? '' : 'bg-white'">
          <q-card-section class="row items-center">
            <div class="col">
              <div class="text-caption text-grey text-uppercase">Em Andamento</div>
              <div class="text-h4 text-weight-bold text-blue-8">{{ totalInProgress }}</div>
            </div>
            <div class="col-auto">
              <q-avatar color="blue-1" text-color="blue-8" icon="engineering" size="lg" font-size="28px" />
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-4">
        <q-card flat bordered class="full-height" :class="$q.dark.isActive ? '' : 'bg-white'">
          <q-card-section class="row items-center">
            <div class="col">
              <div class="text-caption text-grey text-uppercase">Total Finalizado</div>
              <div class="text-h4 text-weight-bold text-green-8">{{ totalCompleted }}</div>
            </div>
            <div class="col-auto">
              <q-avatar color="green-1" text-color="green-8" icon="task_alt" size="lg" font-size="28px" />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-card flat bordered :class="$q.dark.isActive ? '' : 'bg-white'">
      <q-card-section class="q-pb-none">
        <div class="row items-center justify-between q-mb-md">
            <q-tabs 
                v-model="tab" 
                dense 
                class="text-grey" 
                active-color="primary" 
                indicator-color="primary" 
                align="left" 
                narrow-indicator
            >
                <q-tab name="open" label="Fila de Atendimento" icon="format_list_bulleted" />
                <q-tab name="closed" label="Histórico Completo" icon="history" />
            </q-tabs>

            <q-input
                outlined
                dense
                debounce="300"
                v-model="searchTerm"
                placeholder="Buscar chamado..."
                class="search-input"
                :bg-color="$q.dark.isActive ? '' : 'white'"
            >
                <template v-slot:prepend><q-icon name="search" /></template>
            </q-input>
        </div>
        <q-separator />
      </q-card-section>

      <q-card-section class="q-pa-none">
        <q-tab-panels v-model="tab" animated :class="$q.dark.isActive ? '' : 'bg-white'">
          
          <q-tab-panel name="open" class="q-pa-md">
            <div v-if="maintenanceStore.isLoading" class="row q-col-gutter-md">
              <div v-for="n in 4" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
                  <q-card flat bordered><q-skeleton height="180px" square /></q-card>
              </div>
            </div>
            
            <div v-else-if="openRequests.length > 0" class="row q-col-gutter-md">
              <div v-for="req in openRequests" :key="req.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
                <MaintenanceRequestCard :request="req" @click="openDetailsDialog(req)" />
              </div>
            </div>
            
            <div v-else class="text-center q-pa-xl">
              <div class="bg-green-1 q-pa-md rounded-borders inline-block q-mb-md">
                  <q-icon name="check_circle" size="4em" color="green-6" />
              </div>
              <div class="text-h6 text-grey-8">Tudo Certo!</div>
              <p class="text-grey-6">Nenhum chamado aberto pendente de atenção.</p>
            </div>
          </q-tab-panel>

          <q-tab-panel name="closed" class="q-pa-none">
            <div v-if="closedRequests.length === 0 && !maintenanceStore.isLoading" class="text-center q-pa-xl">
              <q-icon name="history" size="4em" color="grey-4" />
              <p class="q-mt-md text-grey-6">Nenhum histórico de manutenções encontrado.</p>
            </div>
            
            <q-list v-else separator>
              <q-item 
                v-for="req in closedRequests" 
                :key="req.id" 
                clickable 
                v-ripple 
                @click="openDetailsDialog(req)"
                class="q-py-md hover-bg"
              >
                <q-item-section avatar>
                    <q-avatar :color="getStatusColor(req.status)" text-color="white" icon="build" size="md" font-size="18px" />
                </q-item-section>
                
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ req.vehicle?.brand }} {{ req.vehicle?.model }}</q-item-label>
                  <q-item-label caption>
                      <span class="text-grey-8">{{ req.vehicle?.license_plate || req.vehicle?.identifier }}</span> &bull; {{ req.problem_description }}
                  </q-item-label>
                </q-item-section>
                
                <q-item-section side>
                  <div class="column items-end">
                      <q-badge :color="getStatusColor(req.status)" :label="req.status" class="q-mb-xs" />
                      <span class="text-caption text-grey-6" v-if="req.created_at">{{ new Date(req.created_at).toLocaleDateString() }}</span>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <MaintenanceDetailsDialog 
      v-model="isDetailsDialogOpen" 
      :request="selectedRequest" 
    />
    
    <CreateRequestDialog 
      v-model="isCreateDialogOpen" 
      @request-created="refreshData" 
    />

    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 750px; max-width: 95vw;" :class="$q.dark.isActive ? '' : 'bg-white'">
        <q-card-section class="bg-primary text-white q-py-lg text-center relative-position overflow-hidden">
          <div class="absolute-full bg-white opacity-10" style="transform: skewY(-5deg) scale(1.5);"></div>
          <q-icon name="handyman" size="4em" class="q-mb-sm" />
          <div class="text-h4 text-weight-bold relative-position">Gestão de Manutenção Profissional</div>
          <div class="text-subtitle1 text-blue-2 relative-position">Reduza custos e tempo de oficina com o Plano PRO</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat :dark="$q.dark.isActive" :class="$q.dark.isActive ? 'bg-transparent' : ''">
            <thead>
              <tr :class="$q.dark.isActive ? 'bg-grey-8' : 'bg-grey-1 text-grey-7'">
                <th class="text-left q-pa-md text-uppercase text-caption">Funcionalidade</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9 border-left">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary bg-blue-1">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="build" color="grey-6" size="xs" /> Chamados Mensais</td>
                <td class="text-center bg-amber-1 text-amber-10">{{ demoUsageLimitLabel }}</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="calendar_month" color="grey-6" size="xs" /> Plano de Preventivas</td>
                <td class="text-center bg-amber-1 text-amber-10">Básico</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Automático</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="inventory" color="grey-6" size="xs" /> Controle de Peças</td>
                <td class="text-center bg-amber-1 text-amber-10">Manual</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1">Integrado ao Estoque</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-1'">
          <div class="column items-center full-width q-gutter-y-md">
            <div class="text-h6 text-weight-bold">Precisa de mais controle sobre a oficina?</div>
            <q-btn color="positive" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width shadow-2" />
            <q-btn flat color="grey-7" label="Continuar no Demo" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useAuthStore } from 'stores/auth-store';
import { useDemoStore } from 'stores/demo-store';
import { MaintenanceStatus, type MaintenanceRequest } from 'src/models/maintenance-models';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import MaintenanceRequestCard from 'components/maintenance/MaintenanceRequestCard.vue';

const $q = useQuasar();
const maintenanceStore = useMaintenanceStore();
const authStore = useAuthStore();
const demoStore = useDemoStore();

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

const usageColor = computed(() => {
  if (usagePercentage.value >= 100) return 'red-4';
  if (usagePercentage.value >= 80) return 'orange-4';
  return 'white';
});
// -------------------

const searchTerm = ref('');
const tab = ref('open');
const isCreateDialogOpen = ref(false);
const isDetailsDialogOpen = ref(false);
const selectedRequest = ref<MaintenanceRequest | null>(null);

const openRequests = computed(() => maintenanceStore.maintenances.filter(r => r.status !== MaintenanceStatus.CONCLUIDA && r.status !== MaintenanceStatus.REJEITADA));
const closedRequests = computed(() => maintenanceStore.maintenances.filter(r => r.status === MaintenanceStatus.CONCLUIDA || r.status === MaintenanceStatus.REJEITADA));

// --- KPIs Calculados ---
const totalOpen = computed(() => openRequests.value.length);
const totalInProgress = computed(() => maintenanceStore.maintenances.filter(r => r.status === MaintenanceStatus.EM_ANDAMENTO).length);
const totalCompleted = computed(() => closedRequests.value.length);

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
      void demoStore.fetchDemoStats(true);
  }
});
</script>

<style scoped lang="scss">
.demo-card-gradient {
  background: linear-gradient(135deg, var(--q-primary) 0%, darken($primary, 20%) 100%);
  border: none;
  border-radius: 12px;
}

.search-input {
  width: 300px;
  @media (max-width: 599px) {
    width: 100%;
  }
}

.white-30 {
  color: rgba(255,255,255,0.3) !important;
}

.opacity-10 {
  opacity: 0.1;
}

.hover-bg {
    transition: background-color 0.2s;
    &:hover {
        background-color: rgba(0,0,0,0.03);
    }
}

.body--dark .hover-bg:hover {
    background-color: rgba(255,255,255,0.05);
}
</style>