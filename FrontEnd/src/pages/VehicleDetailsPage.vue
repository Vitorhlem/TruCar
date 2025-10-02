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
      <q-tab name="tires" label="Pneus" />
      <q-tab name="history" :label="`Histórico de Peças (${filteredHistory.length})`" />
      <q-tab name="components" :label="`Componentes Ativos (${filteredComponents.length})`" />
      <q-tab name="costs" :label="`Custos (${filteredCosts.length})`" />
      <q-tab name="maintenance" :label="`Manutenções (${filteredMaintenances.length})`" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="tires">
        <div class="row items-center justify-between q-mb-md">
          <div class="text-h6">Gerenciamento de Pneus</div>
           <q-btn
              v-if="tireStore.tireLayout?.axle_configuration"
              label="Alterar Configuração"
              color="secondary"
              flat
              dense
              icon="settings"
              @click="isAxleConfigDialogOpen = true"
            />
        </div>
        <TireLayout
          v-if="tireStore.tireLayout"
          :axle-config="tireStore.tireLayout.axle_configuration"
          :tires="tiresWithStatus"
          :is-agro="isAgro"
          @install="openInstallDialog"
          @remove="openRemoveDialog"
          @define-config="isAxleConfigDialogOpen = true"
        />
        <q-inner-loading :showing="tireStore.isLoading" />
      </q-tab-panel>
      
      <q-tab-panel name="history">
        <div class="row items-center justify-between q-mb-md q-gutter-sm">
          <div class="text-h6">Histórico de Movimentações</div>
          <div class="row items-center q-gutter-sm">
            <q-input dense outlined v-model="dateRange.history" mask="##/##/####" label="De" style="width: 120px" clearable>
              <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.history" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
            </q-input>
            <q-input dense outlined v-model="dateRange.historyTo" mask="##/##/####" label="Até" style="width: 120px" clearable>
              <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.historyTo" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
            </q-input>
            <q-input dense debounce="300" v-model="search.history" placeholder="Pesquisar..." style="width: 220px" clearable>
              <template v-slot:append><q-icon name="search" /></template>
            </q-input>
            <q-btn @click="exportToCsv('history')" color="secondary" icon="archive" label="Exportar CSV" unelevated dense />
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
        <div class="row items-center justify-between q-mb-md q-gutter-sm">
          <div class="text-h6">Componentes Atualmente Instalados</div>
          <div class="row items-center q-gutter-sm">
            <q-input dense debounce="300" v-model="search.components" placeholder="Pesquisar..." style="width: 220px" clearable>
              <template v-slot:append><q-icon name="search" /></template>
            </q-input>
            <q-btn @click="exportToCsv('components')" color="secondary" icon="archive" label="Exportar CSV" unelevated dense />
            <q-btn @click="isInstallDialogOpen = true" color="primary" icon="add" label="Instalar Componente" unelevated />
          </div>
        </div>
        <q-table :rows="filteredComponents" :columns="componentColumns" row-key="id" :loading="componentStore.isLoading" no-data-label="Nenhum componente encontrado." flat bordered>
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
        <div class="row items-center justify-between q-mb-md q-gutter-sm">
            <div class="text-h6">Custos Lançados</div>
            <div class="row items-center q-gutter-sm">
              <q-input dense outlined v-model="dateRange.costs" mask="##/##/####" label="De" style="width: 120px" clearable>
                <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.costs" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
              </q-input>
              <q-input dense outlined v-model="dateRange.costsTo" mask="##/##/####" label="Até" style="width: 120px" clearable>
                <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.costsTo" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
              </q-input>
              <q-input dense debounce="300" v-model="search.costs" placeholder="Pesquisar..." style="width: 220px" clearable>
                <template v-slot:append><q-icon name="search" /></template>
              </q-input>
              <q-btn @click="exportToCsv('costs')" color="secondary" icon="archive" label="Exportar CSV" unelevated dense />
              <q-btn @click="isAddCostDialogOpen = true" color="primary" icon="add" label="Adicionar Custo" unelevated />
            </div>
        </div>
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-md-7">
            <q-table :rows="filteredCosts" :columns="costColumns" row-key="id" :loading="costStore.isLoading" no-data-label="Nenhum custo encontrado para os filtros aplicados." flat bordered>
              <template v-slot:bottom-row>
                <q-tr class="bg-black-9 text-weight-bold">
                  <q-td colspan="2" class="text-right">Total (Filtrado):</q-td>
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
                <div class="text-h6">Distribuição de Custos (Filtrado)</div>
              </q-card-section>
              <q-card-section>
                <CostsPieChart v-if="filteredCosts.length > 0" :costs="filteredCosts" />
                <div v-else class="text-center text-grey q-pa-md">
                  Sem dados para exibir o gráfico.
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <q-tab-panel name="maintenance">
        <div class="row items-center justify-between q-mb-md q-gutter-sm">
          <div class="text-h6">Histórico de Manutenções</div>
          <div class="row items-center q-gutter-sm">
            <q-input dense debounce="300" v-model="search.maintenances" placeholder="Pesquisar..." style="width: 220px" clearable>
              <template v-slot:append><q-icon name="search" /></template>
            </q-input>
            <q-btn @click="exportToCsv('maintenances')" color="secondary" icon="archive" label="Exportar CSV" unelevated dense />
            <q-btn color="primary" icon="add" label="Agendar Manutenção" unelevated @click="isMaintenanceDialogOpen = true" />
          </div>
        </div>
        <q-table :rows="filteredMaintenances" :columns="maintenanceColumns" row-key="id" :loading="maintenanceStore.isLoading" no-data-label="Nenhuma manutenção encontrada para os filtros aplicados." flat bordered>
          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <q-chip :color="props.row.status === 'COMPLETED' ? 'positive' : 'warning'" text-color="white" dense square>{{ props.value }}</q-chip>
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

    <!-- Diálogos -->
    <q-dialog v-model="isInstallTireDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallTire">
          <q-card-section>
            <div class="text-h6">Instalar Pneu na Posição: {{ targetPosition }}</div>
          </q-card-section>
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="installTireForm.part_id" :options="tireOptions" label="Selecione o Pneu do Estoque *" emit-value map-options use-input @filter="filterTires" :rules="[val => !!val || 'Selecione um pneu']" />
            <q-input v-if="!isAgro" outlined v-model.number="installTireForm.install_km" type="number" label="KM atual do Veículo *" :rules="[val => val >= 0 || 'KM inválido']" />
            <q-input v-else outlined v-model.number="installTireForm.install_engine_hours" type="number" label="Horas do Motor atuais *" :rules="[val => val >= 0 || 'Horas inválidas']" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Instalar" :loading="tireStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isAxleConfigDialogOpen">
      <q-card style="width: 400px; max-width: 90vw;">
        <q-form @submit.prevent="handleUpdateAxleConfig">
          <q-card-section>
            <div class="text-h6">Definir Configuração de Eixos</div>
          </q-card-section>
          <q-card-section>
            <q-select outlined v-model="selectedAxleConfig" :options="axleConfigOptions" label="Selecione o tipo de veículo/eixo" emit-value map-options :rules="[val => !!val || 'Selecione uma configuração']" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isInstallDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallComponent">
          <q-card-section><div class="text-h6">Instalar Componente</div></q-card-section>
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="installFormComponent.part_id" :options="partOptions" label="Selecione a Peça/Fluído *" emit-value map-options use-input @filter="filterParts" :rules="[val => !!val || 'Selecione um item']">
              <template v-slot:no-option><q-item><q-item-section class="text-grey">Nenhum item encontrado</q-item-section></q-item></template>
            </q-select>
            <q-input outlined v-model.number="installFormComponent.quantity" type="number" label="Quantidade *" :rules="[val => val > 0 || 'Deve ser maior que zero']" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Instalar" :loading="componentStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isAddCostDialogOpen">
      <AddCostDialog :vehicle-id="vehicleId" @close="isAddCostDialogOpen = false" />
    </q-dialog>

    <PartHistoryDialog v-model="isPartHistoryDialogOpen" :part="selectedPart" />
    <MaintenanceDetailsDialog v-model="isMaintenanceDetailsOpen" :request="selectedMaintenance" />
    <CreateRequestDialog v-model="isMaintenanceDialogOpen" :preselected-vehicle-id="vehicleId" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onActivated } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar, type QTableColumn, exportFile } from 'quasar';
