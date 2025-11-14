<template>
  <q-page padding>
    <div v-if="!vehicleStore.isLoading && vehicleStore.selectedVehicle">
      <h1 class="text-h4 text-weight-bold q-my-md">
        {{ vehicleStore.selectedVehicle.brand }} {{ vehicleStore.selectedVehicle.model }}
      </h1>
      <div class="text-subtitle1 text-grey
      ">
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
      <q-tab-panel name="tires" class="q-pa-md">
        <!-- ... (Toda a lógica de Pneus permanece igual) ... -->
        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-6 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey">Custo por KM (Pneus)</div>
                <div class="text-h6 text-weight-bold">
                  {{ kpiTireCostPerKm }}
                  <span v-if="kpiTireCostPerKm !== 'N/A'" class="text-subtitle2 text-grey"> R$/km</span>
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey">Vida Útil Média</div>
                <div class="text-h6 text-weight-bold">
                  {{ kpiAvgTireLifespan }}
                  <span v-if="kpiAvgTireLifespan !== 'N/A'" class="text-subtitle2 text-grey"> km</span>
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey">Pneus em Alerta</div>
                <div class="text-h6 text-weight-bold" :class="kpiTiresInAlert > 0 ? 'text-negative' : 'text-positive'">
                  {{ kpiTiresInAlert }}
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-md-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey">Custo Total (Pneus)</div>
                <div class="text-h6 text-weight-bold">
                  {{ kpiTotalTireCost }}
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
        <q-separator class="q-my-lg" />
        <div class="row items-center justify-between q-mb-md">
          <div class="text-h6">Layout e Status Atual</div>
          <q-btn
            v-if="tireStore.tireLayout?.axle_configuration"
            label="Alterar Config."
            color="secondary"
            flat dense icon="settings"
            @click="isAxleConfigDialogOpen = true"
          />
        </div>
        <InteractiveTireLayout
          v-if="tireStore.tireLayout?.axle_configuration"
          :axle-config="tireStore.tireLayout.axle_configuration"
          :tires="tiresWithStatus"
          :is-agro="isAgro"
          @install="openInstallDialog"
          @remove="openRemoveDialog"
        />
        <div v-else-if="!tireStore.isLoading && !vehicleStore.isLoading && !tireStore.tireLayout?.axle_configuration" class="text-center q-pa-lg bg bordered-card">
            <q-icon name="build" size="lg" color="grey-5" />
            <div class="text-h6 q-mt-md">Nenhuma configuração de eixos definida.</div>
            <p class="text-grey">Para começar a gerenciar os pneus, você precisa primeiro definir o layout de eixos do veículo.</p>
            <q-btn
              label="Definir Configuração de Eixos"
              color="primary"
              unelevated
              @click="isAxleConfigDialogOpen = true"
            />
        </div>
        <q-separator class="q-my-lg" />
        <div class="text-h6 q-mb-md">Análise e Histórico de Pneus</div>
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-lg-8">
            <q-table
              title="Histórico de Pneus Removidos"
              :rows="removedTiresHistory"
              :columns="historyTireColumns"
              row-key="id"
              flat bordered
              dense
              no-data-label="Nenhum pneu foi removido deste veículo ainda."
              :loading="isHistoryLoading"
            />
          </div>
          <div class="col-12 col-lg-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle1">Custos Mensais com Pneus</div>
              </q-card-section>
              <q-card-section>
                <TireCostChart :costs="tireCostsByMonth" />
              </q-card-section>
            </q-card>
          </div>
        </div>
        <q-inner-loading :showing="tireStore.isLoading || isHistoryLoading" />
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
        >
          <!-- CORREÇÃO: Slot para a célula customizada -->
          <template v-slot:body-cell-part_and_item="props">
            <q-td :props="props">
              <div>{{ getPartName(props.row.item?.part_id || props.row.part?.id) }}</div>
              
              <a
                v-if="props.row.item"
                href="#"
                @click.prevent="goToItemDetails(props.row.item.id)"
                class="text-primary text-weight-medium"
                style="text-decoration: none;"
              >
                (Cód. Item: {{ props.row.item.item_identifier }})
                <q-tooltip>Ver detalhes do item (ID Global: {{ props.row.item.id }})</q-tooltip>
              </a>
              <span v-else class="text-grey">(Item N/A)</span>
            </q-td>
          </template>
          </q-table>
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
          
          <!-- CORREÇÃO: Slot para a célula customizada de Componente -->
          <template v-slot:body-cell-component_and_item="props">
            <q-td :props="props">
              <a href="#" @click.prevent="openPartHistoryDialog(props.row.part)" class="text-primary text-weight-medium" style="text-decoration: none;">
                {{ props.row.part?.name || 'Peça N/A' }}
                <q-tooltip>Ver histórico completo do TEMPLATE</q-tooltip>
              </a>
              <a
                v-if="props.row.inventory_transaction?.item"
                href="#"
                @click.prevent="goToItemDetails(props.row.inventory_transaction.item.id)"
                class="text-primary text-weight-medium"
                style="text-decoration: none; display: block;"
              >
                (Cód. Item: {{ props.row.inventory_transaction.item.item_identifier }})
                <q-tooltip>Ver detalhes do ITEM (ID Global: {{ props.row.inventory_transaction.item.id }})</q-tooltip>
              </a>
              <span v-else class="text-grey">(Item N/A)</span>
            </q-td>
          </template>
          <!-- FIM DO SLOT -->
          
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn v-if="props.row.is_active" @click="confirmDiscard(props.row)" flat round dense color="negative" icon="delete" title="Descartar (Fim de Vida)" />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>

      <q-tab-panel name="costs">
        <!-- ... (Toda a lógica de Custos permanece igual) ... -->
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
                <q-tr class="text-weight-bold" :class="$q.dark.isActive ? 'bg-black-9' : 'bg-grey-2'">
                  <q-td colspan="3" class="text-right">Total (Filtrado):</q-td>
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
        <!-- ... (Toda a lógica de Manutenção permanece igual) ... -->
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

    <!-- ... (Todos os diálogos permanecem iguais) ... -->
    <q-dialog v-model="isInstallTireDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallTire">
          <q-card-section>
            <div class="text-h6">Instalar Pneu na Posição: {{ targetPosition }}</div>
          </q-card-section>
          <q-card-section class="q-gutter-y-md">
            <q-select outlined v-model="installTireForm.part_id" :options="tireOptions" label="Selecione o Pneu do Estoque *" emit-value map-options use-input @filter="filterTires" :rules="[val => !!val || 'Selecione um pneu']" />
            <q-input v-if="!isAgro" outlined v-model.number="installTireForm.install_km" type="number" label="KM atual do Veículo *" :rules="[val => val !== null && val >= 0 || 'KM inválido']" />
            <q-input v-else outlined v-model.number="installTireForm.install_engine_hours" type="number" label="Horas do Motor atuais *" :rules="[val => val !== null && val >= 0 || 'Horas inválidas']" />
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
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // <-- 1. IMPORTAR ROUTER
import { useQuasar, type QTableColumn, exportFile } from 'quasar';
import { api } from 'boot/axios';
import { format, differenceInDays, parse } from 'date-fns';
import { storeToRefs } from 'pinia';

