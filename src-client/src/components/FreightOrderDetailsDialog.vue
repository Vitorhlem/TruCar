<template>
  <q-card style="width: 900px; max-width: 95vw; display: flex; flex-direction: column; max-height: 90vh;">
    
    <q-toolbar :class="headerClass" class="text-white">
      <q-icon name="local_shipping" size="md" />
      <q-toolbar-title>
        <div class="text-subtitle2 text-uppercase opacity-80">Ordem #{{ order.id }}</div>
        <div class="text-h6" style="line-height: 1.1;">{{ order.client.name }}</div>
      </q-toolbar-title>
      <q-btn flat round dense icon="close" v-close-popup />
    </q-toolbar>

    <q-separator />

    <q-card-section class="scroll col q-pa-none">
      <div class="row fit">
        
        <div class="col-12 col-md-7 q-pa-md border-right-md">
          <div class="text-h6 q-mb-md text-grey-9">Rota e Paradas</div>
          
          <q-timeline color="secondary" class="q-ml-sm">
            <q-timeline-entry
              v-for="(stop, index) in order.stop_points"
              :key="stop.id"
              :icon="stop.type === 'Coleta' ? 'inventory_2' : 'local_shipping'"
              :color="getStopColor(stop)"
            >
              <template v-slot:title>
                <div class="text-subtitle2 text-weight-bold">{{ stop.type }}</div>
              </template>
              <template v-slot:subtitle>
                {{ new Date(stop.scheduled_time).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) }}
              </template>
              
              <q-card flat bordered class="bg-grey-1">
                <q-card-section class="q-py-sm">
                  <div class="text-body2">{{ stop.address }} - {{ stop.city }}/{{ stop.state }}</div>
                  <div v-if="stop.cargo_description" class="text-caption text-grey-7 q-mt-xs">
                    <q-icon name="description" size="xs" /> {{ stop.cargo_description }}
                  </div>
                </q-card-section>
              </q-card>
            </q-timeline-entry>
          </q-timeline>

          <q-separator class="q-my-md" />
          
          <div class="text-subtitle2 text-grey-7">Descrição Geral</div>
          <div class="text-body1">{{ order.description || 'Sem descrição adicional.' }}</div>
        </div>

        <div class="col-12 col-md-5 bg-grey-1 column">
          
          <div class="q-pa-md">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-overline text-grey-7">Status Atual</div>
                <div class="text-h5 text-weight-bold text-primary">{{ order.status }}</div>
              </q-card-section>
              <q-separator />
              <q-list dense>
                <q-item>
                  <q-item-section avatar><q-icon name="person" color="grey-7" /></q-item-section>
                  <q-item-section>
                    <q-item-label caption>Motorista</q-item-label>
                    <q-item-label>{{ order.driver?.full_name || 'Não atribuído' }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section avatar><q-icon name="directions_car" color="grey-7" /></q-item-section>
                  <q-item-section>
                    <q-item-label caption>Veículo</q-item-label>
                    <q-item-label>{{ order.vehicle ? `${order.vehicle.brand} ${order.vehicle.model}` : 'Não atribuído' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card>
          </div>

          <q-space />

          <div class="q-pa-md">
            
            <div v-if="authStore.isManager">
              <div class="text-subtitle2 q-mb-sm">Gerenciar Alocação</div>
              <q-select 
                outlined dense bg-color=""
                v-model="allocationForm.vehicle_id" 
                :options="vehicleOptions" 
                label="Veículo" 
                emit-value map-options 
                class="q-mb-sm" 
              >
                <template v-slot:prepend><q-icon name="local_shipping" /></template>
              </q-select>
              
              <q-select 
                outlined dense bg-color=""
                v-model="allocationForm.driver_id" 
                :options="driverOptions" 
                label="Motorista" 
                emit-value map-options 
                class="q-mb-md"
              >
                <template v-slot:prepend><q-icon name="person" /></template>
              </q-select>
              
              <q-btn 
                color="primary" 
                label="Salvar Alterações" 
                class="full-width shadow-2" 
                :loading="isSubmitting" 
                @click="handleManagerUpdate"
              />
            </div>

            <div v-else-if="!authStore.isManager && order.status === 'Aberta'">
              <q-banner class="bg-blue-1 text-primary q-mb-md rounded-borders">
                Este frete está disponível. Selecione um veículo para aceitá-lo.
              </q-banner>
              <q-form @submit.prevent="handleDriverClaim">
                <q-select 
                  outlined dense bg-color="white"
                  v-model="claimForm.vehicle_id" 
                  :options="vehicleOptions" 
                  label="Selecione seu Veículo" 
                  emit-value map-options 
                  :rules="[val => !!val || 'Obrigatório']"
                />
                <q-btn 
                  type="submit" 
                  color="positive" 
                  icon="check_circle" 
                  label="Aceitar Frete" 
                  class="full-width q-mt-md shadow-2" 
                  :loading="isSubmitting" 
                />
              </q-form>
            </div>

          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useFreightOrderStore } from 'stores/freight-order-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useUserStore } from 'stores/user-store';
import type { FreightOrder, FreightOrderUpdate, FreightOrderClaim, FreightStopPoint } from 'src/models/freight-order-models';
import type { User } from 'src/models/auth-models';

const props = defineProps<{ order: FreightOrder; }>();
const emit = defineEmits(['close']);

const authStore = useAuthStore();
const freightOrderStore = useFreightOrderStore();
const vehicleStore = useVehicleStore();
const userStore = useUserStore();

const isSubmitting = ref(false);
const allocationForm = ref<Partial<FreightOrderUpdate>>({});
const claimForm = ref<Partial<FreightOrderClaim>>({});

const headerClass = computed(() => {
  switch (props.order.status) {
    case 'Atribuída': return 'bg-primary';
    case 'Em Trânsito': return 'bg-orange-8';
    case 'Entregue': return 'bg-positive';
    case 'Cancelada': return 'bg-negative';
    default: return 'bg-blue-grey-8';
  }
});

function getStopColor(stop: FreightStopPoint) {
  if (stop.status === 'Concluído') return 'positive';
  if (stop.type === 'Coleta') return 'accent';
  return 'secondary';
}

watch(() => props.order, (newOrder) => {
  if (newOrder) {
    allocationForm.value = {
      vehicle_id: newOrder.vehicle?.id || null,
      driver_id: newOrder.driver?.id || null,
    };
    claimForm.value = {};
  }
}, { immediate: true });

const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id })));
const driverOptions = computed(() => userStore.users.filter((u: User) => u.role === 'driver').map(d => ({ label: d.full_name, value: d.id })));

async function handleManagerUpdate() {
  isSubmitting.value = true;
  try {
    await freightOrderStore.updateFreightOrder(props.order.id, allocationForm.value);
    emit('close');
  } finally { isSubmitting.value = false; }
}

async function handleDriverClaim() {
  if (!claimForm.value.vehicle_id) return;
  isSubmitting.value = true;
  try {
    await freightOrderStore.claimFreightOrder(props.order.id, claimForm.value as FreightOrderClaim);
    emit('close');
  } finally { isSubmitting.value = false; }
}

onMounted(() => {
  void vehicleStore.fetchAllVehicles();
  if (authStore.isManager) {
    void userStore.fetchAllUsers();
  }
});
</script>

<style scoped>
.border-right-md {
  border-right: 1px solid #e0e0e0;
}
@media (max-width: 1023px) {
  .border-right-md { border-right: none; border-bottom: 1px solid #e0e0e0; }
}
.opacity-80 { opacity: 0.8; }

/* Dark Mode support */
body.body--dark .bg-grey-1 { background: #1d1d1d !important; }
body.body--dark .border-right-md { border-color: rgba(255,255,255,0.1); }
</style>