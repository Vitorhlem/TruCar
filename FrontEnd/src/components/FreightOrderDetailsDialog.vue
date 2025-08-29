<template>
  <q-card v-if="order" style="width: 700px; max-width: 90vw;">
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>{{ order.description || 'Detalhes da Ordem de Frete' }}</q-toolbar-title>
      <q-btn flat round dense icon="close" @click="emit('close')" />
    </q-toolbar>

      <div class="row q-col-gutter-lg">
        <!-- Coluna Esquerda: Ações e Status -->
        <div class="col-12 col-md-5">
          <q-list bordered separator>
            <q-item><q-item-section><q-item-label overline>CLIENTE</q-item-label><q-item-label>{{ order.client.name }}</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label overline>STATUS</q-item-label><q-item-label>{{ order.status }}</q-item-label></q-item-section></q-item>
          </q-list>

          <!-- ########################################## -->
          <!-- ### BLOCO DE AÇÕES PARA O GESTOR       ### -->
          <!-- ########################################## -->
          <div v-if="authStore.isManager" class="q-mt-lg">
            <div class="text-subtitle1 q-mb-sm">Alocação (Gestor)</div>
            <q-select outlined v-model="allocationForm.vehicle_id" :options="vehicleOptions" label="Veículo" emit-value map-options clearable class="q-mb-md" :loading="vehicleStore.isLoading" />
            <q-select outlined v-model="allocationForm.driver_id" :options="driverOptions" label="Motorista" emit-value map-options clearable :loading="userStore.isLoading" />
            <q-btn color="primary" label="Salvar Alocação" @click="handleManagerUpdate" class="q-mt-md full-width" :loading="isSubmitting" />
          </div>

          <!-- ########################################## -->
          <!-- ### BLOCO DE AÇÕES PARA O MOTORISTA    ### -->
          <!-- ########################################## -->
          <div v-else-if="!authStore.isManager && order.status === 'Aberta'" class="q-mt-lg">
            <div class="text-subtitle1 q-mb-sm">Atribuir a Mim</div>
            <q-select outlined v-model="claimForm.vehicle_id" :options="vehicleOptions" label="Selecione um veículo disponível *" emit-value map-options :rules="[val => !!val || 'Selecione um veículo']" :loading="vehicleStore.isLoading" />
            <q-btn color="positive" label="Pegar este Frete" @click="handleDriverClaim" class="q-mt-md full-width" :loading="isSubmitting" />
          </div>
        
        <!-- Coluna Direita: Rota/Paradas -->
        <div class="col-12 col-md-7">
          <div class="text-subtitle1 q-mb-sm">Rota e Paradas</div>
          <q-timeline color="secondary" dense>
            <q-timeline-entry
              v-for="stop in order.stop_points"
              :key="stop.id"
              :title="`${stop.type}: ${stop.address}`"
              :subtitle="new Date(stop.scheduled_time).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })"
              :icon="stop.type === 'Coleta' ? 'archive' : 'unarchive'"
            >
              <div>{{ stop.cargo_description }}</div>
            </q-timeline-entry>
          </q-timeline>
        </div>
      </div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useFreightOrderStore } from 'stores/freight-order-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useUserStore } from 'stores/user-store';
import type { FreightOrder, FreightOrderUpdate, FreightOrderClaim } from 'src/models/freight-order-models';
import type { User } from 'src/models/auth-models';

const props = defineProps<{
  order: FreightOrder;
}>();

const emit = defineEmits(['close']);
const authStore = useAuthStore();
const freightOrderStore = useFreightOrderStore();
const vehicleStore = useVehicleStore();
const userStore = useUserStore();

const isSubmitting = ref(false);
// Formulários separados para cada ação
const allocationForm = ref<Partial<FreightOrderUpdate>>({}); // Para o gestor
const claimForm = ref<Partial<FreightOrderClaim>>({}); // Para o motorista

watch(() => props.order, (newOrder) => {
  if (newOrder) {
    // Sempre popula o formulário do gestor para referência
    allocationForm.value = {
      vehicle_id: newOrder.vehicle?.id || null,
      driver_id: newOrder.driver?.id || null,
    };
    // Reseta o formulário do motorista
    claimForm.value = {};
  }
}, { immediate: true });

const vehicleOptions = computed(() => vehicleStore.availableVehicles.map(v => ({ label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`, value: v.id })));
const driverOptions = computed(() => userStore.users.filter((u: User) => u.role === 'driver').map(d => ({ label: d.full_name, value: d.id })));

// Ação do GESTOR
async function handleManagerUpdate() {
  isSubmitting.value = true;
  try {
    await freightOrderStore.updateFreightOrder(props.order.id, allocationForm.value);
    emit('close');
  } finally { isSubmitting.value = false; }
}

// Ação do MOTORISTA
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
  // A busca de todos os usuários só é feita se o usuário for um gestor
  if (authStore.isManager) {
    void userStore.fetchAllUsers();
  }
});
</script>