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
        @click="onMapClick"
      >
        <l-tile-layer :url="mapUrl" layer-type="base" name="Map" :attribution="mapAttribution"></l-tile-layer>
        
        <l-tile-layer 
          v-if="showWeatherLayer"
          url="https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=e876939c6147a5242f651dca4a7fc557"
          layer-type="overlay" 
          name="Precipitation" 
          :opacity="0.6"
          :max-native-zoom="10"
        ></l-tile-layer>

        <l-polyline
          v-if="mapStore.routeCoordinates.length > 0"
          :lat-lngs="mapStore.routeCoordinates"
          :color="mapStore.routeAlert ? '#d50000' : '#0055FF'" 
          :weight="7" 
          :opacity="1.0"
        >
           <l-popup v-if="mapStore.routeAlert">
             <div class="text-weight-bold text-orange">⚠️ Rota Desviada!</div>
             <div>Evitando: {{ mapStore.routeAlert.event_type }}</div>
           </l-popup>
        </l-polyline>

        <l-marker 
          v-for="hole in potholes" 
          :key="'hole-' + hole.id" 
          :lat-lng="[hole.latitude, hole.longitude]"
        >
          <l-icon :icon-size="[20, 20]" :icon-anchor="[10, 10]" class-name="no-bg">
            <div style="background: #3e2723; border-radius: 50%; width: 20px; height: 20px; border: 2px solid white; display: flex; align-items: center; justify-content: center;">
              ⚠️
            </div>
          </l-icon>
          <l-popup>
            <div class="text-weight-bold">Via Danificada</div>
            <div class="text-caption">{{ hole.description }}</div>
          </l-popup>
        </l-marker>

        <l-marker v-if="mapStore.destination" :lat-lng="mapStore.destination">
           <l-icon :icon-size="[32, 32]" :icon-anchor="[16, 32]" class-name="no-bg">
             <div style="font-size: 36px; line-height: 1; text-align: center;">📍</div>
           </l-icon>
        </l-marker>

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
                'risk': isVehicleInRisk(vehicle) 
              }"
            >
              <q-icon :name="isVehicleInRisk(vehicle) ? 'warning' : 'directions_car'" size="20px" color="white" />
            </div>
            <div v-if="selectedVehicleId === vehicle.id" class="marker-pulse"></div>
          </l-icon>
        </l-marker>

        <l-circle
          v-for="event in weatherEvents"
          :key="'event-' + event.id"
          :lat-lng="[event.affected_lat, event.affected_lon]"
          :radius="event.affected_radius_km * 1000"
          color="red"
          fill-color="#f44336"
          :fill-opacity="0.3"
        >
          <l-popup>
            <div class="text-weight-bold text-red">⚠️ {{ event.event_type }}</div>
            <div>{{ event.description }}</div>
          </l-popup>
        </l-circle>

        <l-polygon
          v-for="zone in mapStore.geofences"
          :key="'zone-' + zone.id"
          :lat-lngs="zone.polygon_points"
          :color="zone.type === 'RISK_ZONE' ? 'red' : 'green'"
          :fill-opacity="0.2"
          @click="onMapClick" 
        >
          <l-popup v-if="!selectedVehicleId && !mapStore.isDrawingMode">
            <div class="column q-gutter-y-xs">
              <div class="text-subtitle2 text-weight-bold">{{ zone.name }}</div>
              <div class="text-caption">
                {{ zone.type === 'RISK_ZONE' ? 'Zona de Risco' : 'Zona Segura' }}
              </div>
              <q-separator />
              <q-btn dense size="sm" color="negative" icon="delete" label="Excluir Área" class="full-width" @click.stop="deleteGeofence(zone.id)" />
            </div>
          </l-popup>
        </l-polygon>

        <l-polygon
          v-if="mapStore.drawingPoints.length > 0"
          :lat-lngs="mapStore.drawingPoints"
          color="orange"
          :weight="2"
          dash-array="5, 5"
        ></l-polygon>
        
        <l-marker v-for="(pt, index) in mapStore.drawingPoints" :key="'pt-'+index" :lat-lng="pt">
           <l-icon :icon-size="[10, 10]" :icon-anchor="[5, 5]" class-name="no-bg">
             <div style="width: 10px; height: 10px; background: orange; border-radius: 50%;"></div>
           </l-icon>
        </l-marker>

      </l-map>

      <div v-if="mapStore.isDrawingMode" class="absolute-top-center q-mt-md z-top bg-white q-pa-sm rounded-borders shadow-2 row items-center q-gutter-x-sm">
        <div class="text-weight-bold text-orange">Modo Criação:</div>
        <div class="text-caption">Clique no mapa para desenhar.</div>
        <q-btn size="sm" color="negative" flat icon="close" label="Cancelar" @click="cancelDrawing" />
        <q-btn size="sm" color="positive" icon="save" label="Salvar" :disable="mapStore.drawingPoints.length < 3" @click="saveGeofence" />
      </div>

      <div class="absolute-top-right q-ma-md column q-gutter-y-sm z-top">
        <q-btn round dense color="white" text-color="black" icon="add" @click="zoomIn" />
        <q-btn round dense color="white" text-color="black" icon="remove" @click="zoomOut" />
        <q-btn round dense :color="isMapDark ? 'yellow-9' : 'grey-9'" :icon="isMapDark ? 'wb_sunny' : 'nights_stay'" @click="toggleTheme">
           <q-tooltip>Modo Escuro</q-tooltip>
        </q-btn>
        <q-btn round dense :color="showWeatherLayer ? 'blue' : 'grey'" text-color="white" icon="thunderstorm" @click="showWeatherLayer = !showWeatherLayer">
          <q-tooltip>Ativar Camada de Clima</q-tooltip>
        </q-btn>
        <q-btn round dense :color="mapStore.isDrawingMode ? 'orange' : 'white'" text-color="black" icon="hexagon" @click="toggleDrawingMode">
          <q-tooltip>Criar Cerca Eletrônica</q-tooltip>
        </q-btn>
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
            <div class="text-h6 text-weight-bold">Monitoramento</div>
            <div class="row items-center">
               <q-btn flat round dense :icon="isAutoRefresh ? 'sync' : 'pause'" :color="isAutoRefresh ? 'green' : 'grey'" @click="toggleAutoRefresh" />
               <q-btn flat round dense icon="close" class="lt-md" @click="showSidebar = false" />
            </div>
          </div>
          
          <div v-if="mapStore.routeCoordinates.length > 0" class="bg-blue-1 text-blue-9 q-pa-sm rounded-borders q-mb-sm border-blue">
            <div class="text-weight-bold flex items-center">
               <q-icon name="alt_route" class="q-mr-xs"/> Rota Calculada
            </div>
            <div v-if="mapStore.routeAlert" class="text-caption text-orange text-weight-bold">
               ⚠️ Desvio ativado por {{ mapStore.routeAlert.event_type }}
            </div>
            <div v-else class="text-caption text-green">
               ✅ Caminho livre e seguro.
            </div>
          </div>

          <q-input :dark="isMapDark" dense outlined rounded v-model="searchQuery" placeholder="Buscar placa..." :bg-color="isMapDark ? 'grey-9' : 'grey-1'">
            <template v-slot:prepend><q-icon name="search" /></template>
          </q-input>
        </div>

        <q-separator :dark="isMapDark" />

        <q-scroll-area class="col">
          <q-list separator>
            <q-item
              v-for="vehicle in filteredVehicles"
              :key="vehicle.id"
              clickable v-ripple
              @click="selectVehicle(vehicle)"
              :class="{
                'bg-red-1': isVehicleInRisk(vehicle) && !isMapDark, 
                'bg-red-9': isVehicleInRisk(vehicle) && isMapDark,
                'bg-blue-grey-2': selectedVehicleId === vehicle.id && !isVehicleInRisk(vehicle)
              }"
            >
              <q-item-section avatar>
                <div class="relative-position">
                  <q-avatar :color="isVehicleInRisk(vehicle) ? 'red' : getSignalStatus(vehicle).color" text-color="white" :icon="isVehicleInRisk(vehicle) ? 'storm' : 'directions_car'" size="md"/>
                </div>
              </q-item-section>

              <q-item-section>
                <q-item-label class="text-weight-medium">{{ vehicle.brand }} {{ vehicle.model }}</q-item-label>
                <q-item-label caption>{{ vehicle.license_plate }}</q-item-label>
                <q-badge v-if="isVehicleInRisk(vehicle)" color="red" label="PERIGO" class="q-mt-xs" />
              </q-item-section>
              
              <q-item-section side>
                 <q-icon name="check_circle" color="primary" v-if="selectedVehicleId === vehicle.id"/>
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
import { useQuasar } from 'quasar';
import { LMap, LTileLayer, LMarker, LPopup, LIcon, LCircle, LPolyline, LPolygon } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import { useVehicleStore } from 'stores/vehicle-store';
import { useMapStore } from 'stores/map-store';
import type { Vehicle } from 'src/models/vehicle-models';
import { api } from 'src/boot/axios';