// Stores
import { useAuthStore } from 'stores/auth-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store';
import { usePartStore } from 'stores/part-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useTireStore } from 'stores/tire-store';

// Models
import { InventoryItemStatus } from 'src/models/inventory-item-models'; // <-- ADICIONE ESTA IMPORTAÇÃO
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type { InventoryTransaction } from 'src/models/inventory-transaction-models';
import type { Part } from 'src/models/part-models';
import type { MaintenanceRequest } from 'src/models/maintenance-models';
import type { VehicleTire, TireWithStatus, VehicleTireHistory, TireInstallPayload } from 'src/models/tire-models';
import type { VehicleCost } from 'src/models/vehicle-cost-models';

// Components
import PartHistoryDialog from 'components/PartHistoryDialog.vue';
import CostsPieChart from 'components/CostsPieChart.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';
import InteractiveTireLayout from 'components/InteractiveTireLayout.vue';
import TireCostChart from 'components/TireCostChart.vue';
import { axleLayouts } from 'src/config/tire-layouts';
import AddCostDialog from 'components/AddCostDialog.vue';

// --- 2. INICIAR ROUTER ---
const route = useRoute();
const router = useRouter(); 
const $q = useQuasar();
const authStore = useAuthStore();
const vehicleStore = useVehicleStore();
const costStore = useVehicleCostStore();
const componentStore = useVehicleComponentStore();
const partStore = usePartStore();
const maintenanceStore = useMaintenanceStore();
const tireStore = useTireStore();

