<template>
  <q-page class="flex overflow-hidden relative-position">
    
    <div class="col relative-position" style="z-index: 0;">
      <l-map 
        ref="mapRef" 
        v-model:zoom="zoom" 
        :center="center" 
        :use-global-leaflet="false" 
        class="full-height"
        :options="{ zoomControl: false }" 
      >
        <l-tile-layer :url="mapUrl" layer-type="base" name="Map" :attribution="mapAttribution"></l-tile-layer>

        <l-marker 
          v-for="vehicle in vehiclesWithPosition" 
          :key="vehicle.id" 
          :lat-lng="[vehicle.last_latitude!, vehicle.last_longitude!]"
          @click="selectVehicle(vehicle)"
        >
          <l-icon :icon-size="[46, 46]" :icon-anchor="[23, 23]" class-name="custom-marker-icon">
            <div 
              class="marker-pin"
              :class="{ 
                'selected': selectedVehicleId === vehicle.id,
                'moving': isMoving(vehicle),
                'stopped': !isMoving(vehicle)
              }"
            >
              <q-icon name="directions_car" size="20px" color="white" />
            </div>
            <div v-if="selectedVehicleId === vehicle.id" class="marker-pulse"></div>
          </l-icon>

          <l-popup>
            <div class="text-subtitle2 text-weight-bold">{{ vehicle.brand }} {{ vehicle.model }}</div>
            <div class="text-caption text-grey-7">{{ vehicle.license_plate }}</div>
            <q-separator class="q-my-xs" />
            <div class="row items-center q-gutter-x-sm">
              <q-badge :color="isMoving(vehicle) ? 'green' : 'grey'">
                {{ isMoving(vehicle) ? 'Em Movimento' : 'Parado' }}
              </q-badge>
              <span class="text-caption">Horímetro: {{ vehicle.current_engine_hours?.toFixed(1) }}h</span>
            </div>
          </l-popup>
        </l-marker>
      </l-map>

      <div class="absolute-top-right q-ma-md column q-gutter-y-sm z-top">
        <q-btn round dense color="white" text-color="black" icon="add" @click="zoomIn" />
        <q-btn round dense color="white" text-color="black" icon="remove" @click="zoomOut" />
        <q-btn round dense :color="isMapDark ? 'yellow-9' : 'grey-9'" :icon="isMapDark ? 'wb_sunny' : 'nights_stay'" @click="toggleTheme">
          <q-tooltip>Alternar Modo Escuro</q-tooltip>
        </q-btn>
      </div>

      <div v-if="isLoading" class="absolute-center bg-white q-pa-md rounded-borders shadow-2 z-top text-center" style="opacity: 0.9;">
        <q-spinner-dots color="primary" size="30px" />
        <div class="text-caption q-mt-xs">Buscando satélites...</div>
      </div>
    </div>

    <transition name="slide-fade">
      <div 
        v-show="showSidebar"
        class="sidebar-panel column no-wrap shadow-5"
        :class="isMapDark ? 'bg-dark-glass text-white' : 'bg-white-glass text-grey-9'"
      >
        <div class="q-pa-md">
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-bold">Frota Online</div>
            <div class="row items-center">
              <q-btn 
                flat round dense 
                :icon="isAutoRefresh ? 'sync' : 'pause'" 
                :color="isAutoRefresh ? 'green' : 'grey'"
                @click="toggleAutoRefresh"
              >
                <q-tooltip>{{ isAutoRefresh ? 'Atualizando a cada 5s' : 'Atualização Pausada' }}</q-tooltip>
              </q-btn>
              <q-btn flat round dense icon="close" class="lt-md" @click="showSidebar = false" />
            </div>
          </div>
          
          <q-input
            :dark="isMapDark" dense outlined rounded
            v-model="searchQuery" 
            placeholder="Buscar placa..."
            :bg-color="isMapDark ? 'grey-9' : 'grey-1'"
          >
            <template v-slot:prepend><q-icon name="search" /></template>
          </q-input>
          
          <div class="q-mt-sm text-caption text-center opacity-70 bg-grey-3 text-black q-pa-xs rounded-borders cursor-pointer" @click="copyIp">
             IP de Conexão: <b>{{ apiHost }}</b>
             <q-tooltip>Clique para copiar</q-tooltip>
          </div>
        </div>

        <q-separator :dark="isMapDark" />

        <q-scroll-area class="col">
          <q-list separator>
            <q-item
              v-for="vehicle in filteredVehicles"
              :key="vehicle.id"
              clickable v-ripple
              :active="selectedVehicleId === vehicle.id"
              :active-class="isMapDark ? 'bg-blue-grey-9' : 'bg-blue-1'"
              @click="selectVehicle(vehicle)"
            >
              <q-item-section avatar>
                <div class="relative-position">
                  <q-avatar :color="getSignalStatus(vehicle).color" text-color="white" icon="directions_car" size="md"/>
                  <q-badge floating rounded :color="hasSignal(vehicle) ? 'green' : 'red'" style="border: 2px solid white; width: 10px; height: 10px; padding: 0;"/>
                </div>
              </q-item-section>

              <q-item-section>
                <q-item-label class="text-weight-medium">{{ vehicle.brand }} {{ vehicle.model }}</q-item-label>
                <q-item-label caption :class="isMapDark ? 'text-grey-4' : 'text-grey-7'">{{ vehicle.license_plate || 'Sem Placa' }}</q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="column items-end">
                  <q-icon name="wifi" size="xs" :color="hasSignal(vehicle) ? 'green' : 'grey-5'" />
                  <span class="text-caption text-weight-bold" style="font-size: 10px;">{{ hasSignal(vehicle) ? 'GPS OK' : 'OFF' }}</span>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-scroll-area>
      </div>
    </transition>
    
    <q-btn v-if="!showSidebar" fab icon="list" color="primary" class="absolute-bottom-left q-ma-md z-top" @click="showSidebar = true" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useQuasar, copyToClipboard } from 'quasar';