interface Pothole {
  id: number;
  latitude: number;
  longitude: number;
  description: string;
}
interface WeatherEvent {
  id: number;
  event_type: string;
  description: string;
  affected_lat: number;
  affected_lon: number;
  affected_radius_km: number;
}

const $q = useQuasar();
const vehicleStore = useVehicleStore();
const mapStore = useMapStore();
const mapRef = ref(null);
const zoom = ref(5);
const center = ref<[number, number]>([-14.2350, -51.9253]);

const isLoading = ref(true);
const isAutoRefresh = ref(true);
const showSidebar = ref(true);
const showWeatherLayer = ref(false);
const searchQuery = ref('');
const selectedVehicleId = ref<number | null>(null);

const potholes = ref<Pothole[]>([]);
const weatherEvents = ref<WeatherEvent[]>([]);

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

const allTrackedVehicles = computed(() => vehicleStore.vehicles);
const filteredVehicles = computed(() => {
  if (!searchQuery.value) return allTrackedVehicles.value;
  const q = searchQuery.value.toLowerCase();
  return allTrackedVehicles.value.filter(v => v.brand.toLowerCase().includes(q) || v.license_plate?.toLowerCase().includes(q));
});
const vehiclesWithPosition = computed(() => allTrackedVehicles.value.filter(v => v.last_latitude));