const { removedTiresHistory } = storeToRefs(tireStore);

const vehicleId = Number(route.params.id);
const tab = ref((route.query.tab as string) || 'tires');
const isAgro = computed(() => authStore.userSector === 'agronegocio');
const isHistoryLoading = ref(false);
const inventoryHistory = ref<InventoryTransaction[]>([]);

// DIÁLOGOS E FORMULÁRIOS
const isAddCostDialogOpen = ref(false);
const isInstallDialogOpen = ref(false);
const isPartHistoryDialogOpen = ref(false);
const isMaintenanceDialogOpen = ref(false);
const isMaintenanceDetailsOpen = ref(false);
const selectedPart = ref<Part | null>(null);
const selectedMaintenance = ref<MaintenanceRequest | null>(null);
const installFormComponent = ref({ part_id: null, quantity: 1 });
const partOptions = ref<{label: string, value: number}[]>([]);
const isInstallTireDialogOpen = ref(false);
const targetPosition = ref('');
const tireOptions = ref<{label: string, value: number}[]>([]);
const installTireForm = ref<{
  part_id: number | null,
  install_km: number | null,
  install_engine_hours?: number | null
}>({ part_id: null, install_km: 0, install_engine_hours: 0 });
const isAxleConfigDialogOpen = ref(false);
const selectedAxleConfig = ref<string | null>(null);
const axleConfigOptions = Object.keys(axleLayouts).map(key => ({
  label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
  value: key
}));

async function refreshAllVehicleData() {
isHistoryLoading.value = true;
  
  // --- A CORREÇÃO ESTÁ AQUI ---
  // 1. Primeiro, buscamos os nomes das peças e ESPERAMOS eles chegarem.
  //    Isso garante que partStore.parts estará preenchido.
  await partStore.fetchParts();

  // 2. Agora que temos os nomes, buscamos todo o resto em paralelo.
await Promise.all([
fetchHistory(), // Esta função agora pode confiar que partStore.parts existe
vehicleStore.fetchVehicleById(vehicleId),
costStore.fetchCosts(vehicleId),
componentStore.fetchComponents(vehicleId),
 maintenanceStore.fetchMaintenanceRequests({ vehicleId: vehicleId, limit: 100 }),
 tireStore.fetchTireLayout(vehicleId),
tireStore.fetchRemovedTiresHistory(vehicleId), // <-- BUSCA O HISTÓRICO CORRETO
 ]);
  isHistoryLoading.value = false;
}

// ... (Lógica de Pneus e KPIs) ...
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

const kpiTireCostPerKm = computed(() => {
  const totalKm = removedTiresHistory.value.reduce((sum, tire) => sum + tire.km_run, 0);
  const totalCost = removedTiresHistory.value.reduce((sum, tire) => sum + (tire.part.value || 0), 0);
  if (totalKm <= 0 || totalCost <= 0) return 'N/A';
  return (totalCost / totalKm).toFixed(2);
});
const kpiTiresInAlert = computed(() => {
  return tiresWithStatus.value.filter(t => t.status === 'warning' || t.status === 'critical').length;
});
const kpiTotalTireCost = computed(() => {
  const removedCost = removedTiresHistory.value.reduce((sum, tire) => sum + (tire.part.value || 0), 0);
  const installedCost = tiresWithStatus.value.reduce((sum, tire) => sum + (tire.part.value || 0), 0);
  const total = removedCost + installedCost;
  return total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
});
const kpiAvgTireLifespan = computed(() => {
    if (removedTiresHistory.value.length === 0) return 'N/A';
    const validEntries = removedTiresHistory.value.filter(item => item.km_run > 0);
    if (validEntries.length === 0) return 'N/A';
    const totalKm = validEntries.reduce((sum, item) => sum + item.km_run, 0);
    return Math.round(totalKm / validEntries.length).toLocaleString('pt-BR');
});
const tireCostsByMonth = computed(() => {
  return inventoryHistory.value
    .filter(t => t.part?.category === 'Pneu' && t.transaction_type === 'Saída para Uso' && t.part?.value)
    .map(t => ({
      date: new Date(t.timestamp),
      amount: t.part!.value!,
    }));
});
// ... (Fim da lógica de Pneus e KPIs) ...


