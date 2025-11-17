<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h5 text-weight-bold q-my-none">Registros de Abastecimento</h1>
        <div class="text-subtitle1 text-grey-7">Gerencie abastecimentos manuais e integrados.</div>
      </div>
      <div class="q-gutter-sm">
        <q-btn
          @click="handleSync"
          color="secondary"
          icon="sync"
          label="Sincronizar com Provedor"
          :loading="fuelLogStore.isLoading"
          unelevated
        >
          <q-tooltip>Buscar novos abastecimentos do provedor do cartão</q-tooltip>
        </q-btn>
        <q-btn
          @click="openCreateDialog"
          color="primary"
          icon="add"
          label="Registrar Manualmente"
          unelevated
        />
      </div>
    </div>

    <q-card flat bordered>
      <q-table
        :rows="fuelLogStore.fuelLogs"
        :columns="columns"
        row-key="id"
        :loading="fuelLogStore.isLoading"
        no-data-label="Nenhum abastecimento registrado"
      >
        <template v-slot:body-cell-verification_status="props">
          <q-td :props="props">
            <q-chip
              :color="getVerificationStatusProps(props.row.verification_status).color"
              :icon="getVerificationStatusProps(props.row.verification_status).icon"
              :label="getVerificationStatusProps(props.row.verification_status).label"
              text-color="white"
              square
              size="sm"
              class="text-weight-bold"
            />
          </q-td>
        </template>

        <template v-slot:body-cell-source="props">
          <q-td :props="props">
            <q-chip
              :label="props.row.source === 'INTEGRATION' ? 'Integração' : 'Manual'"
              :icon="props.row.source === 'INTEGRATION' ? 'cloud_sync' : 'edit'"
              size="sm"
              outline
              :color="props.row.source === 'INTEGRATION' ? 'blue-7' : 'grey-7'"
            />
          </q-td>
        </template>
        
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <div v-if="isManager" class="q-gutter-x-sm">
              <q-btn
                icon="edit"
                color="info"
                dense
                flat
                round
                @click="onEditLog(props.row)"
              >
                <q-tooltip>Editar Registro</q-tooltip>
              </q-btn>
              <q-btn
                icon="delete"
                color="negative"
                dense
                flat
                round
                @click="onDeleteLog(props.row.id)"
              >
                <q-tooltip>Excluir Registro</q-tooltip>
              </q-btn>
            </div>
            <span v-else class="text-grey-6">N/A</span>
          </q-td>
        </template>
        
      </q-table>
    </q-card>

    <q-dialog v-model="isCreateDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
           <div class="text-h6">{{ editingLogId ? 'Editar Registro' : 'Novo Registro de Abastecimento' }}</div>
        </q-card-section>
        
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-select
              outlined
              v-model="formData.vehicle_id"
              :options="vehicleOptions"
              :label="`${terminologyStore.vehicleNoun} *`" emit-value map-options
              :rules="[val => val > 0 || 'Selecione um veículo']"
              @update:model-value="handleVehicleSelect"
            />
            <q-input
              outlined
              v-model.number="formData.odometer"
              type="number"
              :label="`${terminologyStore.odometerLabel} *`"
              :rules="[val => (val !== null && val !== undefined && val >= 0) || 'Valor inválido']"
            />
            <q-input outlined v-model.number="formData.liters" type="number" label="Litros Abastecidos *" step="0.01" :rules="[val => val > 0 || 'Litros devem ser maior que 0']" />
            <q-input outlined v-model.number="formData.total_cost" type="number" label="Custo Total (R$) *" prefix="R$" step="0.01" :rules="[val => val > 0 || 'Custo deve ser maior que 0']" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn
              type="submit"
              unelevated
              color="primary"
              :label="editingLogId ? 'Atualizar Registro' : 'Salvar Registro'" :loading="fuelLogStore.isLoading"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useFuelLogStore } from 'stores/fuel-log-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import type { QTableProps } from 'quasar';
import type { FuelLog, FuelLogCreate, FuelLogUpdate } from 'src/models/fuel-log-models';

const fuelLogStore = useFuelLogStore();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const $q = useQuasar();

const isCreateDialogOpen = ref(false);
const editingLogId = ref<number | null>(null);

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