const hasSignal = (v: Vehicle) => !!(v.last_latitude && v.last_longitude);
const isMoving = (v: Vehicle) => hasSignal(v);
const getSignalStatus = (v: Vehicle) => hasSignal(v) ? { label: 'Online', color: 'blue-6' } : { label: 'Offline', color: 'grey-5' };

function isVehicleInRisk(vehicle: Vehicle) {
  if (!vehicle.last_latitude || !vehicle.last_longitude) return false;
  return weatherEvents.value.some(event => {
    const dist = Math.sqrt(Math.pow(event.affected_lat - vehicle.last_latitude!, 2) + Math.pow(event.affected_lon - vehicle.last_longitude!, 2));
    return dist < 0.2;
  });
}

const zoomIn = () => zoom.value++;
const zoomOut = () => zoom.value--;

// --- GEOFENCING LOGIC ---

const toggleDrawingMode = () => {
  mapStore.isDrawingMode = !mapStore.isDrawingMode;
  mapStore.drawingPoints = [];
  if (mapStore.isDrawingMode) {
    $q.notify({message: 'Clique no mapa para desenhar a área.', color: 'info', icon: 'edit_location', position: 'top'});
  }
};

const cancelDrawing = () => {
  mapStore.isDrawingMode = false;
  mapStore.drawingPoints = [];
};

const saveGeofence = () => {
  if (mapStore.drawingPoints.length < 3) return;

  $q.dialog({
    title: 'Salvar Cerca',
    message: 'Nome da Zona:',
    prompt: { model: '', type: 'text' },
    options: {
      type: 'radio',
      model: 'SAFE_ZONE',
      items: [
        { label: 'Zona Segura (Alerta se SAIR)', value: 'SAFE_ZONE' },
        { label: 'Zona de Risco (Alerta se ENTRAR)', value: 'RISK_ZONE' }
      ]
    },
    cancel: true,
    persistent: true
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  }).onOk((data: any) => {
    const name = typeof data === 'string' ? data : data.data; 
    
    // CORREÇÃO AQUI: Remoção do async/await desnecessário
    try {
      mapStore.addGeofence({
        id: Date.now(),
        name: name,
        type: "SAFE_ZONE", 
        polygon_points: [...mapStore.drawingPoints]
      });

      $q.notify({message: 'Cerca criada com sucesso!', color: 'positive'});
      cancelDrawing();
    } catch (error) {
      console.error(error);
    }
  });
};

const deleteGeofence = (id: number) => {
  $q.dialog({
    title: 'Excluir Cerca',
    message: 'Tem certeza que deseja remover esta área monitorada?',
    cancel: true,
    persistent: true,
    ok: { label: 'Sim, Excluir', color: 'negative' }
  }).onOk(() => {
    // CORREÇÃO AQUI: Remoção do async/await desnecessário
    try {
      mapStore.removeGeofence(id);
      $q.notify({message: 'Cerca removida.', color: 'positive', icon: 'delete', position: 'top'});
    } catch (error) {
      console.error(error);
      $q.notify({message: 'Erro ao excluir cerca.', color: 'negative'});
    }
  });
};

const loadGeofences = async () => {
  // Lógica de carregar do backend futuramente
};

// --- AÇÕES DO MAPA ---