import { LMap, LTileLayer, LMarker, LPopup, LIcon } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { useVehicleStore } from 'stores/vehicle-store';
import type { Vehicle } from 'src/models/vehicle-models';

// --- CONFIGURAÇÕES ---
const $q = useQuasar();
const vehicleStore = useVehicleStore();
const mapRef = ref(null);
const zoom = ref(5);
const center = ref<[number, number]>([-14.2350, -51.9253]);
const apiHost = window.location.hostname + ':8000';

// --- ESTADOS ---
const isLoading = ref(true);
const isAutoRefresh = ref(true);
const showSidebar = ref(true);
const searchQuery = ref('');
const selectedVehicleId = ref<number | null>(null);

// --- TEMA ---
const savedMapTheme = localStorage.getItem('trucar_map_theme');
const isMapDark = ref(savedMapTheme ? savedMapTheme === 'dark' : $q.dark.isActive);
watch(isMapDark, (val) => {
  localStorage.setItem('trucar_map_theme', val ? 'dark' : 'light');
  $q.dark.set(val);
});
const toggleTheme = () => isMapDark.value = !isMapDark.value;

const mapUrl = computed(() => isMapDark.value 
  ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' 
  : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
);
const mapAttribution = computed(() => '&copy; OpenStreetMap contributors');

// --- DADOS ---
const allTrackedVehicles = computed(() => 
  vehicleStore.vehicles.filter(v => v.telemetry_device_id && v.telemetry_device_id.length > 0)
);

const filteredVehicles = computed(() => {
  if (!searchQuery.value) return allTrackedVehicles.value;
  const q = searchQuery.value.toLowerCase();
  return allTrackedVehicles.value.filter(v => 
    v.brand.toLowerCase().includes(q) || 
    v.model.toLowerCase().includes(q) || 
    (v.license_plate && v.license_plate.toLowerCase().includes(q))
  );
});

