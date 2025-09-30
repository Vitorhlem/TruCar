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
      <q-tab name="history" :label="`Histórico de Peças (${historyCount})`" />
      <q-tab name="components" label="Componentes Ativos" />
      <q-tab name="costs" label="Custos" />
      <q-tab name="maintenance" label="Manutenções" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="history">
        <div class="text-h6 q-mb-md">Histórico de Movimentações de Estoque</div>
        <q-table
          :rows="inventoryHistory"
          :columns="historyColumns"
          row-key="id"
          :loading="isHistoryLoading"
          no-data-label="Nenhuma movimentação de estoque registrada para este veículo."
        />
      </q-tab-panel>

      <q-tab-panel name="components">
        <div class="flex items-center justify-between q-mb-md">
          <div class="text-h6">Componentes Atualmente Instalados</div>
          <q-btn @click="isInstallDialogOpen = true" color="primary" icon="add" label="Instalar Componente" unelevated />
        </div>
        <q-table
          :rows="componentStore.components"
          :columns="componentColumns"
          row-key="id"
          :loading="componentStore.isLoading"
          no-data-label="Nenhum componente ativo instalado neste veículo."
        >
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn v-if="props.row.is_active" @click="confirmDiscard(props.row)" flat round dense color="negative" icon="delete" title="Descartar (Fim de Vida)" />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>

      <q-tab-panel name="costs">
        <div class="flex items-center justify-between q-mb-md">
          <div class="text-h6">Custos Lançados</div>
          <q-btn @click="isAddCostDialogOpen = true" color="primary" icon="add" label="Adicionar Custo" unelevated />
        </div>
        <q-table :rows="costStore.costs" :columns="costColumns" row-key="id" :loading="costStore.isLoading" no-data-label="Nenhum custo lançado para este veículo." />
      </q-tab-panel>
      
      <q-tab-panel name="maintenance">
        <div class="text-h6">Histórico de Manutenções</div>
        <p>Em breve: O histórico de manutenções do veículo será exibido aqui.</p>
      </q-tab-panel>
    </q-tab-panels>

    <q-dialog v-model="isAddCostDialogOpen"><AddCostDialog :vehicle-id="vehicleId" @close="isAddCostDialogOpen = false" /></q-dialog>
    <q-dialog v-model="isInstallDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallComponent">
          <q-card-section>
            <div class="text-h6">Instalar Componente</div>
          </q-card-section>
          <q-card-section class="q-gutter-y-md">
            <q-select
              outlined v-model="installForm.part_id" :options="partOptions"
              label="Selecione a Peça/Fluído do Estoque *" emit-value map-options use-input
              @filter="filterParts" :rules="[val => !!val || 'Selecione um item']"
            >
              <template v-slot:no-option>
                <q-item><q-item-section class="text-grey">Nenhum item encontrado</q-item-section></q-item>
              </template>
            </q-select>
            <q-input outlined v-model.number="installForm.quantity" type="number" label="Quantidade *" :rules="[val => val > 0 || 'Deve ser maior que zero']" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Instalar" :loading="componentStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar, type QTableColumn } from 'quasar';
import { api } from 'boot/axios';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store';
import { usePartStore } from 'stores/part-store';
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type { InventoryTransaction } from 'src/models/inventory-transaction-models';
import AddCostDialog from 'components/AddCostDialog.vue';

const route = useRoute();
const $q = useQuasar();
const vehicleStore = useVehicleStore();
const costStore = useVehicleCostStore();
const componentStore = useVehicleComponentStore();
const partStore = usePartStore();

const tab = ref((route.query.tab as string) || 'history');

const isAddCostDialogOpen = ref(false);
const isInstallDialogOpen = ref(false);
const vehicleId = Number(route.params.id);

const installForm = ref({ part_id: null, quantity: 1 });
const partOptions = ref<{label: string, value: number}[]>([]);

const inventoryHistory = ref<InventoryTransaction[]>([]);
const isHistoryLoading = ref(false);
const historyCount = computed(() => inventoryHistory.value.length);

const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => new Date(val).toLocaleDateString('pt-BR', { timeZone: 'UTC' }), sortable: true, align: 'left' },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', sortable: true, align: 'left' },
  { name: 'amount', label: 'Valor', field: 'amount', format: (val) => `R$ ${val.toFixed(2)}`, sortable: true, align: 'right' },
];

// --- CORREÇÃO APLICADA AQUI ---
const componentColumns: QTableColumn[] = [
  { name: 'part', label: 'Componente', field: row => row.part?.name || 'Item Removido', align: 'left', sortable: true },
  { name: 'installation_date', label: 'Data de Instalação', field: 'installation_date', format: (val) => new Date(val).toLocaleDateString('pt-BR'), align: 'left', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

const historyColumns: QTableColumn[] = [
  { name: 'timestamp', label: 'Data e Hora', field: 'timestamp', format: (val) => new Date(val).toLocaleString('pt-BR'), align: 'left', sortable: true },
  { name: 'part', label: 'Peça / Item', field: row => row.part?.name || 'Item Removido', align: 'left', sortable: true },
  { name: 'transaction_type', label: 'Movimentação', field: 'transaction_type', align: 'center', sortable: true },
  { name: 'quantity_change', label: 'Quantidade', field: 'quantity_change', align: 'center', sortable: true },
  { name: 'user', label: 'Realizado por', field: row => row.user?.full_name || 'Sistema', align: 'left' },
];
// --- FIM DA CORREÇÃO ---

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
  if (val === '') {
    update(() => { partOptions.value = partStore.parts.map(p => ({ label: `${p.name} (Estoque: ${p.stock})`, value: p.id })); });
    return;
  }
  update(() => {
    const needle = val.toLowerCase();
    partOptions.value = partStore.parts
      .filter(p => p.name.toLowerCase().indexOf(needle) > -1)
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
    await fetchHistory();
  }
}

function confirmDiscard(component: VehicleComponent) {
  $q.dialog({
    title: 'Confirmar Descarte',
    message: `Você tem certeza que deseja marcar o componente "${component.part.name}" como "Fim de Vida"?`,
    cancel: true, persistent: false,
    ok: { label: 'Confirmar', color: 'negative' }
  }).onOk(() => {
    void componentStore.discardComponent(component.id, vehicleId);
  });
}

onMounted(() => {
  void vehicleStore.fetchVehicleById(vehicleId);
  void costStore.fetchCosts(vehicleId);
  void componentStore.fetchComponents(vehicleId);
  void partStore.fetchParts(); 
  void fetchHistory();
});
</script>