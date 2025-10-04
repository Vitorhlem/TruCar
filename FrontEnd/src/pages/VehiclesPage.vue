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

    <!-- SKELETON LOADING -->
    <div v-if="vehicleStore.isLoading && vehicleStore.vehicles.length === 0" class="row q-col-gutter-md">
      <div v-for="n in 8" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered>
          <q-skeleton height="160px" square />
          <q-card-section><q-skeleton type="text" class="text-subtitle1" /></q-card-section>
          <q-separator /><q-card-section><q-skeleton type="text" width="70%" /></q-card-section>
        </q-card>
      </div>
    </div>

    <!-- VEHICLE CARDS -->
    <div v-else-if="vehicleStore.vehicles.length > 0" class="row q-col-gutter-md">
      <div v-for="vehicle in vehicleStore.vehicles" :key="vehicle.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card class="vehicle-card column no-wrap full-height" @click="goToVehicleDetails(vehicle, 'details')">
          <q-img :src="vehicle.photo_url ?? undefined" height="160px" fit="cover" class="bg-grey-3">
            <template v-slot:error>
              <div class="absolute-full flex flex-center bg-primary text-white">
                <q-icon :name="getVehicleIcon(vehicle)" size="48px" />
              </div>
            </template>
            <q-badge :color="getStatusColor(vehicle.status)" :label="vehicle.status" class="absolute-top-right q-ma-sm" />
          </q-img>

          <q-card-section>
            <div class="flex items-start no-wrap">
              <div class="col">
                <div class="text-subtitle1 text-weight-bold ellipsis">{{ vehicle.brand }} {{ vehicle.model }}</div>
                <div class="text-caption text-grey-8">{{ vehicle.license_plate || vehicle.identifier }} &bull; {{ vehicle.year }}</div>
              </div>
              <div v-if="authStore.isManager" class="col-auto no-wrap">
                <q-icon v-if="vehicle.telemetry_device_id" name="sensors" color="positive" size="20px" class="q-mr-xs">
                  <q-tooltip>Telemetria Ativa</q-tooltip>
                </q-icon>
                <!-- NOVO BOTÃO DE CUSTOS -->
                <q-btn @click.stop="goToVehicleDetails(vehicle, 'costs')" flat round dense icon="receipt_long">
                  <q-tooltip>Ver Custos</q-tooltip>
                </q-btn>
                <q-btn @click.stop="openEditDialog(vehicle)" flat round dense icon="edit"><q-tooltip>Editar</q-tooltip></q-btn>
                <q-btn @click.stop="promptToDelete(vehicle)" flat round dense icon="delete" color="negative"><q-tooltip>Excluir</q-tooltip></q-btn>
              </div>
            </div>
          </q-card-section>

          <q-space />
          <q-separator />

          <q-card-section class="q-py-sm">
            <div class="flex justify-between items-center text-caption text-grey-8">
              <span>{{ terminologyStore.distanceUnit === 'km' ? 'Odómetro' : 'Horímetro' }}</span>
              <span class="text-weight-bold text-white-9">{{
                formatDistance(
                  terminologyStore.distanceUnit === 'km' ? vehicle.current_km : vehicle.current_engine_hours,
                  terminologyStore.distanceUnit as 'km' | 'Horas'
                )
              }}</span>
            </div>
            <div v-if="vehicle.next_maintenance_km || vehicle.next_maintenance_date" class="flex justify-between items-center text-caption text-grey-8 q-mt-xs">
              <span>Próx. Revisão</span>
              <span class="text-weight-bold text-black ellipsis text-right" style="max-width: 60%;">
                {{ vehicle.next_maintenance_km ? `${vehicle.next_maintenance_km.toLocaleString('pt-BR')} ${terminologyStore.distanceUnit}` : '' }}
                {{ vehicle.next_maintenance_km && vehicle.next_maintenance_date ? ' ou ' : '' }}
                {{ vehicle.next_maintenance_date ? (new Date(vehicle.next_maintenance_date + 'T00:00:00')).toLocaleDateString('pt-BR') : '' }}
              </span>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- EMPTY STATE -->
    <div v-else class="full-width row flex-center text-primary q-gutter-sm q-pa-xl">
      <q-icon name="add_circle_outline" size="3em" />
      <span class="text-h6">Nenhum {{ terminologyStore.vehicleNoun.toLowerCase() }} encontrado</span>
      <q-btn @click="openCreateDialog" v-if="authStore.isManager" unelevated color="primary" :label="`Adicionar primeiro ${terminologyStore.vehicleNoun.toLowerCase()}`" class="q-ml-lg" />
    </div>

    <!-- PAGINATION -->
    <div class="flex flex-center q-mt-lg" v-if="pagination.rowsNumber > pagination.rowsPerPage">
      <q-pagination v-model="pagination.page" :max="Math.ceil(pagination.rowsNumber / pagination.rowsPerPage)" @update:model-value="onPageChange" direction-links boundary-links icon-first="skip_previous" icon-last="skip_next" icon-prev="fast_rewind" icon-next="fast_forward" />
    </div>

    <!-- FORM DIALOG -->
    <q-dialog v-model="isFormDialogOpen">
        <q-card style="width: 500px; max-width: 90vw;" :dark="$q.dark.isActive">
          <q-card-section>
            <div class="text-h6">{{ isEditing ? terminologyStore.editButtonLabel : terminologyStore.newButtonLabel }}</div>
          </q-card-section>
          <q-form @submit.prevent="onFormSubmit">
            <q-card-section class="q-gutter-y-md">
              <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-input v-if="!isEditing" outlined v-model="formData.license_plate" :label="terminologyStore.plateOrIdentifierLabel + ' *'" :mask="authStore.userSector !== 'agronegocio' ? 'AAA#A##' : ''" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Ano inválido']" />
              <q-input v-if="authStore.userSector === 'agronegocio'" outlined v-model.number="formData.current_engine_hours" type="number" label="Horas de Motor Atuais" step="0.1" />
              <q-input v-else outlined v-model.number="formData.current_km" type="number" label="KM Inicial" />
              <q-select v-if="isEditing" outlined v-model="formData.status" :options="statusOptions" label="Status" />
              <q-file v-model="photoFile" label="Carregar Foto do Veículo" outlined clearable accept=".jpg, image/*">
                <template v-slot:prepend><q-icon name="attach_file" /></template>
                <template v-if="formData.photo_url && !photoFile" v-slot:append>
                  <q-avatar square><img :src="formData.photo_url ?? undefined" alt="Foto atual" /></q-avatar>
                </template>
              </q-file>
              <q-separator class="q-my-md" />
              <div class="text-subtitle1 text-weight-medium">Telemetria (Opcional)</div>
              <q-input outlined v-model="formData.telemetry_device_id" label="ID do Dispositivo de Telemetria" hint="Ex: TRATOR-001. Este ID conecta o maquinário ao dispositivo físico." />
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
            <q-card-actions align="right" class="q-pa-md">
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
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';
import api from 'src/services/api';
import axios from 'axios';

