<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gerenciamento de Frota</h1>
      <q-btn
        v-if="authStore.isManager"
        @click="openCreateDialog"
        color="primary"
        icon="add"
        label="Adicionar Veículo"
        unelevated
      />
    </div>

    <q-card flat bordered>
      <q-table
        :rows="vehicleStore.vehicles"
        :columns="columns"
        row-key="id"
        :loading="vehicleStore.isLoading"
        no-data-label="Nenhum carro na frota"
      >
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="getStatusColor(props.value)" :label="props.value" />
          </q-td>
        </template>

        <template v-if="authStore.isManager" v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn @click="openEditDialog(props.row)" flat round dense icon="edit" class="q-mr-sm" />
            <q-btn @click="promptToDelete(props.row)" flat round dense icon="delete" color="negative" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isFormDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Veículo' : 'Novo Veículo' }}</div>
        </q-card-section>

        <q-form @submit.prevent="onFormSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input v-if="!isEditing" outlined v-model="formData.license_plate" label="Placa *" mask="AAA#A##" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Ano inválido']" />
            <q-select v-if="isEditing" outlined v-model="formData.status" :options="statusOptions" label="Status" />
            <q-input outlined v-model="formData.photo_url" label="URL da Foto" />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store'; // MUDANÇA 3: Importamos a authStore
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';

const $q = useQuasar();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore(); // E criamos a instância dela

const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingVehicleId = ref<number | null>(null);

const isEditing = computed(() => editingVehicleId.value !== null);
const statusOptions = Object.values(VehicleStatus);

const formData = ref<Partial<VehicleCreate & VehicleUpdate>>({});

// MUDANÇA 4: As colunas da tabela agora são 'computadas' e dinâmicas
const columns = computed<QTableColumn[]>(() => [
  { name: 'brand', label: 'Marca', field: 'brand', align: 'left', sortable: true },
  { name: 'model', label: 'Modelo', field: 'model', align: 'left', sortable: true },
  { name: 'license_plate', label: 'Placa', field: 'license_plate', align: 'center' },
  { name: 'year', label: 'Ano', field: 'year', align: 'center', sortable: true },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  // A coluna de Ações só é adicionada ao array se o usuário for um gestor
  ...(authStore.isManager ? [{ name: 'actions', label: 'Ações', field: 'actions', align: 'right' }] as QTableColumn[] : [])
]);

function getStatusColor(status: VehicleStatus) {
  const colorMap = { [VehicleStatus.AVAILABLE]: 'positive', [VehicleStatus.IN_USE]: 'orange-8', [VehicleStatus.MAINTENANCE]: 'negative' };
  return colorMap[status];
}

function resetForm() {
  editingVehicleId.value = null;
  formData.value = { brand: '', model: '', license_plate: '', year: new Date().getFullYear(), photo_url: '' };
}

function openCreateDialog() {
  resetForm();
  isFormDialogOpen.value = true;
}

function openEditDialog(vehicle: Vehicle) {
  resetForm();
  editingVehicleId.value = vehicle.id;
  formData.value = { ...vehicle };
  isFormDialogOpen.value = true;
}

async function onFormSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value && editingVehicleId.value) {
      const updatePayload: VehicleUpdate = {};
      if (formData.value.brand) updatePayload.brand = formData.value.brand;
      if (formData.value.model) updatePayload.model = formData.value.model;
      if (formData.value.year) updatePayload.year = formData.value.year;
      if (formData.value.status) updatePayload.status = formData.value.status;
      if (formData.value.photo_url !== undefined) {
        updatePayload.photo_url = formData.value.photo_url;
      }
      await vehicleStore.updateVehicle(editingVehicleId.value, updatePayload);
    } else {
      await vehicleStore.addNewVehicle(formData.value as VehicleCreate);
    }
    isFormDialogOpen.value = false;
  } catch {
    console.log('O formulário não fecha pois a operação falhou.');
  } finally {
    isSubmitting.value = false;
  }
}

function promptToDelete(vehicle: Vehicle) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja excluir o veículo ${vehicle.brand} ${vehicle.model} (Placa: ${vehicle.license_plate})? Esta ação não pode ser desfeita.`,
    persistent: true,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
    cancel: { label: 'Cancelar', flat: true }
  }).onOk(() => {
    void vehicleStore.deleteVehicle(vehicle.id);
  });
}

onMounted(async () => {
  await vehicleStore.fetchAllVehicles();
});
</script>