// ### TABELAS E FILTROS ###
const search = ref({ history: '', components: '', costs: '', maintenances: '' });
const dateRange = ref({ history: '', historyTo: '', costs: '', costsTo: '' });

const filteredHistory = computed(() => {
  return inventoryHistory.value.filter(row => {
    const needle = search.value.history.toLowerCase();
    const startDate = dateRange.value.history ? parse(dateRange.value.history, 'dd/MM/yyyy', new Date()) : null;
    const endDate = dateRange.value.historyTo ? parse(dateRange.value.historyTo, 'dd/MM/yyyy', new Date()) : null;
    if(endDate) endDate.setHours(23, 59, 59, 999);
    const rowDate = new Date(row.timestamp);
    const dateMatch = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);
    // Melhorar a pesquisa para incluir o item_identifier
    const itemIdentifier = row.item?.item_identifier || '';
    const partName = row.part?.name || row.item?.part?.name || '';
    const textMatch = !needle || 
                      JSON.stringify(row).toLowerCase().includes(needle) ||
                      String(itemIdentifier).includes(needle) ||
                      partName.toLowerCase().includes(needle);
    return dateMatch && textMatch;
  });
});
const filteredComponents = computed(() => {
  const needle = search.value.components.toLowerCase();
  if (!needle) return componentStore.components;
  return componentStore.components.filter(row => {
    const itemIdentifier = row.inventory_transaction?.item?.item_identifier || '';
    return JSON.stringify(row).toLowerCase().includes(needle) || String(itemIdentifier).includes(needle);
  });
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


// COLUNAS DAS TABELAS
const historyTireColumns: QTableColumn<VehicleTireHistory>[] = [
  { name: 'part', label: 'Pneu (Série)', field: row => row.part.serial_number || 'N/A', align: 'left', sortable: true },
  { name: 'position', label: 'Posição', field: (row) => row.position_code || 'N/A', align: 'center' },
  { name: 'dates', label: 'Inst./Remoção', field: row => `${row.installation_date ? format(new Date(row.installation_date), 'dd/MM/yy') : 'N/A'} - ${row.removal_date ? format(new Date(row.removal_date), 'dd/MM/yy') : 'Em uso'}`, align: 'left' },
  { name: 'km_run', label: 'KM Rodados', field: 'km_run', align: 'right', sortable: true, format: (val: number) => val > 0 ? val.toLocaleString('pt-BR') : 'N/A' },
  { name: 'cost_per_km', label: 'Custo/KM', field: row => (row.km_run > 0 && row.part.value) ? `R$ ${(row.part.value / row.km_run).toFixed(2)}` : 'N/A', align: 'right', sortable: true },
];

// --- 3. CORREÇÃO COLUNAS HISTÓRICO ---
const historyColumns: QTableColumn<InventoryTransaction>[] = [
    { name: 'timestamp', label: 'Data e Hora', field: 'timestamp', format: (val) => format(new Date(val), 'dd/MM/yyyy HH:mm'), align: 'left', sortable: true },
    { 
      name: 'part_and_item', 
      label: 'Peça / Cód. Item', 
      field: (row) => {
          const partId = row.item?.part_id || row.part?.id;
          const partFromStore = partStore.parts.find(p => p.id === partId);

          const name = partFromStore?.name ||   // 1º: Tentar o partStore (confiável)
                       row.part?.name ||          // 2º: Tentar o 'part' da transação
                       row.item?.part?.name ||    // 3º: Tentar o 'part' do item da transação
                       'Peça N/A';              // 4º: Fallback

          // A lógica do Cód. Item já está correta
          const itemId = row.item?.item_identifier || 'N/A';
          
          return `${name} (Cód. Item: ${itemId})`;
      },
      align: 'left', 
      sortable: true 
    },
    { name: 'transaction_type', label: 'Movimentação', field: 'transaction_type', align: 'center', sortable: true },
    { name: 'user', label: 'Realizado por', field: row => row.user?.full_name || 'Sistema', align: 'left' },
    { name: 'notes', label: 'Notas', field: 'notes', align: 'left', style: 'max-width: 200px; white-space: normal;' },
];

// --- 4. CORREÇÃO COLUNAS COMPONENTES ---
  const componentColumns: QTableColumn<VehicleComponent>[] = [
    { 
    name: 'component_and_item', // <-- Nome do slot customizado
    label: 'Componente / Cód. Item', 
    field: (row) => {
        const name = row.part?.name || 'Peça N/A';
        const itemId = row.inventory_transaction?.item?.item_identifier || 'N/A';
        return `${name} (Cód. Item: ${String(itemId)})`;
    },
    align: 'left', 
    sortable: true 
  },
  { 
    name: 'installation_date', 
    label: 'Instalado em', 
    field: 'installation_date', 
    format: (val) => format(new Date(val), 'dd/MM/yyyy'), 
    align: 'left', 
    sortable: true 
  },
  { 
    name: 'age', 
    label: 'Idade (dias)', 
    field: 'installation_date', 
    format: (val) => `${differenceInDays(new Date(), new Date(val))}`, 
    align: 'center', 
    sortable: true 
  },
  { 
    name: 'installer', 
    label: 'Instalado por', 
    field: row => row.inventory_transaction?.user?.full_name || 'N/A', 
    align: 'left', 
    sortable: true 
  },
  { 
    name: 'actions', 
    label: 'Ações', 
    field: () => '', 
    align: 'right' 
  },
];
// --- FIM DA CORREÇÃO ---

const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), sortable: true, align: 'left' },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', sortable: true, align: 'left' },
  { name: 'description', label: 'Descrição', field: 'description', sortable: false, align: 'left', style: 'max-width: 300px; white-space: pre-wrap;' },
  { name: 'amount', label: 'Valor', field: 'amount', format: (val) => val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), sortable: true, align: 'right' },
];
const maintenanceColumns: QTableColumn<MaintenanceRequest>[] = [
  { name: 'created_at', label: 'Data', field: 'created_at', format: (val) => val ? format(new Date(val), 'dd/MM/yyyy') : 'A definir', sortable: true, align: 'left' },
  { name: 'category', label: 'Tipo', field: 'category', sortable: true, align: 'left' },
  { name: 'problem_description', label: 'Descrição', field: 'problem_description', align: 'left', style: 'white-space: pre-wrap;' },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'actions', label: 'Ações', field: () => '', align: 'right' },
];


