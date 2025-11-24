<template>
  <q-page class="q-pa-md q-pa-lg-xl">
    
    <div class="row items-center justify-between q-mb-lg q-col-gutter-y-md">
      <div class="col-12 col-md-auto">
        <h1 class="text-h4 text-weight-bolder q-my-none text-primary flex items-center gap-sm">
          <q-icon name="garage" size="md" />
          {{ terminologyStore.vehiclePageTitle }}
        </h1>
        <div class="text-subtitle2 text-grey-7 q-mt-xs" :class="{ 'text-grey-5': $q.dark.isActive }">
          Gerencie e monitore toda a sua frota num só lugar
        </div>
      </div>

      <div class="col-12 col-md-auto row q-gutter-sm">
        <q-input
          outlined
          dense
          debounce="300"
          v-model="searchTerm"
          :placeholder="`Buscar ${terminologyStore.plateOrIdentifierLabel.toLowerCase()} ou modelo...`"
          class="search-input"
          :bg-color="$q.dark.isActive ? 'grey-9' : 'white'"
        >
          <template v-slot:prepend><q-icon name="search" /></template>
        </q-input>
        
        <div v-if="authStore.isManager" class="relative-position">
          <q-btn
            @click="openCreateDialog" 
            color="primary"
            icon="add" 
            :label="terminologyStore.addVehicleButtonLabel" 
            unelevated
            class="full-height"
            :disable="isVehicleLimitReached"
          />
          
          <q-tooltip 
            v-if="isVehicleLimitReached" 
            class="bg-negative text-body2 shadow-4" 
            anchor="bottom middle" 
            self="top middle"
            :offset="[10, 10]"
          >
            <div class="row items-center no-wrap">
                <q-icon name="lock" size="sm" class="q-mr-sm" />
                <div>
                    <div class="text-weight-bold">Limite de Frota Atingido</div>
                    <div class="text-caption">O plano Demo permite até {{ demoUsageLimitLabel }} veículos.</div>
                    <div class="text-caption q-mt-xs text-yellow-2 cursor-pointer" @click="showLimitUpgradeDialog">Clique para aumentar</div>
                </div>
            </div>
          </q-tooltip>
        </div>
      </div>
    </div>

    <div v-if="isDemo" class="q-mb-xl animate-fade">
      <q-card flat bordered class="demo-card-gradient">
        <q-card-section class="q-pa-md">
          <div class="row items-center justify-between">
            <div class="col-grow row items-center q-gutter-x-md">
              <q-circular-progress
                show-value
                font-size="12px"
                :value="usagePercentage"
                size="50px"
                :thickness="0.22"
                :color="usageColor"
                track-color="white"
                class="text-white q-my-xs"
              >
                {{ usagePercentage }}%
              </q-circular-progress>
              
              <div>
                <div class="text-subtitle2 text-uppercase text-white text-opacity-80">Uso do Plano Demo</div>
                <div class="text-h5 text-white text-weight-bold">
                  {{ demoUsageCount }} <span class="text-body1 text-white text-opacity-70">/ {{ demoUsageLimitLabel }} veículos</span>
                </div>
              </div>
            </div>
            
            <div class="col-auto">
               <q-btn flat dense color="white" icon="info" round>
                 <q-tooltip>Você cadastrou {{ usagePercentage }}% da sua frota permitida no plano Demo.</q-tooltip>
               </q-btn>
            </div>
          </div>
          <q-linear-progress :value="usagePercentage / 100" class="q-mt-sm rounded-borders" color="white" track-color="white-30" />
        </q-card-section>
      </q-card>
    </div>

    <div v-if="vehicleStore.isLoading && vehicleStore.vehicles.length === 0" class="row q-col-gutter-md">
      <div v-for="n in 8" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-white'">
          <q-skeleton height="180px" square />
          <q-card-section>
            <q-skeleton type="text" class="text-subtitle1" width="60%" />
            <q-skeleton type="text" class="text-caption" width="40%" />
          </q-card-section>
          <q-separator />
          <q-card-section class="row justify-between">
            <q-skeleton type="text" width="30%" />
            <q-skeleton type="text" width="30%" />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div v-else-if="vehicleStore.vehicles.length > 0" class="row q-col-gutter-md">
      <div v-for="vehicle in vehicleStore.vehicles" :key="vehicle.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
           class="column no-wrap full-height vehicle-card custom-border" 
           :class="{ 
             'vehicle-card-interactive': authStore.isManager,
             'bg-grey-10 border-grey-8': $q.dark.isActive,
             'bg-white': !$q.dark.isActive
           }"
           @click="handleCardClick(vehicle)"
           flat bordered
        >
          <div class="relative-position">
            <q-img :src="getImageUrl(vehicle.photo_url) ?? undefined" height="180px" fit="cover" class="bg-grey-3">
              <template v-slot:error>
                <div class="absolute-full flex flex-center bg-grey-3 text-grey-5" :class="{'bg-grey-9 text-grey-7': $q.dark.isActive}">
                  <q-icon :name="getVehicleIcon(vehicle)" size="56px" />
                </div>
              </template>
              
              <div class="absolute-bottom text-subtitle2 text-white p-2" style="background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);">
                 <div class="row items-center justify-between full-width">
                   <div class="text-weight-bold">{{ vehicle.year }}</div>
                   <div v-if="vehicle.telemetry_device_id" class="flex items-center">
                     <q-icon name="sensors" color="green-4" size="16px" class="q-mr-xs" />
                     <span class="text-caption text-green-3">Conectado</span>
                   </div>
                 </div>
              </div>
            </q-img>
            
            <q-badge 
              :color="getStatusColor(vehicle.status)" 
              class="absolute-top-right q-ma-sm shadow-2"
              rounded
              padding="xs sm"
            >
              {{ vehicle.status }}
            </q-badge>
          </div>

          <q-card-section class="col q-pb-none">
            <div class="text-overline text-grey-7 line-height-tight" :class="{'text-grey-5': $q.dark.isActive}">
              {{ vehicle.brand }}
            </div>
            <div class="text-h6 text-weight-bold ellipsis q-mb-xs">
              {{ vehicle.model }}
            </div>
            <div class="row items-center text-caption text-grey-8" :class="{'text-grey-4': $q.dark.isActive}">
               <q-icon name="pin" size="16px" class="q-mr-xs text-primary" />
               <span class="text-weight-medium">{{ vehicle.license_plate || vehicle.identifier }}</span>
            </div>
          </q-card-section>

          <q-space />
          
          <q-card-section class="q-pt-sm">
             <div class="row q-col-gutter-sm">
               <div class="col-6">
                 <div class="metric-box" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-1'">
                    <div class="text-caption text-grey-6 text-xs-custom">
                       {{ terminologyStore.distanceUnit.toLowerCase() === 'km' ? 'Odómetro' : 'Horímetro' }}
                    </div>
                    <div class="text-weight-bold text-primary text-body2">
                      {{ formatDistance(terminologyStore.distanceUnit.toLowerCase() === 'km' ? vehicle.current_km : vehicle.current_engine_hours, terminologyStore.distanceUnit as 'km' | 'Horas') }}
                    </div>
                 </div>
               </div>
               
               <div class="col-6" v-if="vehicle.next_maintenance_km || vehicle.next_maintenance_date">
                 <div class="metric-box" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-1'">
                    <div class="text-caption text-grey-6 text-xs-custom">Próx. Revisão</div>
                    <div class="text-weight-bold text-warning-9 text-body2 ellipsis">
                       {{ vehicle.next_maintenance_date ? (new Date(vehicle.next_maintenance_date + 'T00:00:00')).toLocaleDateString('pt-BR').slice(0,5) : (vehicle.next_maintenance_km ? `${(vehicle.next_maintenance_km/1000).toFixed(0)}k` : '--') }}
                    </div>
                 </div>
               </div>
             </div>
          </q-card-section>

          <q-separator :color="$q.dark.isActive ? 'grey-8' : 'grey-2'" />

          <q-card-actions align="right" class="q-px-md" v-if="authStore.isManager">
             <q-btn flat round dense size="sm" color="grey-6" icon="receipt_long" @click.stop="goToVehicleDetails(vehicle, 'costs')">
               <q-tooltip>Ver Custos</q-tooltip>
             </q-btn>
             <q-btn flat round dense size="sm" color="primary" icon="edit" @click.stop="openEditDialog(vehicle)">
               <q-tooltip>Editar</q-tooltip>
             </q-btn>
             <q-btn flat round dense size="sm" color="negative" icon="delete_outline" @click.stop="promptToDelete(vehicle)">
               <q-tooltip>Excluir</q-tooltip>
             </q-btn>
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <div v-else class="full-width column flex-center q-pa-xl text-center">
      <div class="bg-grey-2 rounded-borders flex flex-center q-mb-md" style="width: 120px; height: 120px; border-radius: 50%;">
        <q-icon name="no_crash" size="64px" class="text-grey-5" />
      </div>
      <div class="text-h5 text-weight-bold text-grey-8" :class="{'text-white': $q.dark.isActive}">
        Nenhum {{ terminologyStore.vehicleNoun.toLowerCase() }} encontrado
      </div>
      <div class="text-body1 text-grey-6 q-mb-lg max-width-md">
        Comece adicionando veículos à sua frota para gerir manutenções, custos e motoristas.
      </div>
      <q-btn 
        @click="openCreateDialog" 
        v-if="authStore.isManager" 
        unelevated 
        color="primary" 
        icon="add"
        :label="`Adicionar ${terminologyStore.vehicleNoun}`" 
        size="lg"
        :disable="isVehicleLimitReached"
      />
    </div>

    <div class="flex flex-center q-mt-xl" v-if="pagination.rowsNumber > pagination.rowsPerPage">
      <q-pagination 
        v-model="pagination.page" 
        :max="Math.ceil(pagination.rowsNumber / pagination.rowsPerPage)" 
        @update:model-value="onPageChange" 
        direction-links 
        boundary-numbers
        color="primary"
        active-design="unelevated"
        active-color="primary"
        active-text-color="white"
        flat
      />
    </div>

    <q-dialog v-model="showComparisonDialog" transition-show="scale" transition-hide="scale">
      <q-card style="width: 750px; max-width: 95vw;" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-white'">
        <q-card-section class="bg-primary text-white q-py-lg text-center relative-position overflow-hidden">
          <div class="absolute-full bg-white opacity-10" style="transform: skewY(-5deg) scale(1.5);"></div>
          <q-icon name="rocket_launch" size="4em" class="q-mb-sm" />
          <div class="text-h4 text-weight-bold relative-position">Desbloqueie o Potencial Máximo</div>
          <div class="text-subtitle1 text-blue-2 relative-position">Veja o que ganha com o upgrade para PRO</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat :dark="$q.dark.isActive" :class="$q.dark.isActive ? 'bg-transparent' : ''">
            <thead>
              <tr :class="$q.dark.isActive ? 'bg-grey-8' : 'bg-grey-1 text-grey-7'">
                <th class="text-left q-pa-md text-uppercase text-caption">Funcionalidade</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9 border-left">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary bg-blue-1">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="directions_car" color="grey-6" size="xs" /> Gestão de Veículos</td>
                <td class="text-center bg-amber-1 text-amber-10">Até {{ demoUsageLimitLabel }} veículos</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Frota Ilimitada</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="history" color="grey-6" size="xs" /> Histórico de Dados</td>
                <td class="text-center bg-amber-1 text-amber-10">Últimos 7 dias</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Ilimitado (Vitalício)</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="speed" color="grey-6" size="xs" /> Limite de Viagens</td>
                <td class="text-center bg-amber-1 text-amber-10">10 por mês</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-1'">
          <div class="column items-center full-width q-gutter-y-md">
            <div class="text-h6 text-weight-bold">Pronto para escalar a sua frota?</div>
            <q-btn color="positive" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width shadow-3" />
            <q-btn flat color="grey-7" label="Continuar no Demo por enquanto" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isFormDialogOpen" persistent>
        <q-card style="width: 550px; max-width: 95vw;" :class="$q.dark.isActive ? 'bg-grey-9' : ''">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">{{ isEditing ? terminologyStore.editButtonLabel : terminologyStore.newButtonLabel }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup />
          </q-card-section>

          <q-form @submit.prevent="onFormSubmit">
            <q-card-section class="q-gutter-y-md scroll" style="max-height: 70vh">
              <div class="row q-col-gutter-sm">
                 <div class="col-12 col-sm-6">
                    <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Obrigatório']" dense />
                 </div>
                 <div class="col-12 col-sm-6">
                    <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Obrigatório']" dense />
                 </div>
              </div>

              <div class="row q-col-gutter-sm">
                <div class="col-12 col-sm-6">
                   <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Inválido']" dense />
                </div>
                <div class="col-12 col-sm-6">
                   <q-input v-if="!isEditing" outlined v-model="formData.license_plate" :label="terminologyStore.plateOrIdentifierLabel + ' *'" :mask="authStore.userSector !== 'agronegocio' ? 'AAA#A##' : ''" :rules="[val => !!val || 'Obrigatório']" dense />
                </div>
              </div>

              <q-input v-if="authStore.userSector === 'agronegocio'" outlined v-model.number="formData.current_engine_hours" type="number" label="Horas de Motor Atuais" step="0.1" dense />
              <q-input v-else outlined v-model.number="formData.current_km" type="number" label="KM Inicial" dense />
              
              <q-select v-if="isEditing" outlined v-model="formData.status" :options="statusOptions" label="Status" dense />
              
              <q-file 
                v-model="photoFile" 
                label="Carregar Foto" 
                outlined 
                dense 
                clearable 
                accept=".jpg, image/*" 
                class="q-mt-sm"
                @update:model-value="onFileSelected"
              >
                <template v-slot:prepend><q-icon name="cloud_upload" /></template>
                
                <template v-slot:append>
                    <q-avatar size="24px" square v-if="photoPreview || formData.photo_url">
                      <img :src="(photoPreview || getImageUrl(formData.photo_url)) || ''" style="object-fit: cover" />
                      <q-tooltip>Imagem atual</q-tooltip>
                    </q-avatar>
                </template>
              </q-file>
              
              <div class="text-subtitle2 q-mt-md text-primary">Manutenção Preventiva</div>
              <q-separator class="q-mb-md" />
              
              <div class="row q-col-gutter-sm">
                 <div class="col-12 col-sm-6">
                    <q-input outlined v-model.number="formData.next_maintenance_km" type="number" :label="`Próxima Revisão (${terminologyStore.distanceUnit})`" clearable dense />
                 </div>
                 <div class="col-12 col-sm-6">
                    <q-input outlined v-model="formData.next_maintenance_date" mask="##/##/####" label="Próxima Revisão (Data)" clearable dense>
                      <template v-slot:append>
                        <q-icon name="event" class="cursor-pointer">
                          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-date v-model="formData.next_maintenance_date" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Fechar" color="primary" flat /></div></q-date>
                          </q-popup-proxy>
                        </q-icon>
                      </template>
                    </q-input>
                 </div>
              </div>
              
              <q-expansion-item dense dense-toggle switch-toggle-side label="Configurações Avançadas" class="bg-grey-2 rounded-borders q-mt-md" :class="$q.dark.isActive ? 'bg-grey-8' : ''">
                  <q-card :class="$q.dark.isActive ? 'bg-grey-8' : 'bg-grey-2'">
                      <q-card-section class="q-gutter-y-sm">
                         <q-input bg-color="white" :dark="false" outlined v-model="formData.telemetry_device_id" label="ID Telemetria" dense hint="ID para conexão com IoT" />
                         <q-input bg-color="white" :dark="false" outlined v-model="formData.maintenance_notes" type="textarea" label="Anotações Gerais" autogrow dense />
                      </q-card-section>
                  </q-card>
              </q-expansion-item>
            </q-card-section>
            
            <q-separator />
            
            <q-card-actions align="right" class="q-pa-md">
              <q-btn flat label="Cancelar" color="grey-7" v-close-popup />
              <q-btn type="submit" unelevated color="primary" label="Salvar Veículo" :loading="isSubmitting" />
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
import { useDemoStore } from 'stores/demo-store';
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';
import api from 'src/services/api';
import axios from 'axios';