import { api } from 'boot/axios';
import { format, differenceInDays, parse } from 'date-fns';

// Stores
import { useAuthStore } from 'stores/auth-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store';
import { usePartStore } from 'stores/part-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useTireStore } from 'stores/tire-store';
import { useNotificationStore } from 'stores/notification-store';

// Models
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type { InventoryTransaction } from 'src/models/inventory-transaction-models';
import type { Part } from 'src/models/part-models';
import type { MaintenanceRequest } from 'src/models/maintenance-models';
import type { VehicleTire, TireWithStatus } from 'src/models/tire-models';
import type { VehicleCost } from 'src/models/vehicle-cost-models';


// Components
import PartHistoryDialog from 'components/PartHistoryDialog.vue';
import CostsPieChart from 'components/CostsPieChart.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';
import TireLayout from 'components/TireLayout.vue';
import { axleLayouts } from 'src/config/tire-layouts';
import AddCostDialog from 'components/AddCostDialog.vue';


const route = useRoute();
const $q = useQuasar();
const authStore = useAuthStore();
const vehicleStore = useVehicleStore();
const costStore = useVehicleCostStore();
const componentStore = useVehicleComponentStore();
const partStore = usePartStore();
const maintenanceStore = useMaintenanceStore();
const tireStore = useTireStore();
const notificationStore = useNotificationStore();

