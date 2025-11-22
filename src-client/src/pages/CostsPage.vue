<template>
  <q-page padding>
    
    <div v-if="isDemo" class="q-mb-lg animate-fade">
      <div class="row">
        <div class="col-12">
          <q-card flat bordered class="">
            <q-card-section>
              <div class="row items-center justify-between no-wrap">
                <div class="col">
                  <div class="text-subtitle2 text-uppercase text-grey-8">Controle Financeiro Mensal</div>
                  <div class="text-h4 text-primary text-weight-bold q-mt-sm">
                    {{ demoUsageCount }} <span class="text-h6 text-grey-6">/ {{ demoUsageLimitLabel }} Lançamentos</span>
                  </div>
                  <div class="text-caption text-grey-7 q-mt-sm">
                    <q-icon name="info" />
                    Você utilizou {{ usagePercentage }}% do limite de registros financeiros deste mês.
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
      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">Análise de Custos</h1>
        <div class="text-subtitle1 text-grey-7">Visão geral das despesas da sua frota.</div>
      </div>
      
      <div class="d-inline-block relative-position">
        <q-btn 
          color="primary" 
          icon="attach_money" 
          label="Registrar Despesa" 
          unelevated 
          @click="openAddCostDialog"
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
                  <div class="text-weight-bold">Limite Mensal Atingido</div>
                  <div class="text-caption">Você já realizou {{ demoUsageLimitLabel }} lançamentos este mês.</div>
                  <div class="text-caption q-mt-xs text-yellow-2 cursor-pointer" @click="showComparisonDialog = true">Liberar Acesso CFO</div>
              </div>
          </div>
        </q-tooltip>
      </div>
    </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section class="row q-col-gutter-md items-center">
        <div class="col-12 col-md-4">
          <q-input outlined v-model="dateRangeText" label="Filtrar por Período" readonly dense>
            <template v-slot:prepend>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-date v-model="dateRange" range mask="YYYY-MM-DD" @update:model-value="applyFilters">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Fechar" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </div>
        <div class="col-12 col-md-4">
          <q-select
            outlined
            v-model="categoryFilter"
            :options="costCategoryOptions"
            label="Filtrar por Categoria"
            dense
            clearable
            @update:model-value="applyFilters"
          />
        </div>
      </q-card-section>
    </q-card>

    <q-banner v-if="isDemo && hasOlderData" class="bg-amber-1 text-amber-9 q-mb-md rounded-borders">
      <template v-slot:avatar><q-icon name="history_edu" /></template>
      <div class="text-subtitle2">
        <strong>Análise Histórica Limitada:</strong> Visualizando apenas os últimos 30 dias.
        Dados financeiros antigos são exclusivos da análise de TCO (Custo Total de Propriedade) do Plano PRO.
      </div>
      <template v-slot:action>
        <q-btn flat label="Ver Análise Completa" @click="showComparisonDialog = true" />
      </template>
    </q-banner>

    <div class="row q-col-gutter-lg q-mb-lg">
      <div class="col-12 col-md-8">
        <q-card flat bordered class="full-height relative-position">
          <q-card-section>
            <div class="text-h6">Distribuição de Custos por Categoria</div>
            <div class="text-subtitle2 text-grey">Total: {{ formatCurrency(totalCost) }}</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <CostsPieChart v-if="filteredCosts.length > 0" :costs="filteredCosts" style="height: 300px;" />
            <div v-else class="text-center text-grey q-pa-md">Sem dados para exibir o gráfico.</div>
          </q-card-section>
          
          <div v-if="isDemo && isDateRangeBlocked" class="absolute-full flex flex-center bg-white-blur z-top">
            <div class="text-center">
              <q-icon name="lock" size="xl" color="grey-5" />
              <div class="text-h6 text-grey-8 q-mt-sm">Análise Histórica Bloqueada</div>
              <q-btn outline color="primary" label="Desbloquear TCO" class="q-mt-md" @click="showComparisonDialog = true" />
            </div>
          </div>
        </q-card>
      </div>
      
      <div class="col-12 col-md-4">
        <div class="q-gutter-y-md">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Custo Total (Visível)</div>
              <div class="text-h5 text-weight-bold">{{ formatCurrency(totalCost) }}</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Custo Médio por Lançamento</div>
              <div class="text-h5 text-weight-bold">{{ formatCurrency(averageCost) }}</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Principal Categoria de Custo</div>
              <div class="text-h5 text-weight-bold text-primary">{{ topCostCategory }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <q-card flat bordered>
      <q-table
        title="Todos os Lançamentos de Custos"
        :rows="costsWithVehicleData"
        :columns="columns"
        row-key="id"
        :loading="costStore.isLoading || vehicleStore.isLoading"
        no-data-label="Nenhum custo encontrado para os filtros aplicados."
        flat
        :rows-per-page-options="[10, 25, 50]"
      >
        <template v-slot:body-cell-vehicle="props">
          <q-td :props="props">
            <router-link v-if="props.row.vehicle" :to="`/vehicles/${props.row.vehicle_id}`" class="text-primary" style="text-decoration: none;">
              {{ props.row.vehicle.brand }} {{ props.row.vehicle.model }} ({{ props.row.vehicle.license_plate || props.row.vehicle.identifier }})
            </router-link>
            <span v-else>N/A</span>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isAddCostDialogOpen">
      <AddCostDialog @close="isAddCostDialogOpen = false" @cost-added="refreshData" />
    </q-dialog>

    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 750px; max-width: 95vw;">
        <q-card-section class="bg-primary text-white q-py-lg">
          <div class="text-h5 text-weight-bold text-center">Inteligência Financeira para sua Frota</div>
          <div class="text-subtitle1 text-center text-blue-2">Transforme custos em investimento com o Plano PRO</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat separator="horizontal">
            <thead>
              <tr class="bg-grey-1 text-uppercase text-grey-7">
                <th class="text-left q-pa-md">Recurso</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary">Plano PRO (CFO)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="receipt_long" color="grey-6" size="xs" /> Registros Mensais</td>
                <td class="text-center bg-amber-1 text-amber-10">{{ demoUsageLimitLabel }} lançamentos</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="insights" color="grey-6" size="xs" /> Análise de TCO</td>
                <td class="text-center bg-amber-1 text-amber-10">Últimos 30 dias</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Histórico Completo</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="trending_up" color="grey-6" size="xs" /> Métricas Avançadas</td>
                <td class="text-center bg-amber-1 text-amber-10">Básico</td>
                <td class="text-center text-primary text-weight-bold">Custo/KM, ROI, Depreciação</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg bg-grey-1">
          <div class="text-center full-width">
            <div class="text-grey-7 q-mb-md">Pare de perder dinheiro com manutenção invisível.</div>
            <q-btn color="primary" label="Falar com Consultor Financeiro" size="lg" unelevated icon="whatsapp" class="full-width" />
            <q-btn flat color="grey-7" label="Continuar avaliando" class="q-mt-sm" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { useDemoStore } from 'stores/demo-store';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { useQuasar, type QTableColumn } from 'quasar';
import { format, parseISO } from 'date-fns';
import type { Vehicle } from 'src/models/vehicle-models';
import CostsPieChart from 'components/CostsPieChart.vue';
import AddCostDialog from 'components/AddCostDialog.vue';

const costStore = useVehicleCostStore();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const demoStore = useDemoStore();

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');
const showComparisonDialog = ref(false);
const isAddCostDialogOpen = ref(false);

// Fallback seguro
const demoUsageCount = computed(() => demoStore.stats?.cost_count ?? 0);
const demoUsageLimit = computed(() => 15);
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

const hasOlderData = computed(() => {
    if (!costStore.costs.length) return false;
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return costStore.costs.some(c => c.date && new Date(c.date) < thirtyDaysAgo);
});

const isDateRangeBlocked = computed(() => {
    if (!isDemo.value || !dateRange.value) return false;
    const fromDate = new Date(dateRange.value.from);
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return fromDate < thirtyDaysAgo;
});

const dateRange = ref<{ from: string, to: string } | null>(null);
const categoryFilter = ref<string | null>(null);
const costCategoryOptions = ["Manutenção", "Combustível", "Pedágio", "Seguro", "Pneu", "Peças e Componentes", "Outros"];
const usageColor = computed(() => {
  if (usagePercentage.value >= 100) return 'negative';
  if (usagePercentage.value >= 80) return 'warning';
  return 'primary';
});
const vehicleMap = computed(() => {
  const map = new Map<number, Vehicle>();
  if (vehicleStore.vehicles && Array.isArray(vehicleStore.vehicles)) {
    for (const vehicle of vehicleStore.vehicles) {
      map.set(vehicle.id, vehicle);
    }
  }
  return map;
});

const filteredCosts = computed(() => {
  let costs = costStore.costs || [];

  if (categoryFilter.value) {
    costs = costs.filter(cost => cost.cost_type === categoryFilter.value);
  }

  if (isDemo.value) {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      costs = costs.filter(cost => cost.date && new Date(cost.date) >= thirtyDaysAgo);
  }

  return costs;
});

const costsWithVehicleData = computed(() => {
  return filteredCosts.value.map(cost => {
    return {
      ...cost, 
      vehicle: vehicleMap.value.get(cost.vehicle_id)
    };
  });
});

const totalCost = computed(() => filteredCosts.value.reduce((sum, cost) => sum + (cost.amount || 0), 0));
const averageCost = computed(() => {
    const len = filteredCosts.value.length;
    return len > 0 ? totalCost.value / len : 0;
});

const topCostCategory = computed(() => {
  if (filteredCosts.value.length === 0) return 'N/A';
  const costsByCategory: Record<string, number> = {};
  for (const cost of filteredCosts.value) {
    costsByCategory[cost.cost_type] = (costsByCategory[cost.cost_type] || 0) + (cost.amount || 0);
  }
  const sortedCategories = Object.entries(costsByCategory).sort((a, b) => b[1] - a[1]);
  return sortedCategories.length > 0 && sortedCategories[0] ? sortedCategories[0][0] : 'N/A';
});

const dateRangeText = computed(() => {
  if (dateRange.value) {
    try {
      const from = format(parseISO(dateRange.value.from), 'dd/MM/yyyy');
      const to = format(parseISO(dateRange.value.to), 'dd/MM/yyyy');
      return `${from} - ${to}`;
    } catch {
      return 'Período Inválido';
    }
  }
  return 'Todo o período';
});

function formatCurrency(value: number | undefined | null) {
    return (value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

const columns: QTableColumn[] = [
  { 
    name: 'date', label: 'Data', field: 'date', align: 'left', sortable: true,
    format: (val) => val ? format(parseISO(val), 'dd/MM/yyyy') : '---' 
  },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left', style: 'max-width: 300px; white-space: normal;' },
  { name: 'cost_type', label: 'Categoria', field: 'cost_type', align: 'center', sortable: true },
  { name: 'vehicle', label: 'Veículo', field: 'vehicle_id', align: 'left', sortable: true },
  { 
    name: 'amount', label: 'Valor', field: 'amount', align: 'right', sortable: true,
    format: (val) => formatCurrency(val) 
  },
];

function applyFilters() {
  const params = {
    startDate: dateRange.value ? new Date(dateRange.value.from) : null,
    endDate: dateRange.value ? new Date(dateRange.value.to) : null,
  };
  void costStore.fetchAllCosts(params);
}

function openAddCostDialog() {
    if (isLimitReached.value) {
        showComparisonDialog.value = true;
        return;
    }
    isAddCostDialogOpen.value = true;
}

function refreshData() {
    applyFilters();
    if (authStore.isDemo) {
        void demoStore.fetchDemoStats(true);
    }
}

onMounted(() => {
  applyFilters();
  void vehicleStore.fetchAllVehicles({ page: 1, rowsPerPage: 9999 });
  if (authStore.isDemo) {
      void demoStore.fetchDemoStats();
  }
});
</script>

<style scoped>
.bg-white-blur {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
}
</style>