function selectVehicle(vehicle: Vehicle) {
  selectedVehicleId.value = vehicle.id;
  if (hasSignal(vehicle)) {
    center.value = [vehicle.last_latitude!, vehicle.last_longitude!];
    zoom.value = 14;
  } else {
    center.value = [-23.5505, -46.6333]; 
    zoom.value = 13;
    $q.notify({
        message: 'Modo Dev: Veículo sem GPS. Simulando posição em SP.',
        color: 'blue-grey',
        icon: 'developer_mode',
        timeout: 2000,
        position: 'top'
    });
  }
  if ($q.screen.lt.md) showSidebar.value = false;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const onMapClick = async (e: any) => {
  if (mapStore.isDrawingMode) {
    mapStore.drawingPoints.push([e.latlng.lat, e.latlng.lng]);
    return;
  }

  if (!selectedVehicleId.value) {
    $q.notify({message: 'Selecione um veículo na lista para traçar a rota.', color: 'warning', icon: 'near_me'});
    return;
  }
  
  const vehicle = allTrackedVehicles.value.find(v => v.id === selectedVehicleId.value);
  if (!vehicle) return;

  $q.loading.show({message: 'Calculando rota...'});

  try {
    const destLat = e.latlng.lat;
    const destLon = e.latlng.lng;
    
    mapStore.destination = [destLat, destLon];

    const payload = {
      start_lat: vehicle.last_latitude || 0,
      start_lon: vehicle.last_longitude || 0,
      dest_lat: destLat,
      dest_lon: destLon
    };

    const res = await api.post('/routes/calculate', payload);
    
    mapStore.setRoute(
      res.data.geometry_points,
      res.data.weather_alert,
      [destLat, destLon]
    );

    if (mapStore.routeAlert) {
      $q.notify({
        message: `Rota alterada! Evitando ${mapStore.routeAlert.event_type}`,
        color: 'deep-orange',
        icon: 'warning',
        timeout: 5000,
        position: 'top'
      });
    } else {
      $q.notify({message: 'Rota segura calculada.', color: 'positive', position: 'top'});
    }

  } catch (error) {
    console.error(error);
    $q.notify({message: 'Erro ao calcular rota.', color: 'negative'});
  } finally {
    $q.loading.hide();
  }
};

const fetchData = async () => {
  if (!isAutoRefresh.value) return;
  try {
    // 1. Busca Veículos (Já existia)
    await vehicleStore.fetchAllVehicles();
    
    // 2. Busca Clima (Já existia)
    const weatherRes = await api.get('/weather/alerts');
    weatherEvents.value = weatherRes.data;

    // 3. --- NOVO: BUSCAR BURACOS (Alertas) ---
    // Precisamos de um endpoint que retorne os alertas ativos do tipo POTHOLE
    const alertsRes = await api.get('/alerts?type=POTHOLE&active=true');
    // Mapeia para o formato que seu mapa espera
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    potholes.value = alertsRes.data.map((alert: any) => ({
       id: alert.id,
       latitude: alert.latitude,
       longitude: alert.longitude,
       description: alert.description
    }));

  } catch (e) { 
    console.error(e); 
  } finally { 
    isLoading.value = false; 
  }
};

let pollingInterval: ReturnType<typeof setInterval>;
const toggleAutoRefresh = () => {
  isAutoRefresh.value = !isAutoRefresh.value;
  if (isAutoRefresh.value) void fetchData();
};

onMounted(() => {
  void fetchData();
  void loadGeofences();
  pollingInterval = setInterval(() => { void fetchData(); }, 10000);
});

onUnmounted(() => clearInterval(pollingInterval));
</script>

<style lang="scss" scoped>
.full-height { height: 100vh; }
.sidebar-panel {
  width: 350px; height: 90vh; position: absolute; top: 20px; left: 20px; z-index: 1001;
  border-radius: 16px; overflow: hidden; transition: all 0.3s ease;
}
@media (max-width: 768px) { .sidebar-panel { width: 100%; height: 50vh; bottom: 0; top: auto; left: 0; border-radius: 24px 24px 0 0; } }
.bg-white-glass { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); }
.bg-dark-glass { background: rgba(20,20,30,0.9); backdrop-filter: blur(10px); }
.marker-pin {
  width: 46px; height: 46px; border-radius: 50%; background: #5e6472;
  display: flex; align-items: center; justify-content: center;
  border: 3px solid white; position: relative; z-index: 2; transition: transform 0.2s;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.marker-pin.risk { background: #d32f2f; border-color: #ffcdd2; }
.marker-pin.moving { background: #29c6df; }
.marker-pin.selected { transform: scale(1.2); z-index: 10; border-color: #ffd600; }
.marker-pulse {
  position: absolute; top: 0; left: 0; width: 46px; height: 46px;
  border-radius: 50%; background: rgba(0, 184, 212, 0.5); z-index: 1;
  animation: pulse 2s infinite;
}
.risk-pulse { background: rgba(244, 67, 54, 0.6); animation: pulse-fast 1s infinite; }
@keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(2.5); opacity: 0; } }
@keyframes pulse-fast { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(2.0); opacity: 0; } }
.border-red { border: 1px solid #ef5350; }
.border-blue { border: 1px solid #00b8d4; }
.no-bg { background: transparent !important; border: none !important; }
.absolute-top-center {
  position: absolute; left: 50%; top: 20px; transform: translateX(-50%);
}
</style>