const vehicleId = Number(route.params.id);
const tab = ref((route.query.tab as string) || 'tires');
const isAgro = computed(() => authStore.userSector === 'agronegocio');

// --- Diálogos e Formulários ---
const isAddCostDialogOpen = ref(false);
const isInstallDialogOpen = ref(false);
const isPartHistoryDialogOpen = ref(false);
const isMaintenanceDialogOpen = ref(false);
const isMaintenanceDetailsOpen = ref(false);
const selectedPart = ref<Part | null>(null);
const selectedMaintenance = ref<MaintenanceRequest | null>(null);
const installFormComponent = ref({ part_id: null, quantity: 1 });
const partOptions = ref<{label: string, value: number}[]>([]);

// --- Pneus ---
const isInstallTireDialogOpen = ref(false);
const targetPosition = ref('');
const tireOptions = ref<{label: string, value: number}[]>([]);
const installTireForm = ref<{
  part_id: number | null,
  install_km: number | null,
  install_engine_hours?: number | null
}>({ part_id: null, install_km: null, install_engine_hours: null });

// --- Eixos ---
const isAxleConfigDialogOpen = ref(false);
const selectedAxleConfig = ref<string | null>(null);
const axleConfigOptions = Object.keys(axleLayouts).map(key => ({
  label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
  value: key
}));

// --- Alertas de Pneus ---
const tiresWithStatus = computed((): TireWithStatus[] => {
  if (!tireStore.tireLayout?.tires || !vehicleStore.selectedVehicle) return [];
  const currentKm = vehicleStore.selectedVehicle.current_km || 0;
  const currentEngineHours = vehicleStore.selectedVehicle.current_engine_hours || 0;
  return tireStore.tireLayout.tires.map(tire => {
    const lifespan_unit = tire.part.lifespan_km || 0;
    if (lifespan_unit <= 0) return { ...tire, status: 'ok', wearPercentage: 0, km_rodados: 0, horas_de_uso: 0, lifespan_km: 0 };
    let units_used = 0;
    if (isAgro.value) {
      units_used = currentEngineHours - (tire.install_engine_hours || 0);
    } else {
      units_used = currentKm - tire.install_km;
    }
    units_used = Math.max(0, units_used);
    const wearPercentage = (units_used / lifespan_unit) * 100;
    let status: 'ok' | 'warning' | 'critical' = 'ok';
    if (wearPercentage >= 100) status = 'critical';
    else if (wearPercentage >= 80) status = 'warning';
    return { ...tire, status, wearPercentage, km_rodados: isAgro.value ? 0 : units_used, horas_de_uso: isAgro.value ? units_used : 0, lifespan_km: lifespan_unit };
  });
});

// --- Filtros e Tabelas ---
const search = ref({ history: '', components: '', costs: '', maintenances: '' });
const dateRange = ref({ history: '', historyTo: '', costs: '', costsTo: '' });
const inventoryHistory = ref<InventoryTransaction[]>([]);
const isHistoryLoading = ref(false);

