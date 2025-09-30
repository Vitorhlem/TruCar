<template>
  <q-page padding>
    <div v-if="!vehicleStore.isLoading && vehicleStore.selectedVehicle">
      <h1 class="text-h4 text-weight-bold q-my-md">
        {{ vehicleStore.selectedVehicle.brand }} {{ vehicleStore.selectedVehicle.model }}
      </h1>
      <div class="text-subtitle1 text-grey-7">
        {{ vehicleStore.selectedVehicle.license_plate || vehicleStore.selectedVehicle.identifier }}
      </div>
    </div>
    <q-skeleton v-else type="text" class="text-h4 q-my-md" width="300px" />

    <q-tabs v-model="tab" dense class="text-grey q-mt-md" active-color="primary" indicator-color="primary" align="left">
      <q-tab name="history" :label="`Histórico de Peças (${filteredHistory.length})`" />
      <q-tab name="components" label="Componentes Ativos" />
      <q-tab name="costs" label="Custos" />
      <q-tab name="maintenance" label="Manutenções" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="history">
        <div class="row items-center justify-between q-mb-md q-gutter-sm">
          <div class="text-h6">Histórico de Movimentações</div>
          <div class="row items-center q-gutter-sm">
            <q-input dense outlined v-model="dateRange.from" mask="##/##/####" label="De" style="width: 120px" clearable>
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="dateRange.from" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input dense outlined v-model="dateRange.to" mask="##/##/####" label="Até" style="width: 120px" clearable>
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="dateRange.to" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input dense debounce="300" v-model="historySearch" placeholder="Pesquisar..." style="width: 220px" clearable>
              <template v-slot:append><q-icon name="search" /></template>
            </q-input>
            <q-btn @click="exportHistoryToCsv" color="secondary" icon="archive" label="Exportar CSV" unelevated dense />
          </div>
        </div>
        <q-table
          :rows="filteredHistory"
          :columns="historyColumns"
          row-key="id"
          :loading="isHistoryLoading"
          no-data-label="Nenhuma movimentação encontrada para os filtros aplicados."
          flat
          bordered
        />
      </q-tab-panel>

      <q-tab-panel name="components">
        <div class="flex items-center justify-between q-mb-md">
          <div class="text-h6">Componentes Atualmente Instalados</div>
          <q-btn @click="isInstallDialogOpen = true" color="primary" icon="add" label="Instalar Componente" unelevated />
        </div>
        <q-table :rows="componentStore.components" :columns="componentColumns" row-key="id" :loading="componentStore.isLoading" no-data-label="Nenhum componente ativo instalado neste veículo." flat bordered>
          <template v-slot:body-cell-part="props">
            <q-td :props="props">
              <a href="#" @click.prevent="openPartHistoryDialog(props.row.part)" class="text-primary text-weight-medium cursor-pointer" style="text-decoration: none;">
                {{ props.value }}
                <q-tooltip>Ver histórico completo deste item</q-tooltip>
              </a>
            </q-td>
          </template>
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn v-if="props.row.is_active" @click="confirmDiscard(props.row)" flat round dense color="negative" icon="delete" title="Descartar (Fim de Vida)" />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>

      <q-tab-panel name="costs">
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-md-7">
            <div class="flex items-center justify-between q-mb-md">
              <div class="text-h6">Custos Lançados</div>
              <q-btn @click="isAddCostDialogOpen = true" color="primary" icon="add" label="Adicionar Custo" unelevated />
            </div>
            <q-table :rows="costStore.costs" :columns="costColumns" row-key="id" :loading="costStore.isLoading" no-data-label="Nenhum custo lançado para este veículo." flat bordered>
              <template v-slot:bottom-row>
                <q-tr class="bg-black-7 text-weight-bold">
                  <q-td colspan="2" class="text-right">Total:</q-td>
                  <q-td class="text-right">
                    {{ new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalCost) }}
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </div>
          <div class="col-12 col-md-5">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6">Distribuição de Custos</div>
              </q-card-section>
              <q-card-section>
                <CostsPieChart v-if="costStore.costs.length > 0" :costs="costStore.costs" />
                <div v-else class="text-center text-grey q-pa-md">
                  Sem dados suficientes para exibir o gráfico.
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>
      
      <q-tab-panel name="maintenance">
        <div class="flex items-center justify-between q-mb-md">
          <div class="text-h6">Histórico de Manutenções</div>
          <q-btn color="primary" icon="add" label="Agendar Manutenção" unelevated @click="isMaintenanceDialogOpen = true" />
        </div>
        <q-table :rows="maintenanceStore.maintenances" :columns="maintenanceColumns" row-key="id" :loading="maintenanceStore.isLoading" no-data-label="Nenhuma manutenção registrada para este veículo." flat bordered>
          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <q-chip :color="props.row.status === 'CONCLUIDA' ? 'positive' : 'warning'" text-color="white" dense square>{{ props.value }}</q-chip>
            </q-td>
          </template>
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn flat round dense icon="visibility" @click="openMaintenanceDetails(props.row)" title="Ver Detalhes" />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>
    </q-tab-panels>

    <q-dialog v-model="isAddCostDialogOpen"><AddCostDialog :vehicle-id="vehicleId" @close="isAddCostDialogOpen = false" /></q-dialog>
    <q-dialog v-model="isInstallDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallComponent">
          <q-card-section><div class="text-h6">Instalar Componente</div></q-card-section>
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="installForm.part_id" :options="partOptions" label="Selecione a Peça/Fluído *" emit-value map-options use-input @filter="filterParts" :rules="[val => !!val || 'Selecione um item']">
              <template v-slot:no-option><q-item><q-item-section class="text-grey">Nenhum item encontrado</q-item-section></q-item></template>
            </q-select>
            <q-input outlined v-model.number="installForm.quantity" type="number" label="Quantidade *" :rules="[val => val > 0 || 'Deve ser maior que zero']" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Instalar" :loading="componentStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
    <PartHistoryDialog v-model="isPartHistoryDialogOpen" :part="selectedPart" />
    <MaintenanceDetailsDialog v-model="isMaintenanceDetailsOpen" :request="selectedMaintenance" />
    <CreateRequestDialog v-model="isMaintenanceDialogOpen" :preselected-vehicle-id="vehicleId" />

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar, type QTableColumn, exportFile } from 'quasar';
import { api } from 'boot/axios';
import { format, differenceInDays, parse } from 'date-fns';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store';
import { usePartStore } from 'stores/part-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type { InventoryTransaction } from 'src/models/inventory-transaction-models';
import type { Part } from 'src/models/part-models';
import type { MaintenanceRequest } from 'src/models/maintenance-models';
import AddCostDialog from 'components/AddCostDialog.vue';
import PartHistoryDialog from 'components/PartHistoryDialog.vue';
import CostsPieChart from 'components/CostsPieChart.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';