// --- CONFIGURAÇÃO DE URL DE IMAGENS ---
// Ajuste esta porta caso o seu backend não esteja na 8000
const API_BASE_URL = 'http://localhost:8000'; 

function getImageUrl(url: string | null | undefined) {
  if (!url) return undefined;
  // Se já for um link completo (https://...), usa-o.
  if (url.startsWith('http')) return url;
  // Se for relativo (/static/...), adiciona o domínio do backend.
  return `${API_BASE_URL}${url}`;
}
// ----------------------------------------

const $q = useQuasar();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const router = useRouter();
const demoStore = useDemoStore();
const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingVehicleId = ref<number | null>(null);
const isEditing = computed(() => editingVehicleId.value !== null);
const statusOptions = Object.values(VehicleStatus);
const formData = ref<Partial<Vehicle>>({});
const photoFile = ref<File | null>(null);
const photoPreview = ref<string | null>(null); // CORREÇÃO: Variável para o preview

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

// --- LÓGICA DEMO E LIMITES ---
const showComparisonDialog = ref(false);

const demoUsageCount = computed(() => demoStore.stats?.vehicle_count ?? 0);
const demoUsageLimit = computed(() => authStore.user?.organization?.vehicle_limit ?? 3); // Padrão 3 se null
const demoUsageLimitLabel = computed(() => {
    const limit = authStore.user?.organization?.vehicle_limit;
    return (limit === undefined || limit === null || limit < 0) ? 'Ilimitado' : limit.toString();
});