const filteredHistory = computed(() => {
  return inventoryHistory.value.filter(row => {
    const needle = search.value.history.toLowerCase();
    const startDate = dateRange.value.history ? parse(dateRange.value.history, 'dd/MM/yyyy', new Date()) : null;
    const endDate = dateRange.value.historyTo ? parse(dateRange.value.historyTo, 'dd/MM/yyyy', new Date()) : null;
    if(endDate) endDate.setHours(23, 59, 59, 999);
    const rowDate = new Date(row.timestamp);
    const dateMatch = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);
    const textMatch = !needle || JSON.stringify(row).toLowerCase().includes(needle);
    return dateMatch && textMatch;
  });
});
const filteredComponents = computed(() => {
  const needle = search.value.components.toLowerCase();
  if (!needle) return componentStore.components;
  return componentStore.components.filter(row => JSON.stringify(row).toLowerCase().includes(needle));
});
const filteredCosts = computed(() => {
  return costStore.costs.filter(row => {
    const needle = search.value.costs.toLowerCase();
    const startDate = dateRange.value.costs ? parse(dateRange.value.costs, 'dd/MM/yyyy', new Date()) : null;
    const endDate = dateRange.value.costsTo ? parse(dateRange.value.costsTo, 'dd/MM/yyyy', new Date()) : null;
    if(endDate) endDate.setHours(23, 59, 59, 999);
    const rowDate = new Date(row.date);
    const dateMatch = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);
    const textMatch = !needle || JSON.stringify(row).toLowerCase().includes(needle);
    return dateMatch && textMatch;
  });
});
const totalCost = computed(() => filteredCosts.value.reduce((sum, cost) => sum + cost.amount, 0));
const filteredMaintenances = computed(() => {
  const needle = search.value.maintenances.toLowerCase();
  if (!needle) return maintenanceStore.maintenances;
  return maintenanceStore.maintenances.filter(row => JSON.stringify(row).toLowerCase().includes(needle));
});

