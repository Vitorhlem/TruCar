<template>
  <q-page class="flex overflow-hidden">

    <!-- PAINEL LATERAL DE CONTROLO (ADAPTATIVO LOCALMENTE) -->
    <div 
      class="col-12 col-md-3 column no-wrap"
      :class="isMapDark ? 'glass-panel-dark' : 'glass-panel-light'"
    >
      <div class="q-pa-md">
        <div :class="isMapDark ? 'text-white' : 'text-grey-9'" class="text-h6">Veículos Conectados</div>
        <q-input
          :dark="isMapDark"
          dense
          :standout="isMapDark ? 'bg-grey-10' : 'bg-grey-3'"
          v-model="searchQuery"
          placeholder="Procurar por marca ou modelo..."
          class="q-mt-md"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>

      <q-separator :dark="isMapDark" />

      <q-scroll-area class="col">
        <q-list :dark="isMapDark" separator>
          <q-item
            v-for="vehicle in filteredVehicles"
            :key="vehicle.id"
            clickable
            v-ripple
            :active="selectedVehicleId === vehicle.id"
            :active-class="isMapDark ? 'bg-blue-grey-10' : 'bg-blue-1'"
            @click="selectVehicle(vehicle)"
          >
            <q-item-section avatar>
              <q-icon :color="getVehicleStatus(vehicle).color" :name="getVehicleStatus(vehicle).icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label :class="{ 'text-white': isMapDark }">{{ vehicle.brand }} {{ vehicle.model }}</q-item-label>
              <q-item-label caption>Placa: {{ vehicle.license_plate || 'N/A' }}</q-item-label>
            </q-item-section>
             <q-item-section side>
              <q-item-label caption>{{ getVehicleStatus(vehicle).label }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </div>

    <!-- MAPA PRINCIPAL (ADAPTATIVO LOCALMENTE) -->
    <div class="col relative-position">
      <div v-if="isLoading" class="absolute-center z-top text-center">
        <q-spinner-dots color="primary" size="40px" />
        <div class="q-mt-md" :class="isMapDark ? 'text-white' : 'text-primary'">Carregando mapa e posições...</div>
      </div>
      <l-map ref="map" v-model:zoom="zoom" :center="center" :use-global-leaflet="false" class="full-height">
        <l-tile-layer
          :url="mapUrl"
          layer-type="base"
          name="Map"
          :attribution="mapAttribution"
        ></l-tile-layer>
        
        <l-marker 
          v-for="vehicle in filteredVehicles" 
          :key="vehicle.id" 
          :lat-lng="[vehicle.last_latitude!, vehicle.last_longitude!]"
          @click="selectVehicle(vehicle)"
        >
          <l-icon :icon-size="[40, 40]" class-name="vehicle-marker-wrapper">
            <div class="vehicle-marker" :class="`marker-${getVehicleStatus(vehicle).color}`">
              <q-icon :name="getVehicleStatus(vehicle).icon" color="white" size="24px"/>
            </div>
            <div class="marker-pulse" :class="`pulse-${getVehicleStatus(vehicle).color}`"></div>
          </l-icon>
          <l-popup>
            <div class="text-weight-bold">{{ vehicle.brand }} {{ vehicle.model }}</div>
            <div>Horímetro: {{ vehicle.current_engine_hours?.toFixed(1) }} Horas</div>
            <div class="q-mt-sm"><q-btn size="sm" dense flat color="primary" @click="selectVehicle(vehicle)">Centralizar</q-btn></div>
          </l-popup>
        </l-marker>
      </l-map>

      <!-- BOTÃO DE MUDANÇA DE TEMA LOCAL -->
      <q-btn
        flat
        round
        dense
        :icon="isMapDark ? 'wb_sunny' : 'nights_stay'"
        @click="isMapDark = !isMapDark"
        class="theme-toggle-btn"
        :color="isMapDark ? 'yellow' : 'black'"
        title="Mudar tema do mapa"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { LMap, LTileLayer, LMarker, LPopup, LIcon } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { useVehicleStore } from 'stores/vehicle-store';
import type { Vehicle } from 'src/models/vehicle-models';

const $q = useQuasar();
const vehicleStore = useVehicleStore();
const zoom = ref(5);
const center = ref<[number, number]>([-14.2350, -51.9253]);
const isLoading = ref(true);
const searchQuery = ref('');
const selectedVehicleId = ref<number | null>(null);

// LÓGICA DE PERSISTÊNCIA: Carrega o tema salvo ou usa o tema global como padrão
const savedMapTheme = localStorage.getItem('trucar_map_theme');
const isMapDark = ref(savedMapTheme ? savedMapTheme === 'dark' : $q.dark.isActive);

// Salva a preferência do utilizador no localStorage sempre que ela for alterada
watch(isMapDark, (isDark) => {
  localStorage.setItem('trucar_map_theme', isDark ? 'dark' : 'light');
});


const mapUrl = computed(() => {
  return isMapDark.value
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
});

const mapAttribution = computed(() => {
  return isMapDark.value
    ? `&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a href='https://carto.com/attributions'>CARTO</a>`
    : `&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>`;
});

const connectedVehicles = computed(() =>
  vehicleStore.vehicles.filter(
    (v): v is Vehicle & { id: number; last_latitude: number; last_longitude: number } =>
      !!v.id && !!v.telemetry_device_id && typeof v.last_latitude === 'number' && typeof v.last_longitude === 'number'
  )
);

const filteredVehicles = computed(() => {
  if (!searchQuery.value) {
    return connectedVehicles.value;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return connectedVehicles.value.filter(v => 
    v.brand?.toLowerCase().includes(lowerCaseQuery) || 
    v.model?.toLowerCase().includes(lowerCaseQuery) ||
    v.license_plate?.toLowerCase().includes(lowerCaseQuery)
  );
});

function getVehicleStatus(vehicle: Vehicle & {id: number}) {
  if (!vehicle.current_engine_hours || vehicle.current_engine_hours < 1) {
    return { label: 'Desligado', color: 'grey', icon: 'power_off' };
  }
  if (vehicle.id % 2 === 0) {
    return { label: 'Parado', color: 'info', icon: 'pause_circle' };
  }
  return { label: 'Em Movimento', color: 'positive', icon: 'local_shipping' };
}

let pollingInterval: NodeJS.Timeout | null = null;

onMounted(async () => {
  isLoading.value = true;
  await vehicleStore.fetchAllVehicles({ rowsPerPage: 500 });
  const firstVehicle = connectedVehicles.value[0];
  if (firstVehicle) {
    center.value = [firstVehicle.last_latitude, firstVehicle.last_longitude];
    zoom.value = 12;
  }
  isLoading.value = false;
  pollingInterval = setInterval(() => { void vehicleStore.fetchAllVehicles({ rowsPerPage: 500 }); }, 15000);
});

onUnmounted(() => { if (pollingInterval) clearInterval(pollingInterval); });

function selectVehicle(vehicle: Vehicle & {id: number}) {
  if (vehicle.last_latitude && vehicle.last_longitude) {
    center.value = [vehicle.last_latitude, vehicle.last_longitude];
    zoom.value = 17;
    selectedVehicleId.value = vehicle.id;
  }
}
</script>

<style lang="scss" scoped>
/* ESTILOS ADAPTATIVOS */
.glass-panel-light {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  z-index: 1000;
}
.glass-panel-dark {
  background: rgba(18, 23, 38, 0.5);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
}

.full-height {
  height: 100%;
}

.theme-toggle-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1001;
  background: v-bind("(isMapDark ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.7)')");
}

.vehicle-marker-wrapper {
  background: transparent;
  border: none;
}

.vehicle-marker {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  position: relative;
  z-index: 2;
}

.marker-pulse {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  animation: pulse-animation 2s infinite;
}

.marker-positive { background-color: $positive; }
.marker-info { background-color: $info; }
.marker-grey { background-color: $grey; }
.marker-negative { background-color: $negative; }

.pulse-positive { box-shadow: 0 0 0 0 rgba($positive, 0.7); }
.pulse-info { box-shadow: 0 0 0 0 rgba($info, 0.7); }
.pulse-grey { box-shadow: 0 0 0 0 rgba($grey, 0.7); }
.pulse-negative { box-shadow: 0 0 0 0 rgba($negative, 0.7); }

@keyframes pulse-animation {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.7);
  }
  70% {
    transform: scale(1.4);
    box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
  }
}
</style>