const $q = useQuasar();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const router = useRouter();

const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingVehicleId = ref<number | null>(null);
const isEditing = computed(() => editingVehicleId.value !== null);
const statusOptions = Object.values(VehicleStatus);
const formData = ref<Partial<Vehicle>>({});
const photoFile = ref<File | null>(null);

function goToVehicleDetails(vehicle: Vehicle, tab = 'details') {
  void router.push({ 
    name: 'vehicle-details', 
    params: { id: vehicle.id },
    query: { tab: tab }
  });
}

function resetForm() {
  editingVehicleId.value = null;
  formData.value = {
    brand: '', model: '', year: new Date().getFullYear(),
    license_plate: '', identifier: '', photo_url: null, status: VehicleStatus.AVAILABLE,
    current_km: 0, current_engine_hours: 0,
    next_maintenance_date: null, next_maintenance_km: null, maintenance_notes: '',
    telemetry_device_id: null,
  };
  photoFile.value = null;
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
  photoFile.value = null;
  isFormDialogOpen.value = true;
}

async function uploadPhoto(file: File): Promise<string | null> {
  try {
    const fd = new FormData();
    fd.append('file', file);
    const response = await api.post('/upload-photo', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data.file_url;
  } catch {
    $q.notify({ type: 'negative', message: 'Falha ao carregar a foto.' });
    return null;
  }
}

async function onFormSubmit() {
  isSubmitting.value = true;
  try {
    const payload = { ...formData.value };

    if (photoFile.value) {
      const photoUrl = await uploadPhoto(photoFile.value);
      if (!photoUrl) { isSubmitting.value = false; return; }
      payload.photo_url = photoUrl;
    }

    if (payload.next_maintenance_date?.includes('/')) {
      payload.next_maintenance_date = payload.next_maintenance_date.split('/').reverse().join('-');
    }

    if (authStore.userSector === 'agronegocio' && payload.license_plate) {
      payload.identifier = payload.license_plate;
      delete payload.license_plate;
    }

    const currentFetchParams = {
      page: pagination.value.page,
      rowsPerPage: pagination.value.rowsPerPage,
      search: searchTerm.value,
    };

    if (isEditing.value && editingVehicleId.value) {
      await vehicleStore.updateVehicle(editingVehicleId.value, payload as VehicleUpdate, currentFetchParams);
    } else {
      await vehicleStore.addNewVehicle(payload as VehicleCreate, currentFetchParams);
    }

    isFormDialogOpen.value = false;
  } catch (error) {
    let errorMessage = 'Falha ao salvar o veículo. Verifique os dados.';
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    $q.notify({ type: 'negative', message: errorMessage });
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

watch(searchTerm, () => {
  pagination.value.page = 1;
  void fetchFromServer(1, pagination.value.rowsPerPage, searchTerm.value);
});

onMounted(() => {
  void fetchFromServer(pagination.value.page, pagination.value.rowsPerPage, searchTerm.value);
});

function formatDistance(value: number | null | undefined, unit: 'km' | 'Horas'): string {
  const numValue = value ?? 0;
  const formattedValue = numValue.toLocaleString('pt-BR', {
    minimumFractionDigits: unit === 'Horas' ? 1 : 0,
    maximumFractionDigits: unit === 'Horas' ? 1 : 0,
  });
  return `${formattedValue} ${unit}`;
}

function getVehicleIcon(vehicle: Vehicle): string {
  if (authStore.userSector === 'agronegocio') return 'agriculture';
  if (authStore.userSector === 'construcao_civil') return 'construction';
  if (vehicle.model) {
    const lowerModel = vehicle.model.toLowerCase();
    if (lowerModel.includes('strada') || lowerModel.includes('fiorino') || lowerModel.includes('caminhonete')) return 'local_shipping';
    if (lowerModel.includes('carro') || lowerModel.includes('sedan') || lowerModel.includes('hatch')) return 'directions_car';
    if (lowerModel.includes('moto') || lowerModel.includes('motocicleta')) return 'two_wheeler';
  }
  return 'directions_car';
}

function getStatusColor(status: VehicleStatus): string {
  const colorMap: Record<VehicleStatus, string> = {
    [VehicleStatus.AVAILABLE]: 'positive',
    [VehicleStatus.IN_USE]: 'orange-8',
    [VehicleStatus.MAINTENANCE]: 'negative'
  };
  return colorMap[status] || 'grey';
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

<style scoped lang="scss">
.vehicle-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}
</style>
