<template>
  <q-page class="column no-wrap">
    <div class="q-pa-md text-h5 text-weight-bold">
      {{ selectedVehicle ? `Rastreando: ${selectedVehicle.brand} ${selectedVehicle.model}` : 'Frota em Movimento' }}
    </div>
    
    <div v-if="!selectedVehicle" class="col q-pa-md row q-col-gutter-md">
      <div v-if="activeJourneys.length === 0 && !journeyStore.isLoading" class="full-width text-center q-pa-xl text-grey-7">
        <q-icon name="explore_off" size="4em" />
        <p class="q-mt-md">Nenhum veículo em viagem no momento.</p>
      </div>
      <div
        v-for="journey in activeJourneys"
        :key="journey.id"
        class="col-xs-12 col-sm-6 col-md-4 col-lg-3"
      >
        <q-card
          flat bordered
          class="vehicle-card cursor-pointer"
          @click="selectVehicle(journey.vehicle)"
          @mousemove="handleCardMouseMove"
          @mouseleave="resetCardTransform"
        >
          <q-card-section>
            <div class="text-overline text-orange-8">{{ journey.driver.full_name }}</div>
            <div class="text-h6 ellipsis">{{ journey.vehicle.brand }} {{ journey.vehicle.model }}</div>
            <div class="text-caption text-grey-8">{{ journey.vehicle.license_plate }}</div>
          </q-card-section>
          <q-separator />
          <q-card-section class="text-caption">
            <q-icon name="place" /> {{ journey.destination_address || journey.trip_description }}
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div v-else class="col row q-pa-md q-col-gutter-md">
      <div class="col-12 col-md-9 full-height">
         <l-map
            v-if="selectedVehicle.last_latitude && selectedVehicle.last_longitude"
            ref="map"
            :zoom="zoom"
            :center="center"
            :use-global-leaflet="false"
            style="height: 100%; border-radius: 4px;"
          >
            <l-tile-layer url="https:
            <l-marker :lat-lng="[selectedVehicle.last_latitude, selectedVehicle.last_longitude]">
              <l-icon :icon-url="carIcon" :icon-size="[35, 35]" />
            </l-marker>
          </l-map>
          <q-card v-else flat bordered class="full-height flex flex-center">
            <div class="text-grey-7">Sem dados de localização para este veículo.</div>
          </q-card>
      </div>
      <div class="col-12 col-md-3 full-height">
        <q-card flat bordered class="full-height">
          <q-card-section>
            <div class="text-h6">Dados em Tempo Real</div>
            <div class="text-subtitle2">{{ selectedVehicle.brand }} {{ selectedVehicle.model }}</div>
          </q-card-section>
          <q-separator />
          <q-list separator>
            <q-item><q-item-section><q-item-label caption>Velocidade Atual</q-item-label><q-item-label>Em desenvolvimento</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>Nível de Combustível</q-item-label><q-item-label>Em desenvolvimento</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>Rotação do Motor (RPM)</q-item-label><q-item-label>Em desenvolvimento</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>Saúde do Motor</q-item-label><q-item-label>Em desenvolvimento</q-item-label></q-item-section></q-item>
          </q-list>
          <q-space />
           <q-card-actions align="center">
            <q-btn @click="selectedVehicleId = null" color="primary" label="Voltar para Visão Geral" flat />
           </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import "leaflet/dist/leaflet.css";

import { LMap, LTileLayer, LMarker, LIcon } from "@vue-leaflet/vue-leaflet";

import { ref, onMounted, computed, nextTick, watch } from 'vue';
import { useJourneyStore } from 'stores/journey-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useAuthStore } from 'stores/auth-store';
import { type Vehicle } from 'src/models/vehicle-models';
import carIcon from 'src/assets/car-icon.png';

const journeyStore = useJourneyStore();
const vehicleStore = useVehicleStore();
const authStore = useAuthStore();
const selectedVehicleId = ref<number | null>(null);
const zoom = ref(5);
const center = ref<[number, number]>([-14.2350, -51.9253]);

const map = ref<InstanceType<typeof LMap> | null>(null);

const activeJourneys = computed(() => journeyStore.activeJourneys);

const selectedVehicle = computed(() => {
  if (!selectedVehicleId.value) return null;
  return vehicleStore.vehicles.find(v => v.id === selectedVehicleId.value);
});


watch(vehicleStore.vehicles, (newVehicles) => {
  const vehicle = newVehicles[0];
  if (newVehicles.length === 1 && !authStore.isManager && vehicle) {
    if(vehicle.last_latitude && vehicle.last_longitude) {
      center.value = [vehicle.last_latitude, vehicle.last_longitude];
      zoom.value = 15;
    }
  }
});

async function selectVehicle(vehicle: Vehicle) {
  selectedVehicleId.value = vehicle.id;
  if(vehicle.last_latitude && vehicle.last_longitude) {
    center.value = [vehicle.last_latitude, vehicle.last_longitude];
    zoom.value = 15;
  }
  await nextTick();
  map.value?.leafletObject?.invalidateSize();
}

function handleCardMouseMove(evt: MouseEvent) {
  const card = evt.currentTarget as HTMLElement;
  const { top, left, width, height } = card.getBoundingClientRect();
  const x = evt.clientX - left;
  const y = evt.clientY - top;
  const rotateX = -10 * ((y - height / 2) / height);
  const rotateY = 10 * ((x - width / 2) / width);
  card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
}
function resetCardTransform(evt: MouseEvent) {
  const card = evt.currentTarget as HTMLElement;
  card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
}

onMounted(async () => {

  await journeyStore.fetchAllJourneys();
  await vehicleStore.fetchAllVehicles();
});
</script>

<style lang="scss" scoped>
.vehicle-card {
  transition: transform 0.2s ease-out;
  will-change: transform;
}
.full-height {
  height: 100%;
}
</style>