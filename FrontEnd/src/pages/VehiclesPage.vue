<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">{{ terminologyStore.vehiclePageTitle }}</h1>
      <div class="row items-center q-gutter-md">
        <q-input
          outlined dense debounce="300" v-model="searchTerm"
          :placeholder="`Buscar por ${terminologyStore.plateOrIdentifierLabel.toLowerCase()}, marca...`"
          style="width: 250px"
        >
          <template v-slot:append><q-icon name="search" /></template>
        </q-input>
        <q-btn
          v-if="authStore.isManager" @click="openCreateDialog" color="primary"
          icon="add" :label="terminologyStore.addVehicleButtonLabel" unelevated
        />
      </div>
    </div>

    <div v-if="vehicleStore.isLoading" class="row q-col-gutter-md">
      <div v-for="n in 8" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered><q-skeleton height="180px" square /></q-card>
      </div>
    </div>

    <div v-else-if="vehicleStore.vehicles && vehicleStore.vehicles.length > 0" class="row q-col-gutter-md">
      <div v-for="vehicle in vehicleStore.vehicles" :key="vehicle.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered class="column no-wrap full-height">
          <q-card-section class="row items-center q-pa-md">
            <q-icon :name="getVehicleIcon(vehicle)" color="primary" size="32px" class="q-mr-md" />
            <div class="col ellipsis">
              <div class="text-subtitle1 text-weight-bold ellipsis">{{ vehicle.brand }} {{ vehicle.model }}</div>
              <div class="text-caption text-grey-8">{{ vehicle.license_plate || vehicle.identifier }} - {{ vehicle.year }}</div>
            </div>
          </q-card-section>
          <q-space />
          <q-separator />
          <q-card-actions class="row justify-between items-center q-pa-sm">
             <q-badge :color="getStatusColor(vehicle.status)" text-color="white">{{ vehicle.status }}</q-badge>
             <div class="text-caption text-weight-medium text-grey-8">{{ vehicle.current_km ?? vehicle.current_engine_hours ?? 0 }} {{ terminologyStore.distanceUnit }}</div>
            <div v-if="authStore.isManager">
              <q-btn @click="openEditDialog(vehicle)" flat round dense icon="edit" :title="terminologyStore.editButtonLabel" />
              <q-btn @click="promptToDelete(vehicle)" flat round dense icon="delete" color="negative" title="Excluir" />
            </div>
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <div v-else class="full-width row flex-center text-primary q-gutter-sm q-pa-xl">
      <q-icon name="add_circle_outline" size="3em" />
      <span class="text-h6">Nenhum {{ terminologyStore.vehicleNoun.toLowerCase() }} encontrado</span>
      <q-btn @click="openCreateDialog" v-if="authStore.isManager" unelevated color="primary" :label="`Adicionar primeiro ${terminologyStore.vehicleNoun.toLowerCase()}`" class="q-ml-lg" />
    </div>

    <div class="flex flex-center q-mt-lg" v-if="pagination.rowsNumber > pagination.rowsPerPage">
       <q-pagination
        v-model="pagination.page"
        :max="Math.ceil(pagination.rowsNumber / pagination.rowsPerPage)"
        @update:model-value="onPageChange"
        direction-links boundary-links icon-first="skip_previous"
        icon-last="skip_next" icon-prev="fast_rewind" icon-next="fast_forward"
      />
    </div>

    <q-dialog v-model="isFormDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? terminologyStore.editButtonLabel : terminologyStore.newButtonLabel }}</div>
        </q-card-section>
        <q-form @submit.prevent="onFormSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input
              v-if="!isEditing" outlined v-model="formData.license_plate"
              :label="terminologyStore.plateOrIdentifierLabel + ' *'"
              :mask="authStore.userSector !== 'agronegocio' ? 'AAA#A##' : ''"
              :rules="[val => !!val || 'Campo obrigatório']"
            />
            <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Ano inválido']" />
            <q-input v-if="authStore.userSector === 'agronegocio'" outlined v-model.number="formData.current_engine_hours" type="number" label="Horas de Motor Atuais" step="0.1" />
            <q-input v-else outlined v-model.number="formData.current_km" type="number" label="KM Inicial" />
            <q-select v-if="isEditing" outlined v-model="formData.status" :options="statusOptions" label="Status" />
            <q-input outlined v-model="formData.photo_url" label="URL da Foto" />
            <q-separator class="q-my-lg" />
            <div class="text-subtitle1 text-weight-medium">Dados de Manutenção</div>
            <q-input outlined v-model.number="formData.next_maintenance_km" type="number" :label="`Próxima Revisão (${terminologyStore.distanceUnit})`" clearable />
            <q-input outlined v-model="formData.next_maintenance_date" mask="##/##/####" label="Próxima Revisão (Data)" clearable>
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="formData.next_maintenance_date" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input outlined v-model="formData.maintenance_notes" type="textarea" label="Anotações de Manutenção" autogrow />
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
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';