const isVehicleLimitReached = computed(() => {
  if (!isDemo.value) return false;
  const limit = authStore.user?.organization?.vehicle_limit;
  if (limit === undefined || limit === null || limit < 0) return false;
  return demoUsageCount.value >= limit;
});

const usagePercentage = computed(() => {
  if (!isDemo.value || demoUsageLimit.value <= 0) return 0;
  const pct = Math.round((demoUsageCount.value / demoUsageLimit.value) * 100);
  return Math.min(pct, 100);
});

const usageColor = computed(() => {
  if (usagePercentage.value >= 100) return 'red-4';
  if (usagePercentage.value >= 80) return 'orange-4';
  return 'white';
});

function showLimitUpgradeDialog() {
  showComparisonDialog.value = true;
}

// --- NAVEGAÇÃO E CRUD ---
function handleCardClick(vehicle: Vehicle) {
  if (authStore.isManager) {
    goToVehicleDetails(vehicle);
  } 
}

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
    license_plate: '', identifier: null, photo_url: null, status: VehicleStatus.AVAILABLE,
    current_km: 0, current_engine_hours: 0,
    next_maintenance_date: null, next_maintenance_km: null, maintenance_notes: '',
    telemetry_device_id: null,
  };
  photoFile.value = null;
  photoPreview.value = null; // CORREÇÃO: Limpa o preview
}