// ### FUNÇÕES DE AÇÃO ATUALIZADAS ###
async function fetchHistory() {
  isHistoryLoading.value = true;
  try {
    const { data } = await api.get<InventoryTransaction[]>(`/vehicles/${vehicleId}/inventory-history`);
    inventoryHistory.value = data;
  } catch (error) {
    console.error("Falha ao carregar histórico:", error);
    $q.notify({ type: 'negative', message: 'Falha ao carregar o histórico do veículo.' });
  } finally {
    isHistoryLoading.value = false;
  }
}

function getPartName(partId: number | undefined | null): string {
  if (!partId) return 'Peça N/A';
  
  // partStore.parts foi carregado no 'onMounted'
  const part = partStore.parts.find(p => p.id === partId);
  
  return part?.name || 'Peça N/A';
}

// ... (Funções de Pneu: openInstallDialog, handleInstallTire, openRemoveDialog, handleUpdateAxleConfig, filterTires) ...
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
  const payload: TireInstallPayload = {
    position_code: targetPosition.value,
    part_id: installTireForm.value.part_id,
    install_km: installTireForm.value.install_km ?? 0
  };
  if (isAgro.value && typeof installTireForm.value.install_engine_hours === 'number') {
    payload.install_engine_hours = installTireForm.value.install_engine_hours;
  }
  const success = await tireStore.installTire(vehicleId, payload);
  if (success) {
    isInstallTireDialogOpen.value = false;
    await refreshAllVehicleData();
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
    persistent: false,
  }).onOk((valueStr: string) => {
    void (async () => {
      const value = Number(valueStr);
      const removal_km = isAgro.value ? (vehicleStore.selectedVehicle?.current_km || tire.install_km) : value;
      const removal_engine_hours = isAgro.value ? value : undefined;

      let validationOk = false;
      if (isAgro.value) {
        if (removal_engine_hours !== undefined && !isNaN(removal_engine_hours) && removal_engine_hours >= (tire.install_engine_hours || 0)) validationOk = true;
      } else {
        if (!isNaN(removal_km) && removal_km >= tire.install_km) validationOk = true;
      }

      if (!validationOk) {
        $q.notify({ type: 'negative', message: `O valor de remoção deve ser maior ou igual ao de instalação.` });
        return;
      }

      const success = await tireStore.removeTire(tire.id, removal_km, removal_engine_hours);
      if (success) {
        await refreshAllVehicleData();
      }
    })();
  });
}
async function handleUpdateAxleConfig() {
  if (!selectedAxleConfig.value) return;
  const success = await vehicleStore.updateAxleConfiguration(vehicleId, selectedAxleConfig.value);
  if (success) {
    isAxleConfigDialogOpen.value = false;
    await tireStore.fetchTireLayout(vehicleId);
  }
}
function filterTires(val: string, update: (cb: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    tireOptions.value = partStore.parts
      .filter(p => p.category === 'Pneu' && p.stock > 0 && (p.serial_number?.toLowerCase().includes(needle) || p.name.toLowerCase().includes(needle)))
      .map(p => ({ label: `${p.brand || ''} ${p.name} (Série: ${p.serial_number || 'N/A'})`, value: p.id }));
  });
}
// ... (Fim das funções de Pneu) ...