const isManager = computed(() => {
  if (!authStore.user) return false;
  return ['cliente_ativo', 'cliente_demo'].includes(authStore.user.role);
});

const columns: QTableProps['columns'] = [
  { name: 'verification_status', label: 'Status', field: 'verification_status', align: 'center', sortable: true },
  { name: 'date', label: 'Data', field: 'timestamp', format: (val) => new Date(val).toLocaleDateString('pt-BR'), align: 'left', sortable: true },
  { name: 'vehicle', label: 'Veículo', field: (row: FuelLog) => `${row.vehicle.brand} ${row.vehicle.model}`, align: 'left', sortable: true },
  { name: 'liters', label: 'Litros', field: 'liters', align: 'right', format: (val) => val.toFixed(2), sortable: true },
  { name: 'cost', label: 'Custo Total', field: 'total_cost', align: 'right', format: (val) => `R$ ${val.toFixed(2)}`, sortable: true },
  { name: 'user', label: 'Registrado por', field: (row: FuelLog) => row.user.full_name, align: 'left', sortable: true },
  { name: 'source', label: 'Fonte', field: 'source', align: 'center', sortable: true },
  { name: 'actions', label: 'Ações', field: '', align: 'center' },
];


function getVerificationStatusProps(status: FuelLog['verification_status']) {
  switch (status) {
    case 'VERIFIED':
      return { color: 'positive', icon: 'check_circle', label: 'Verificado' };
    case 'SUSPICIOUS':
      return { color: 'negative', icon: 'warning', label: 'Suspeito' };
    case 'PENDING':
      return { color: 'grey-7', icon: 'hourglass_empty', label: 'Pendente' };
    case 'UNVERIFIED':
      return { color: 'info', icon: 'info', label: 'Não Verificado' };
    default:
      return { color: 'grey', icon: 'help', label: 'Desconhecido' };
  }
}


function handleVehicleSelect(vehicleId: number) {

  if (!vehicleId || editingLogId.value) return;

  const selectedVehicle = vehicleStore.vehicles.find(v => v.id === vehicleId);
  
  if (selectedVehicle) {

    formData.value.odometer = selectedVehicle.current_km ?? 0;
  }
}


function openCreateDialog() {
  editingLogId.value = null; 
  formData.value = { vehicle_id: 0, odometer: 0, liters: 0, total_cost: 0 };
  isCreateDialogOpen.value = true;
}


function onEditLog(log: FuelLog) {
  editingLogId.value = log.id;
  
  formData.value = {
    vehicle_id: log.vehicle.id,
    odometer: log.odometer,
    liters: log.liters,
    total_cost: log.total_cost,
  };
  
  isCreateDialogOpen.value = true;
}


async function handleSubmit() {
  console.log('Botão Salvar/Atualizar clicado. Iniciando handleSubmit.');
  
  try {
    if (editingLogId.value) {
      console.log('Modo: EDIÇÃO. ID:', editingLogId.value, 'Dados:', formData.value);
      await fuelLogStore.updateFuelLog(editingLogId.value, formData.value as FuelLogUpdate);
    } else {
      console.log('Modo: CRIAÇÃO. Dados:', formData.value);
      await fuelLogStore.createFuelLog(formData.value);
    }
    isCreateDialogOpen.value = false;
    editingLogId.value = null;
    
  } catch (error) {
    console.error('Erro ao salvar o registro de abastecimento:', error);

  }
}


async function handleSync() {
  await fuelLogStore.syncWithProvider();
}


function onDeleteLog(logId: number) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: 'Tem certeza que deseja excluir este registro de abastecimento? Esta ação não pode ser desfeita.',
    color: 'negative',
    persistent: true,
    cancel: {
      label: 'Cancelar',
      flat: true,
    },
    ok: {
      label: 'Excluir',
      color: 'negative',
      unelevated: true,
    },
  }).onOk(() => {
    void fuelLogStore.deleteFuelLog(logId);
  });
}


onMounted(() => {
  void fuelLogStore.fetchFuelLogs();
  if (vehicleStore.vehicles.length === 0) {
    void vehicleStore.fetchAllVehicles();
  }
});
</script>