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
      <q-tab name="details" label="Detalhes" />
      <q-tab name="costs" label="Histórico de Custos" />
      <q-tab name="maintenance" label="Manutenções" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="details">
        <div class="text-h6">Detalhes do Veículo</div>
        <p>Em breve: Todos os detalhes do veículo serão exibidos aqui.</p>
      </q-tab-panel>

      <q-tab-panel name="costs">
        <div class="flex items-center justify-between q-mb-md">
          <div class="text-h6">Custos Lançados</div>
          <q-btn
            @click="isAddCostDialogOpen = true"
            color="primary"
            icon="add"
            label="Adicionar Custo"
            unelevated
          />
        </div>
        <q-table
          :rows="costStore.costs"
          :columns="costColumns"
          row-key="id"
          :loading="costStore.isLoading"
          no-data-label="Nenhum custo lançado para este veículo."
        />
      </q-tab-panel>
      
      <q-tab-panel name="maintenance">
        <div class="text-h6">Histórico de Manutenções</div>
        <p>Em breve: O histórico de manutenções do veículo será exibido aqui.</p>
      </q-tab-panel>
    </q-tab-panels>

    <q-dialog v-model="isAddCostDialogOpen">
      <AddCostDialog :vehicle-id="vehicleId" @close="isAddCostDialogOpen = false" />
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import type { QTableColumn } from 'quasar'; // <-- Importação corrigida para 'import type'
import AddCostDialog from 'components/AddCostDialog.vue';

const route = useRoute();
const vehicleStore = useVehicleStore();
const costStore = useVehicleCostStore();

const tab = ref('costs');
const isAddCostDialogOpen = ref(false);
const vehicleId = Number(route.params.id);

const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => new Date(val).toLocaleDateString('pt-BR', { timeZone: 'UTC' }), sortable: true, align: 'left' },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', sortable: true, align: 'left' },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left' },
  { name: 'amount', label: 'Valor', field: 'amount', format: (val) => `R$ ${val.toFixed(2)}`, sortable: true, align: 'right' },
];

onMounted(() => {
  void vehicleStore.fetchVehicleById(vehicleId);
  void costStore.fetchCosts(vehicleId);
});
</script>