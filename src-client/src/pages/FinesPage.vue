<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">{{ pageTitle }}</h1>
        <div class="text-subtitle1 text-grey-7">{{ pageSubtitle }}</div>
      </div>
      <q-btn v-if="authStore.isManager || authStore.isDriver" color="primary" icon="add" label="Registrar Multa" unelevated @click="openDialog()" />
    </div>

    <q-card flat bordered>
      <q-table
        :rows="fineStore.fines"
        :columns="tableColumns"
        row-key="id"
        :loading="fineStore.isLoading"
        no-data-label="Nenhuma multa registrada."
        flat
      >
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-chip :color="getStatusColor(props.value)" text-color="white" dense square>{{ props.value }}</q-chip>
          </q-td>
        </template>
        
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn v-if="authStore.isManager" flat round dense icon="edit" @click="openDialog(props.row)" />
            <q-btn v-if="authStore.isManager" flat round dense icon="delete" color="negative" @click="confirmDelete(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isDialogOpen">
      <q-card style="width: 600px; max-width: 90vw;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ isEditing ? 'Editar Multa' : 'Registrar Nova Multa' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input v-model="formData.description" label="Descrição da Multa *" outlined :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input v-model="formData.date" label="Data da Infração *" outlined readonly hint="Selecione a data no calendário">
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover><q-date v-model="formData.date" mask="YYYY-MM-DD" /></q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input v-model.number="formData.value" label="Valor (R$) *" outlined type="number" prefix="R$" :rules="[val => val > 0 || 'Valor deve ser positivo']"/>
            <q-select v-model="formData.status" label="Status *" outlined :options="statusOptions" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-select v-model="formData.vehicle_id" label="Veículo *" outlined :options="vehicleOptions" emit-value map-options :rules="[val => !!val || 'Campo obrigatório']" />
            <q-select v-if="authStore.isManager" v-model="formData.driver_id" label="Motorista (Opcional)" outlined :options="driverOptions" emit-value map-options clearable />
            <q-input v-model="formData.infraction_code" label="Código da Infração (Opcional)" outlined />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" color="primary" :label="isEditing ? 'Salvar Alterações' : 'Salvar Multa'" unelevated :loading="fineStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useFineStore } from 'stores/fine-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useUserStore } from 'stores/user-store';
import { useAuthStore } from 'stores/auth-store';
import type { Fine, FineCreate, FineUpdate, FineStatus } from 'src/models/fine-models';
import type { QTableColumn } from 'quasar';
import { format } from 'date-fns';

const $q = useQuasar();
const fineStore = useFineStore();
const vehicleStore = useVehicleStore();
const userStore = useUserStore();
const authStore = useAuthStore();

const isDialogOpen = ref(false);
const editingFine = ref<Fine | null>(null);
const isEditing = computed(() => !!editingFine.value);
const formData = ref<Partial<FineCreate>>({});
const statusOptions: FineStatus[] = ["Pendente", "Paga", "Em Recurso", "Cancelada"];


const pageTitle = computed(() => authStore.isDriver ? 'Minhas Multas' : 'Gestão de Multas');
const pageSubtitle = computed(() => authStore.isDriver ? 'Consulte suas infrações registradas.' : 'Registre e controle as infrações da sua frota.');

const vehicleOptions = computed(() => vehicleStore.vehicles.map(v => ({
  label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`,
  value: v.id,
})));

const driverOptions = computed(() => userStore.users.filter(u => u.role === 'driver').map(d => ({
  label: d.full_name,
  value: d.id,
})));

const baseColumns: QTableColumn<Fine>[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => format(new Date(val.replace(/-/g, '/')), 'dd/MM/yyyy'), align: 'left', sortable: true },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left' },
  { name: 'vehicle', label: 'Veículo', field: row => row.vehicle ? `${row.vehicle.brand} ${row.vehicle.model}` : 'N/A', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'value', label: 'Valor', field: 'value', format: val => val ? val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'R$ 0,00', align: 'right', sortable: true },
];


const tableColumns = computed<QTableColumn<Fine>[]>(() => {
  if (authStore.isManager) {
    const driverColumn: QTableColumn<Fine> = { name: 'driver', label: 'Motorista', field: (row: Fine) => row.driver?.full_name || 'Não identificado', align: 'left' };
    const actionsColumn: QTableColumn<Fine> = { name: 'actions', label: 'Ações', field: () => '', align: 'right' };
    
    return [
      ...baseColumns.slice(0, 3),
      driverColumn,
      ...baseColumns.slice(3),
      actionsColumn,
    ];
  }
  return baseColumns;
});


const getStatusColor = (status: FineStatus) => {
  const colorMap: Record<FineStatus, string> = { 'Pendente': 'orange', 'Paga': 'positive', 'Em Recurso': 'info', 'Cancelada': 'grey' };
  return colorMap[status] || 'primary';
}

function openDialog(fine: Fine | null = null) {
  if (fine && authStore.isManager) {
    editingFine.value = fine;
    formData.value = {
      description: fine.description,
      date: fine.date,
      value: fine.value,
      status: fine.status,
      vehicle_id: fine.vehicle_id,
      driver_id: fine.driver_id,
      infraction_code: fine.infraction_code,
    };
  } else {
    editingFine.value = null;
    formData.value = { 
      status: "Pendente", 
      date: format(new Date(), 'yyyy-MM-dd'),
      driver_id: authStore.isDriver ? authStore.user?.id ?? null : null
    };
  }
  isDialogOpen.value = true;
}

async function handleSubmit() {
  let success = false;
  if (isEditing.value && editingFine.value) {
    if (!formData.value.description || !formData.value.date || !formData.value.value || !formData.value.status || !formData.value.vehicle_id) {
      $q.notify({ type: 'negative', message: 'Por favor, preencha todos os campos obrigatórios.' });
      return;
    }
    const payload: FineUpdate = {
      description: formData.value.description,
      date: formData.value.date,
      value: formData.value.value,
      status: formData.value.status,
      vehicle_id: formData.value.vehicle_id,
      driver_id: formData.value.driver_id || null,
      infraction_code: formData.value.infraction_code || null,
    };
    success = await fineStore.updateFine(editingFine.value.id, payload);
  } else {
    if (authStore.isDriver) {
      formData.value.driver_id = authStore.user?.id ?? null;
    }
    success = await fineStore.createFine(formData.value as FineCreate);
  }
  
  if (success) {
    isDialogOpen.value = false;
  }
}

function confirmDelete(fine: Fine) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja excluir a multa "${fine.description}"?`,
    cancel: true,
    persistent: true,
    ok: { label: 'Excluir', color: 'negative', unelevated: true }
  }).onOk(() => {
    void fineStore.deleteFine(fine.id);
  });
}

onMounted(() => {
  void fineStore.fetchFines();
  
  if (vehicleStore.vehicles.length === 0) {
    void vehicleStore.fetchAllVehicles({ rowsPerPage: 9999 });
  }
  
  if (authStore.isManager && userStore.users.length === 0) {
    void userStore.fetchAllUsers();
  }
});
</script>