const historyColumns: QTableColumn[] = [
    { name: 'timestamp', label: 'Data e Hora', field: 'timestamp', format: (val) => format(new Date(val), 'dd/MM/yyyy HH:mm'), align: 'left', sortable: true },
    { name: 'part', label: 'Peça / Item', field: row => row.part?.name || 'Item Removido', align: 'left', sortable: true },
    { name: 'transaction_type', label: 'Movimentação', field: 'transaction_type', align: 'center', sortable: true },
    { name: 'quantity_change', label: 'Quantidade', field: 'quantity_change', align: 'center', sortable: true, format: (val) => val > 0 ? `+${val}`: val },
    { name: 'user', label: 'Realizado por', field: row => row.user?.full_name || 'Sistema', align: 'left' },
];
const componentColumns: QTableColumn[] = [
  { name: 'part', label: 'Componente', field: (row: VehicleComponent) => row.part?.name || 'Item Removido', align: 'left', sortable: true },
  { name: 'installation_date', label: 'Instalado em', field: 'installation_date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), align: 'left', sortable: true },
  { name: 'age', label: 'Idade (dias)', field: 'installation_date', format: (val) => `${differenceInDays(new Date(), new Date(val))}`, align: 'center', sortable: true },
  { name: 'installer', label: 'Instalado por', field: (row: VehicleComponent) => row.inventory_transaction?.user?.full_name || 'N/A', align: 'left', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];
const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), sortable: true, align: 'left' },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', sortable: true, align: 'left' },
  { name: 'amount', label: 'Valor', field: 'amount', format: (val) => val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), sortable: true, align: 'right' },
];
const maintenanceColumns: QTableColumn[] = [
  { name: 'created_at', label: 'Data', field: 'created_at', format: (val) => val ? format(new Date(val), 'dd/MM/yyyy') : 'A definir', sortable: true, align: 'left' },
  { name: 'category', label: 'Tipo', field: 'category', sortable: true, align: 'left' },
  { name: 'problem_description', label: 'Descrição', field: 'problem_description', align: 'left', style: 'white-space: pre-wrap;' },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

// --- Funções ---

// --- Funções de Pneus ---
function openInstallDialog(positionCode: string) {
  targetPosition.value = positionCode;
  installTireForm.value = {
    part_id: null,
    install_km: vehicleStore.selectedVehicle?.current_km || 0,
    install_engine_hours: vehicleStore.selectedVehicle?.current_engine_hours || 0
  };
  isInstallTireDialogOpen.value = true;
}

async function handleInstallTire() {
  if (!installTireForm.value.part_id) {
    $q.notify({ type: 'negative', message: 'Por favor, selecione um pneu.' });
    return;
  }
  const payload = {
    position_code: targetPosition.value,
    part_id: installTireForm.value.part_id,
    install_km: installTireForm.value.install_km ?? 0,
    install_engine_hours: installTireForm.value.install_engine_hours
  };
  const success = await tireStore.installTire(vehicleId, payload);
  if (success) {
    isInstallTireDialogOpen.value = false;
    await Promise.all([
      partStore.fetchParts(),
      costStore.fetchCosts(vehicleId),
      tireStore.fetchTireLayout(vehicleId)
    ]);
  }
}

function openRemoveDialog(tire: VehicleTire) {
  const message = isAgro.value
    ? `Digite as Horas do Motor atuais para remover o pneu (Série: ${tire.part.serial_number}) da posição ${tire.position_code}.`
    : `Digite o KM atual do veículo para remover o pneu (Série: ${tire.part.serial_number}) da posição ${tire.position_code}.`;

  const model = isAgro.value
    ? String(vehicleStore.selectedVehicle?.current_engine_hours || tire.install_engine_hours || 0)
    : String(vehicleStore.selectedVehicle?.current_km || tire.install_km);

  $q.dialog({
    title: 'Remover Pneu',
    message,
    prompt: { model, type: 'number' },
    cancel: true,
    persistent: true,
  }).onOk((valueStr: string) => {
    void (async () => {
      const value = Number(valueStr);
      const payload: { removal_km: number, removal_engine_hours: number } = { 
          removal_km: 0,
          removal_engine_hours: 0,
       };
      let validationOk = false;

      if (isAgro.value) {
        payload.removal_engine_hours = value;
        payload.removal_km = vehicleStore.selectedVehicle?.current_km || tire.install_km;
        if (!isNaN(value) && value >= (tire.install_engine_hours || 0)) {
          validationOk = true;
        }
      } else {
        payload.removal_km = value;
        if (!isNaN(value) && value >= tire.install_km) {
          validationOk = true;
        }
      }

      if (!validationOk) {
        $q.notify({ type: 'negative', message: `O valor de remoção deve ser maior ou igual ao de instalação.` });
        return;
      }
      
      const success = await tireStore.removeTire(tire.id, payload.removal_km, payload.removal_engine_hours);
      if (success) {
        await fetchHistory();
      }
    })();
  });
}

const generatedAlerts = new Set<string>();
function checkTireWearAndNotify(tires: TireWithStatus[]) { 
    if (!vehicleStore.selectedVehicle) return;
    const vehicleName = `${vehicleStore.selectedVehicle.brand} ${vehicleStore.selectedVehicle.model} (${vehicleStore.selectedVehicle.license_plate || vehicleStore.selectedVehicle.identifier})`;
    for (const tire of tires) {
        const alertKey = `tire-${tire.id}-${tire.status}`;
        if (generatedAlerts.has(alertKey)) continue;

        if (tire.status === 'critical') {
            generatedAlerts.add(alertKey);
            void notificationStore.createNotification({
                message: `ALERTA CRÍTICO: Pneu ${tire.part.serial_number} no veículo ${vehicleName} atingiu 100% do desgaste esperado. Troca recomendada!`,
                related_vehicle_id: vehicleId,
            });
        } else if (tire.status === 'warning') {
            generatedAlerts.add(alertKey);
            void notificationStore.createNotification({
                message: `ATENÇÃO: Pneu ${tire.part.serial_number} no veículo ${vehicleName} atingiu 80% do desgaste. Inspecionar para troca ou reforma.`,
                related_vehicle_id: vehicleId,
            });
        }
    }
}
watch(tiresWithStatus, (newTires) => { 
    if (newTires.length > 0) {
        checkTireWearAndNotify(newTires);
    }
}, { deep: true });

async function handleUpdateAxleConfig() {
  if (!selectedAxleConfig.value) return;
  const success = await vehicleStore.updateAxleConfiguration(vehicleId, selectedAxleConfig.value);
  if (success) {
    isAxleConfigDialogOpen.value = false;
  }
}

// --- Funções Genéricas e de Componentes ---
function filterTires(val: string, update: (cb: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    tireOptions.value = partStore.parts
      .filter(p => p.category === 'Pneu' && p.stock > 0 && (p.serial_number?.toLowerCase().includes(needle) || p.name.toLowerCase().includes(needle)))
      .map(p => ({ label: `${p.brand || ''} ${p.name} (Série: ${p.serial_number || 'N/A'})`, value: p.id }));
  });
}