const $q = useQuasar();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();

const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingVehicleId = ref<number | null>(null);
const isEditing = computed(() => editingVehicleId.value !== null);
const statusOptions = Object.values(VehicleStatus);
const formData = ref<Partial<Vehicle>>({});

// CORRIGIDO: Função de reset mais completa
function resetForm() {
  editingVehicleId.value = null;
  formData.value = {
    brand: '', model: '', year: new Date().getFullYear(),
    license_plate: '', identifier: '', photo_url: null, status: VehicleStatus.AVAILABLE,
    current_km: 0, current_engine_hours: 0,
    next_maintenance_date: null, next_maintenance_km: null, maintenance_notes: ''
  };
}

function openCreateDialog() {
  resetForm();
  isFormDialogOpen.value = true;
}

function openEditDialog(vehicle: Vehicle) {
  editingVehicleId.value = vehicle.id;
  formData.value = {
    ...vehicle,
    next_maintenance_date: vehicle.next_maintenance_date
      ? vehicle.next_maintenance_date.split('-').reverse().join('/')
      : null,
  };
  isFormDialogOpen.value = true;
}

async function onFormSubmit() {
  isSubmitting.value = true;
  try {
    const payload = { ...formData.value };

    if (payload.next_maintenance_date && typeof payload.next_maintenance_date === 'string' && payload.next_maintenance_date.includes('/')) {
      payload.next_maintenance_date = payload.next_maintenance_date.split('/').reverse().join('-');
    }

    if (authStore.userSector === 'agronegocio' && payload.license_plate) {
      payload.identifier = payload.license_plate;
      delete payload.license_plate;
    }

    if (isEditing.value && editingVehicleId.value) {
      await vehicleStore.updateVehicle(editingVehicleId.value, payload as VehicleUpdate);
    } else {
      await vehicleStore.addNewVehicle(payload as VehicleCreate);
    }
    isFormDialogOpen.value = false;
  } catch (error) {
    console.error("Falha ao submeter formulário:", error);
  } finally {
    isSubmitting.value = false;
  }
}

const searchTerm = ref('');
const pagination = ref({ page: 1, rowsPerPage: 8, rowsNumber: 0 });
async function fetchFromServer(page: number, rowsPerPage: number, search: string) {
  await vehicleStore.fetchAllVehicles({ page, rowsPerPage, search });
  pagination.value.rowsNumber = vehicleStore.totalItems;
}
function onPageChange(page: number) {
  pagination.value.page = page;
  void fetchFromServer(page, pagination.value.rowsPerPage, searchTerm.value);
}
watch(searchTerm, (newValue) => {
  pagination.value.page = 1;
  void fetchFromServer(1, pagination.value.rowsPerPage, newValue);
});
onMounted(() => {
  void fetchFromServer(pagination.value.page, pagination.value.rowsPerPage, searchTerm.value);
});

function getVehicleIcon(vehicle: Vehicle): string {
  if (authStore.userSector === 'agronegocio') return 'agriculture';
  if (authStore.userSector === 'construcao_civil') return 'construction';
  if (vehicle.model) {
    const lowerModel = vehicle.model.toLowerCase();
    if (lowerModel.includes('strada') || lowerModel.includes('fiorino')) {
      return 'local_shipping';
    }
  }
  return 'directions_car';
}

function getStatusColor(status: VehicleStatus): string {
  // Adicionamos o tipo Record<VehicleStatus, string> para o TypeScript entender a estrutura
  const colorMap: Record<VehicleStatus, string> = {
    [VehicleStatus.AVAILABLE]: 'positive',
    [VehicleStatus.IN_USE]: 'orange-8', // Corrigido o erro de digitação
    [VehicleStatus.MAINTENANCE]: 'negative'
  };
  return colorMap[status] || 'grey'; // Adicionamos um fallback para segurança
}

function promptToDelete(vehicle: Vehicle) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem a certeza que deseja excluir ${terminologyStore.vehicleNoun.toLowerCase()} ${vehicle.brand} ${vehicle.model}?`,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
    cancel: { label: 'Cancelar', flat: true },
  }).onOk(() => {
    void vehicleStore.deleteVehicle(vehicle.id, {
      page: pagination.value.page, rowsPerPage: pagination.value.rowsPerPage, search: searchTerm.value,
    });
  });
}
</script>