// CORREÇÃO: Gera preview ao selecionar arquivo
function onFileSelected(val: File | null) {
  if (val) {
    photoPreview.value = URL.createObjectURL(val);
  } else {
    photoPreview.value = null;
  }
}

function openCreateDialog() {
  if (isVehicleLimitReached.value) {
    showLimitUpgradeDialog();
    return;
  }
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
  photoPreview.value = null; // CORREÇÃO: Limpa o preview para mostrar a foto original
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
      payload.license_plate = null; 
    }

    if (payload.identifier === '' || !payload.identifier) delete payload.identifier;
    if (payload.license_plate === '' || !payload.license_plate) delete payload.license_plate;
    if (payload.telemetry_device_id === '' || !payload.telemetry_device_id) delete payload.telemetry_device_id;

    const currentFetchParams = {
      page: pagination.value.page,
      rowsPerPage: pagination.value.rowsPerPage,
      search: searchTerm.value,
    };

    if (isEditing.value && editingVehicleId.value) {
      await vehicleStore.updateVehicle(editingVehicleId.value, payload as VehicleUpdate, currentFetchParams);
    } else {
      await vehicleStore.addNewVehicle(payload as VehicleCreate, currentFetchParams);
      if (authStore.isDemo) {
        // Força atualização para refletir novo uso imediatamente
        void demoStore.fetchDemoStats(true);
      }
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
  if (authStore.isDemo) {
    void demoStore.fetchDemoStats();
  }
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
    void (async () => {
      await vehicleStore.deleteVehicle(vehicle.id, {
        page: pagination.value.page, rowsPerPage: pagination.value.rowsPerPage, search: searchTerm.value,
      });
      if (authStore.isDemo) {
        await demoStore.fetchDemoStats(true);
      }
    })();
  });
}
</script>

<style scoped lang="scss">
.search-input {
  width: 300px;
  @media (max-width: 599px) {
    width: 100%;
  }
}

.demo-card-gradient {
  background: linear-gradient(135deg, var(--q-primary) 0%, darken($primary, 20%) 100%);
  border: none;
  border-radius: 12px;
}

.vehicle-card {
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;

  &.vehicle-card-interactive {
     cursor: pointer;
     &:hover {
       transform: translateY(-5px);
       box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
       border-color: var(--q-primary);
     }
  }
}

.metric-box {
  padding: 8px 12px;
  border-radius: 8px;
  text-align: left;
}

.text-xs-custom {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.custom-border {
  border: 1px solid rgba(0,0,0,0.08);
}

.white-30 {
  color: rgba(255,255,255,0.3) !important;
}

.opacity-10 {
  opacity: 0.1;
}

/* Dark mode specific tweaks if not handled by Quasar classes */
.body--dark {
  .custom-border {
    border: 1px solid rgba(255,255,255,0.1);
  }
}
</style>