const vehiclesWithPosition = computed(() => 
  allTrackedVehicles.value.filter(v => v.last_latitude && v.last_longitude)
);

// --- AUXILIARES ---
const hasSignal = (v: Vehicle) => !!(v.last_latitude && v.last_longitude);
const isMoving = (v: Vehicle) => hasSignal(v); 
const getSignalStatus = (v: Vehicle) => hasSignal(v) ? { label: 'Online', color: 'blue-6' } : { label: 'Sem Sinal', color: 'grey-5' };

// CORREÇÃO: Adicionado .catch() para tratar promessas soltas
const copyIp = () => {
  copyToClipboard(`http://${apiHost}/api/v1/integrations/traccar`)
    .then(() => { $q.notify({ message: 'URL copiada!', color: 'positive' }); })
    .catch(() => { $q.notify({ message: 'Erro ao copiar', color: 'negative' }); });
};

const zoomIn = () => zoom.value++;
const zoomOut = () => zoom.value--;

function selectVehicle(vehicle: Vehicle) {
  if (hasSignal(vehicle)) {
    center.value = [vehicle.last_latitude!, vehicle.last_longitude!];
    zoom.value = 16;
    selectedVehicleId.value = vehicle.id;
    if ($q.screen.lt.md) showSidebar.value = false;
  } else {
    $q.notify({ message: `Aguardando GPS...`, type: 'warning' });
  }
}

// --- LOOP DE ATUALIZAÇÃO ---
// CORREÇÃO: Tipagem correta do Timer para TypeScript
let pollingInterval: ReturnType<typeof setInterval> | null = null;

// CORREÇÃO: Tratamento try/catch explícito para evitar erro de ESLint
const fetchData = async () => {
  if (!isAutoRefresh.value) return;
  try {
    await vehicleStore.fetchAllVehicles({ rowsPerPage: 1000 }); 
  } catch (error) {
    console.error('Erro ao atualizar mapa:', error);
  } finally {
    isLoading.value = false;
  }
};

const toggleAutoRefresh = () => {
  isAutoRefresh.value = !isAutoRefresh.value;
  // CORREÇÃO: .catch() adicionado para a promessa não ficar "flutuando"
  if (isAutoRefresh.value) {
    fetchData().catch(() => {/* ignora erro silencioso */});
  }
};

onMounted(() => {
  // CORREÇÃO: Chamada inicial com .catch()
  fetchData().catch(() => {/* ignora erro silencioso */});

  // CORREÇÃO: Intervalo chamando função segura
  pollingInterval = setInterval(() => { 
    fetchData().catch(() => {/* ignora erro silencioso */}); 
  }, 5000);
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});
</script>

<style lang="scss" scoped>
.full-height { height: 100vh; }
.sidebar-panel {
  width: 350px;
  height: 90vh;
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1001;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}
@media (max-width: 768px) {
  .sidebar-panel { width: 100%; height: 60vh; bottom: 0; top: auto; left: 0; border-radius: 24px 24px 0 0; }
}
.bg-white-glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.5); }
.bg-dark-glass { background: rgba(20, 20, 30, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
.opacity-70 { opacity: 0.7; }
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(-20px); opacity: 0; }
:deep(.custom-marker-icon) { background: transparent; border: none; }
.marker-pin {
  width: 46px; height: 46px; border-radius: 50%; background: #5e6472;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3); border: 3px solid white;
  position: relative; z-index: 2; transition: transform 0.2s;
}
.marker-pin.moving { background: #2196f3; }
.marker-pin.selected { transform: scale(1.2); background: #4caf50; border-color: #fff; z-index: 10; }
.marker-pulse {
  position: absolute; top: 0; left: 0; width: 46px; height: 46px;
  border-radius: 50%; background: rgba(33, 150, 243, 0.5); z-index: 1;
  animation: pulse-animation 2s infinite;
}
@keyframes pulse-animation {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(2.5); opacity: 0; }
}
</style>