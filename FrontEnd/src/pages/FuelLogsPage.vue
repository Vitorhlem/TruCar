<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Registros de Abastecimento</h1>
      <q-btn @click="openCreateDialog" color="primary" icon="add" label="Registrar Abastecimento" unelevated />
    </div>

    <q-card flat bordered>
      <q-table
        :rows="fuelLogStore.fuelLogs"
        :columns="columns"
        row-key="id"
        :loading="fuelLogStore.isLoading"
        no-data-label="Nenhum abastecimento registrado"
      >
        </q-table>
    </q-card>

    <q-dialog v-model="isCreateDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">Novo Registro de Abastecimento</div>
        </q-card-section>
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-select
              outlined
              v-model="formData.vehicle_id"
              :options="vehicleOptions"
              label="Veículo *"
              emit-value map-options
              :rules="[val => !!val || 'Selecione um veículo']"
            />
            <q-input outlined v-model.number="formData.odometer" type="number" label="KM do Odômetro *" :rules="[val => val > 0 || 'KM deve ser positivo']" />
            <q-input outlined v-model.number="formData.liters" type="number" label="Litros Abastecidos *" step="0.01" :rules="[val => val > 0 || 'Valor inválido']" />
            <q-input outlined v-model.number="formData.total_cost" type="number" label="Custo Total (R$) *" prefix="R$" step="0.01" :rules="[val => val > 0 || 'Valor inválido']" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar Registro" :loading="fuelLogStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useFuelLogStore } from 'stores/fuel-log-store';
import { useVehicleStore } from 'stores/vehicle-store';
import type { QTableColumn } from 'quasar';
import type { FuelLog, FuelLogCreate } from 'src/models/fuel-log-models';

const fuelLogStore = useFuelLogStore();
const vehicleStore = useVehicleStore();

const isCreateDialogOpen = ref(false);
const formData = ref<FuelLogCreate>({
  vehicle_id: 0,
  odometer: 0,
  liters: 0,
  total_cost: 0,
});

const vehicleOptions = computed(() => vehicleStore.vehicles.map(v => ({
  label: `${v.brand} ${v.model} (${v.license_plate})`,
  value: v.id
})));

const columns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'timestamp', format: (val) => new Date(val).toLocaleDateString('pt-BR'), align: 'left', sortable: true },
  { name: 'vehicle', label: 'Veículo', field: (row: FuelLog) => `${row.vehicle.brand} ${row.vehicle.model}`, align: 'left', sortable: true },
  { name: 'odometer', label: 'Odômetro (KM)', field: 'odometer', align: 'center', sortable: true },
  { name: 'liters', label: 'Litros', field: 'liters', align: 'right', format: (val) => val.toFixed(2), sortable: true },
  { name: 'cost', label: 'Custo Total', field: 'total_cost', align: 'right', format: (val) => `R$ ${val.toFixed(2)}`, sortable: true },
  { name: 'user', label: 'Registrado por', field: (row: FuelLog) => row.user.full_name, align: 'left', sortable: true },
];

function openCreateDialog() {
  // Limpa o formulário
  formData.value = { vehicle_id: 0, odometer: 0, liters: 0, total_cost: 0 };
  isCreateDialogOpen.value = true;
}

async function handleSubmit() {
  try {
    await fuelLogStore.createFuelLog(formData.value);
    isCreateDialogOpen.value = false;
  } catch {
    // A store já notifica o erro
  }
}

onMounted(() => {
  // Carrega os dados necessários para a página
  void fuelLogStore.fetchFuelLogs();
  if (vehicleStore.vehicles.length === 0) {
    void vehicleStore.fetchAllVehicles();
  }
});
</script>