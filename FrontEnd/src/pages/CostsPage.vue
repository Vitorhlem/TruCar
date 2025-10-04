<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">Análise de Custos</h1>
        <div class="text-subtitle1 text-grey-7">Visão geral das despesas da sua frota.</div>
      </div>
      </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section class="row q-col-gutter-md items-center">
        <div class="col-12 col-md-4">
          <q-input outlined v-model="dateRangeText" label="Filtrar por Período" readonly dense>
            <template v-slot:prepend><q-icon name="event" class="cursor-pointer" /></template>
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <q-date v-model="dateRange" range mask="YYYY-MM-DD" @update:model-value="applyFilters" />
            </q-popup-proxy>
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

    <div class="row q-col-gutter-lg q-mb-lg">
      <div class="col-12 col-md-8">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6">Distribuição de Custos por Categoria</div>
            <div class="text-subtitle2 text-grey">Total: {{ formatCurrency(totalCost) }}</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <CostsPieChart v-if="filteredCosts.length > 0" :costs="filteredCosts" style="height: 300px;" />
            <div v-else class="text-center text-grey q-pa-md">Sem dados para exibir o gráfico.</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-4">
          <div class="q-gutter-y-md">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey">Custo Total (Filtrado)</div>
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
        :rows="filteredCosts"
        :columns="columns"
        row-key="id"
        :loading="costStore.isLoading"
        no-data-label="Nenhum custo encontrado para os filtros aplicados."
        flat
        :rows-per-page-options="[10, 25, 50]"
      >
        <template v-slot:body-cell-vehicle="props">
          <q-td :props="props">
            <router-link v-if="props.row.vehicle" :to="`/vehicles/${props.row.vehicle_id}`" class="text-primary">
              {{ props.row.vehicle.brand }} {{ props.row.vehicle.model }} ({{ props.row.vehicle.license_plate || props.row.vehicle.identifier }})
            </router-link>
            <span v-else>N/A</span>
          </q-td>
        </template>
      </q-table>
    </q-card>

  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { format, parseISO } from 'date-fns';
import type { QTableColumn } from 'quasar';
import CostsPieChart from 'components/CostsPieChart.vue'; // Componente de gráfico que você já tem

const costStore = useVehicleCostStore();

// Filtros
const dateRange = ref<{ from: string, to: string } | null>(null);
const categoryFilter = ref<string | null>(null);
const costCategoryOptions = ["Manutenção", "Combustível", "Pedágio", "Seguro", "Pneu", "Peças e Componentes", "Outros"];

// Dados Computados para a UI
const filteredCosts = computed(() => {
  if (!categoryFilter.value) {
    return costStore.costs;
  }
  return costStore.costs.filter(cost => cost.cost_type === categoryFilter.value);
});

const totalCost = computed(() => filteredCosts.value.reduce((sum, cost) => sum + cost.amount, 0));
const averageCost = computed(() => totalCost.value / (filteredCosts.value.length || 1));

const topCostCategory = computed(() => {
  if (filteredCosts.value.length === 0) return 'N/A';
  
  const costsByCategory: Record<string, number> = {};
  for (const cost of filteredCosts.value) {
    costsByCategory[cost.cost_type] = (costsByCategory[cost.cost_type] || 0) + cost.amount;
  }
  
  const sortedCategories = Object.entries(costsByCategory).sort((a, b) => b[1] - a[1]);

  // Adiciona uma verificação para garantir que o array não está vazio
  if (sortedCategories.length > 0 && sortedCategories[0]) {
    return sortedCategories[0][0];
  }

  return 'N/A';
});

const dateRangeText = computed(() => {
  if (dateRange.value) {
    const from = format(parseISO(dateRange.value.from), 'dd/MM/yyyy');
    const to = format(parseISO(dateRange.value.to), 'dd/MM/yyyy');
    return `${from} - ${to}`;
  }
  return 'Todo o período';
});

// Colunas da Tabela
const columns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => format(parseISO(val), 'dd/MM/yyyy'), align: 'left', sortable: true },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left', style: 'max-width: 300px; white-space: normal;' },
  { name: 'cost_type', label: 'Categoria', field: 'cost_type', align: 'center', sortable: true },
  { name: 'vehicle', label: 'Veículo', field: 'vehicle', align: 'left', sortable: true },
  { name: 'amount', label: 'Valor', field: 'amount', format: (val) => formatCurrency(val), align: 'right', sortable: true },
];

// Funções de Ação
function applyFilters() {
  const params = {
    startDate: dateRange.value ? new Date(dateRange.value.from) : null,
    endDate: dateRange.value ? new Date(dateRange.value.to) : null,
  };
  void costStore.fetchAllCosts(params);
}

const formatCurrency = (value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

onMounted(() => {
  applyFilters(); // Carrega os dados iniciais
});
</script>