const route = useRoute();
const $q = useQuasar();
const vehicleStore = useVehicleStore();
const costStore = useVehicleCostStore();
const componentStore = useVehicleComponentStore();
const partStore = usePartStore();
const maintenanceStore = useMaintenanceStore();

const tab = ref((route.query.tab as string) || 'history');
const vehicleId = Number(route.params.id);

// --- Controlo de Diálogos ---
const isAddCostDialogOpen = ref(false);
const isInstallDialogOpen = ref(false);
const isPartHistoryDialogOpen = ref(false);
const isMaintenanceDialogOpen = ref(false);
const isMaintenanceDetailsOpen = ref(false);
const selectedPart = ref<Part | null>(null);
const selectedMaintenance = ref<MaintenanceRequest | null>(null);

// --- Histórico ---
const inventoryHistory = ref<InventoryTransaction[]>([]);
const isHistoryLoading = ref(false);
const historySearch = ref('');
const dateRange = ref({ from: '', to: '' });

const filteredHistory = computed(() => {
  const needle = historySearch.value ? historySearch.value.toLowerCase() : '';
  const startDate = dateRange.value.from ? parse(dateRange.value.from, 'dd/MM/yyyy', new Date()) : null;
  const endDate = dateRange.value.to ? parse(dateRange.value.to, 'dd/MM/yyyy', new Date()) : null;
  if(endDate) endDate.setHours(23, 59, 59, 999);

  return inventoryHistory.value.filter((row) => {
    const rowDate = new Date(row.timestamp);
    const dateMatch = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);
    const textMatch = !needle || (
      row.part?.name.toLowerCase().includes(needle) ||
      row.transaction_type.toLowerCase().includes(needle) ||
      row.user?.full_name.toLowerCase().includes(needle)
    );
    return dateMatch && textMatch;
  });
});

// --- Componentes ---
const installForm = ref({ part_id: null, quantity: 1 });
const partOptions = ref<{label: string, value: number}[]>([]);

// --- Custos ---
const totalCost = computed(() => costStore.costs.reduce((sum, cost) => sum + cost.amount, 0));

// --- Colunas das Tabelas ---
const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), sortable: true, align: 'left' },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', sortable: true, align: 'left' },
  { name: 'amount', label: 'Valor', field: 'amount', format: (val) => `R$ ${val.toFixed(2)}`, sortable: true, align: 'right' },
];

