import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

// Interfaces
export interface Geofence {
  id: number;
  name: string;
  type: string;
  polygon_points: [number, number][];
}

export interface RouteAlert {
  id: number;
  event_type: string;
  description: string;
  severity: string;
  affected_lat: number;
  affected_lon: number;
  affected_radius_km: number;
  detected_at?: string;
}

export const useMapStore = defineStore('map', () => {
  // --- ESTADOS ---
  const routeCoordinates = ref<[number, number][]>([]);
  const routeAlert = ref<RouteAlert | null>(null);
  const destination = ref<[number, number] | null>(null);
  
  const geofences = ref<Geofence[]>([]);
  const isDrawingMode = ref(false);
  const drawingPoints = ref<[number, number][]>([]);

  // --- PERSISTÊNCIA (LOCAL STORAGE) ---
  // 1. Carregar dados salvos ao iniciar
  const storedGeofences = localStorage.getItem('trucar_geofences');
  if (storedGeofences) {
    try {
      geofences.value = JSON.parse(storedGeofences);
    } catch (e) {
      console.error('Erro ao carregar cercas salvas', e);
    }
  }

  const storedRoute = localStorage.getItem('trucar_active_route');
  if (storedRoute) {
    try {
      const parsed = JSON.parse(storedRoute);
      routeCoordinates.value = parsed.coords || [];
      routeAlert.value = parsed.alert || null;
      destination.value = parsed.dest || null;
    } catch (e) {
      console.error('Erro ao carregar rota salva', e);
    }
  }

  // 2. Salvar automaticamente quando mudar (Watchers)
  watch(geofences, (newVal) => {
    localStorage.setItem('trucar_geofences', JSON.stringify(newVal));
  }, { deep: true });

  watch([routeCoordinates, routeAlert, destination], () => {
    localStorage.setItem('trucar_active_route', JSON.stringify({
      coords: routeCoordinates.value,
      alert: routeAlert.value,
      dest: destination.value
    }));
  }, { deep: true });

  // --- AÇÕES ---
  
  function setRoute(coords: [number, number][], alert: RouteAlert | null, dest: [number, number]) {
    routeCoordinates.value = coords;
    routeAlert.value = alert;
    destination.value = dest;
  }

  function clearRoute() {
    routeCoordinates.value = [];
    routeAlert.value = null;
    destination.value = null;
    // Limpa também do storage
    localStorage.removeItem('trucar_active_route');
  }

  function addGeofence(fence: Geofence) {
    geofences.value.push(fence);
  }

  function removeGeofence(id: number) {
    geofences.value = geofences.value.filter(f => f.id !== id);
  }

  function setGeofences(fences: Geofence[]) {
    geofences.value = fences;
  }

  return {
    // State
    routeCoordinates,
    routeAlert,
    destination,
    geofences,
    isDrawingMode,
    drawingPoints,
    // Actions
    setRoute,
    clearRoute,
    addGeofence,
    removeGeofence,
    setGeofences
  };
});