function filterParts(val: string, update: (cb: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    partOptions.value = partStore.parts
      .filter(p => p.name.toLowerCase().includes(needle) && p.stock > 0)
      .map(p => ({ label: `${p.name} (Estoque: ${p.stock})`, value: p.id }));
  });
}

async function handleInstallComponent() {
  if (!installFormComponent.value.part_id) return;
  const success = await componentStore.installComponent(vehicleId, {
    part_id: installFormComponent.value.part_id,
    quantity: installFormComponent.value.quantity,
  });
  if (success) {
    isInstallDialogOpen.value = false;
    installFormComponent.value = { part_id: null, quantity: 1 };
    await Promise.all([
        fetchHistory(),
        partStore.fetchParts(),
        componentStore.fetchComponents(vehicleId),
        costStore.fetchCosts(vehicleId)
    ]);
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

async function fetchHistory() {
  isHistoryLoading.value = true;
  try {
    const { data } = await api.get<InventoryTransaction[]>(`/vehicles/${vehicleId}/inventory-history`);
    inventoryHistory.value = data;
  } catch (error) {
    console.error("Falha ao carregar histórico de peças:", error);
    $q.notify({ type: 'negative', message: 'Falha ao carregar o histórico de peças do veículo.' });
  } finally {
    isHistoryLoading.value = false;
  }
}

function exportToCsv(tabName: 'history' | 'components' | 'costs' | 'maintenances') {
    let data: (InventoryTransaction | VehicleComponent | MaintenanceRequest | VehicleCost)[], columns: QTableColumn[], fileName: string;
    switch(tabName) {
        case 'history': data = filteredHistory.value; columns = historyColumns; fileName = 'historico'; break;
        case 'components': data = filteredComponents.value; columns = componentColumns; fileName = 'componentes'; break;
        case 'costs': data = filteredCosts.value; columns = costColumns; fileName = 'custos'; break;
        case 'maintenances': data = filteredMaintenances.value; columns = maintenanceColumns; fileName = 'manutencoes'; break;
    }

    if (!data || !columns || !fileName) return;

    const columnsToExp = columns.filter(c => c.name !== 'actions' && c.label);
    const content = [
        columnsToExp.map(col => col.label).join(';'),
        ...data.map(row => columnsToExp.map(col => {
          let val;
          if (typeof col.field === 'function') val = col.field(row as never);
          else val = row[col.field as keyof typeof row];
          if (col.format && val) val = col.format(val, row as never);
          const cleanVal = `"${String(val ?? '').replace(/"/g, '""')}"`;
          return cleanVal;
        }).join(';'))
    ].join('\r\n');

    const status = exportFile(
      `${fileName}_veiculo_${vehicleId}.csv`,
      '\ufeff' + content, 'text/csv'
    );
    if (status !== true) $q.notify({ message: 'O browser bloqueou o download...', color: 'negative' });
}


// --- Ciclo de Vida ---
onActivated(async () => {
  await vehicleStore.fetchVehicleById(vehicleId);
});

onMounted(() => {
  const promises = [
    vehicleStore.fetchVehicleById(vehicleId),
    costStore.fetchCosts(vehicleId),
    componentStore.fetchComponents(vehicleId),
    partStore.fetchParts(),
    fetchHistory(),
    maintenanceStore.fetchMaintenanceRequests({ vehicleId: vehicleId, limit: 100 }),
    tireStore.fetchTireLayout(vehicleId)
  ];
  void Promise.all(promises).then(() => {
    selectedAxleConfig.value = vehicleStore.selectedVehicle?.axle_configuration || null;
    checkTireWearAndNotify(tiresWithStatus.value);
  }).catch(err => console.error("Erro no onMounted Promise.all:", err));
});

</script>

