<!-- ARQUIVO: src/pages/LiveMapPage.vue -->
<template>
  <q-page class="flex">
    <div class="col relative-position">
      <div v-if="isLoading" class="absolute-center z-top text-center">
        <q-spinner-dots color="primary" size="40px" />
        <div class="q-mt-md text-primary">Carregando mapa e posições...</div>
      </div>
      <l-map ref="map" v-model:zoom="zoom" :center="center" :use-global-leaflet="false" class="full-height">
        <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" attribution="&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>"></l-tile-layer>
        <l-marker v-for="vehicle in connectedVehicles" :key="vehicle.id" :lat-lng="[vehicle.last_latitude!, vehicle.last_longitude!]">
          <l-popup>
            <div class="text-weight-bold">{{ vehicle.brand }} {{ vehicle.model }}</div>
            <div>Horímetro: {{ vehicle.current_engine_hours?.toFixed(1) }} Horas</div>
            <div class="q-mt-sm"><q-btn size="sm" dense flat color="primary" @click="centerOnVehicle(vehicle)">Centralizar</q-btn></div>
          </l-popup>
          <l-icon :icon-size="[40, 40]">
            <q-icon name="agriculture" color="primary" size="40px" style="background: white; border-radius: 50%; padding: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"/>
          </l-icon>
        </l-marker>
      </l-map>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { LMap, LTileLayer, LMarker, LPopup, LIcon } from "@vue-leaflet/vue-leaflet";
import { useVehicleStore } from 'stores/vehicle-store';
import type { Vehicle } from 'src/models/vehicle-models';

const vehicleStore = useVehicleStore();
const zoom = ref(5);
// --- CORREÇÃO DEFINITIVA: Tipamos como um array de 2 números ---
const center = ref<[number, number]>([-14.2350, -51.9253]);
const isLoading = ref(true);

const connectedVehicles = computed(() =>
  vehicleStore.vehicles.filter(
    (v): v is Vehicle & { last_latitude: number; last_longitude: number } =>
      !!v.telemetry_device_id && typeof v.last_latitude === 'number' && typeof v.last_longitude === 'number'
  )
);

let pollingInterval: NodeJS.Timeout | null = null;

onMounted(async () => {
  isLoading.value = true;
  await vehicleStore.fetchAllVehicles({ rowsPerPage: 500 });
  const firstVehicle = connectedVehicles.value[0];
  if (firstVehicle) centerOnVehicle(firstVehicle);
  isLoading.value = false;
  pollingInterval = setInterval(() => { void vehicleStore.fetchAllVehicles({ rowsPerPage: 500 }); }, 15000);
});

onUnmounted(() => { if (pollingInterval) clearInterval(pollingInterval); });

function centerOnVehicle(vehicle: Vehicle) {
  if (vehicle.last_latitude && vehicle.last_longitude) {
    center.value = [vehicle.last_latitude, vehicle.last_longitude];
    zoom.value = 17;
  }
}
</script>