const componentColumns: QTableColumn[] = [
  { name: 'part', label: 'Componente', field: row => row.part?.name || 'Item Removido', align: 'left', sortable: true },
  { name: 'installation_date', label: 'Instalado em', field: 'installation_date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), align: 'left', sortable: true },
  { name: 'age', label: 'Idade', field: 'installation_date', format: (val) => `${differenceInDays(new Date(), new Date(val))} dias`, align: 'center', sortable: true },
  { name: 'installer', label: 'Instalado por', field: row => row.inventory_transaction?.user?.full_name || 'N/A', align: 'left', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

const historyColumns: QTableColumn[] = [
    { name: 'timestamp', label: 'Data e Hora', field: 'timestamp', format: (val) => format(new Date(val), 'dd/MM/yyyy HH:mm'), align: 'left', sortable: true },
    { name: 'part', label: 'Peça / Item', field: row => row.part?.name || 'Item Removido', align: 'left', sortable: true },
    { name: 'transaction_type', label: 'Movimentação', field: 'transaction_type', align: 'center', sortable: true },
    { name: 'quantity_change', label: 'Quantidade', field: 'quantity_change', align: 'center', sortable: true, format: (val) => val > 0 ? `+${val}`: val },
    { name: 'user', label: 'Realizado por', field: row => row.user?.full_name || 'Sistema', align: 'left' },
];

const maintenanceColumns: QTableColumn[] = [
  { name: 'start_date', label: 'Data', field: 'start_date', format: (val) => val ? format(new Date(val), 'dd/MM/yyyy') : 'A definir', sortable: true, align: 'left' },
  { name: 'category', label: 'Tipo', field: 'category', sortable: true, align: 'left' },
  { name: 'title', label: 'Descrição', field: 'title', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];


// --- Funções ---
function openPartHistoryDialog(part: Part | null) {
  if (!part) return;
  selectedPart.value = part;
  void partStore.fetchHistory(part.id);
  isPartHistoryDialogOpen.value = true;
}

function openMaintenanceDetails(maintenance: MaintenanceRequest) {
  selectedMaintenance.value = maintenance;
  isMaintenanceDetailsOpen.value = true;
}

function exportHistoryToCsv() {
  const columnsToExp = historyColumns.filter(c => c.label);
  const content = [
    columnsToExp.map(col => col.label).join(';'),
    ...filteredHistory.value.map(row => columnsToExp.map(col => {
      let val;
      if (typeof col.field === 'function') {
        val = col.field(row);
      } else {
        val = row[col.field as keyof typeof row];
      }
      if (col.format && val) {
        val = col.format(val, row);
      }
      return `"${val ?? ''}"`;
    }).join(';'))
  ].join('\r\n');

  const status = exportFile(
    `historico_${vehicleStore.selectedVehicle?.license_plate || vehicleId}.csv`,
    '\ufeff' + content,
    'text/csv'
  );

  if (status !== true) {
    $q.notify({ message: 'O browser bloqueou o download...', color: 'negative', icon: 'warning' });
  }
}

async function fetchHistory() {
  isHistoryLoading.value = true;
  try {
    const response = await api.get<InventoryTransaction[]>(`/vehicles/${vehicleId}/inventory-history`);
    inventoryHistory.value = response.data;
  } catch {
    $q.notify({ type: 'negative', message: 'Falha ao carregar o histórico de peças do veículo.' });
  } finally {
    isHistoryLoading.value = false;
  }
}

function filterParts(val: string, update: (callback: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    partOptions.value = partStore.parts
      .filter(p => p.name.toLowerCase().includes(needle) && p.stock > 0)
      .map(p => ({ label: `${p.name} (Estoque: ${p.stock})`, value: p.id }));
  });
}

async function handleInstallComponent() {
  if (!installForm.value.part_id) return;
  const success = await componentStore.installComponent(vehicleId, {
    part_id: installForm.value.part_id,
    quantity: installForm.value.quantity,
  });
  if (success) {
    isInstallDialogOpen.value = false;
    installForm.value = { part_id: null, quantity: 1 };
    await fetchHistory();
    await partStore.fetchParts();
    await componentStore.fetchComponents(vehicleId);
    // --- ATUALIZAÇÃO DA LISTA DE CUSTOS ---
    await costStore.fetchCosts(vehicleId);
  }
}

function confirmDiscard(component: VehicleComponent) {
    const partName = component.part?.name || 'este item';
    $q.dialog({
        title: 'Confirmar Descarte',
        message: `Você tem certeza que deseja marcar o componente "${partName}" como "Fim de Vida"?`,
        cancel: true, persistent: false,
        ok: { label: 'Confirmar', color: 'negative', unelevated: true }
    }).onOk(() => {
      void (async () => {
        if (component.part) {
            const success = await componentStore.discardComponent(component.id, vehicleId);
            if (success) {
              await fetchHistory();
            }
        }
      })();
    });
}

onMounted(() => {
  void vehicleStore.fetchVehicleById(vehicleId);
  void costStore.fetchCosts(vehicleId);
  void componentStore.fetchComponents(vehicleId);
  void partStore.fetchParts(); 
  void fetchHistory();
  void maintenanceStore.fetchMaintenanceRequests({ vehicleId: vehicleId, limit: 100 });
});
</script>