function filterParts(val: string, update: (cb: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    partOptions.value = partStore.parts
      .filter(p => p.name.toLowerCase().includes(needle) && p.stock > 0 && p.category !== 'Pneu') // Exclui Pneus
      .map(p => ({ label: `${p.name} (Estoque: ${p.stock})`, value: p.id }));
  });
}

async function handleInstallComponent() {
  if (!installFormComponent.value.part_id) return;
  // Esta função não existe mais, usamos setItemStatus
  // Vamos emular o comportamento antigo pegando um item do estoque
  $q.notify({ type: 'info', message: 'Função de Instalação Manual (sem Cód. Item) ainda não implementada.' });
  // const success = await componentStore.installComponent(vehicleId, {
  //   part_id: installFormComponent.value.part_id,
  //   quantity: installFormComponent.value.quantity,
  // });
  // if (success) {
  //   isInstallDialogOpen.value = false;
  //   installFormComponent.value = { part_id: null, quantity: 1 };
     await refreshAllVehicleData();
  // }
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
            // Esta função também foi modificada.
            // Precisamos do item_id
            const item_id = component.inventory_transaction?.item?.id;
            if (item_id) {
               const success = await partStore.setItemStatus(component.part.id, item_id, InventoryItemStatus.FIM_DE_VIDA, undefined, "Descartado pelo gerenciador de componentes.");
               if (success) await refreshAllVehicleData();
            } else {
              $q.notify({ type: 'negative', message: 'Erro: Não foi possível encontrar o ID do item de inventário associado.' });
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

// --- 5. ADICIONAR FUNÇÃO DE NAVEGAÇÃO ---
function goToItemDetails(itemId: number) {
  void router.push({ name: 'item-details', params: { id: itemId } });
}
// --- FIM DA FUNÇÃO ---

function exportToCsv(tabName: 'history' | 'components' | 'costs' | 'maintenances') {
    let data: (InventoryTransaction | VehicleComponent | MaintenanceRequest | VehicleCost | VehicleTireHistory)[], columns: QTableColumn[], fileName: string;
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

onMounted(async () => {
  await refreshAllVehicleData();
  selectedAxleConfig.value = vehicleStore.selectedVehicle?.axle_configuration || null;
});
</script>

<style lang="scss" scoped>
.bordered-card {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>
