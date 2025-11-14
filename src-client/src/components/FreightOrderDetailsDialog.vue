<template>
  <q-card v-if="order" style="width: 800px; max-width: 95vw;">
    <!-- CABEÇALHO COM CONTEXTO -->
    <q-img src="https://cdn.quasar.dev/img/material.png" style="height: 120px">
      <div class="absolute-bottom bg-transparent">
        <div class="text-h5">{{ order.description || 'Detalhes da Ordem de Frete' }}</div>
        <div class="text-subtitle2">Cliente: {{ order.client.name }}</div>
      </div>
    </q-img>

    <!-- ABAS PARA ORGANIZAÇÃO -->
    <q-tabs v-model="tab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify" narrow-indicator>
      <q-tab name="details" label="Detalhes e Ações" />
      <q-tab name="route" label="Rota e Paradas" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <!-- PAINEL DE DETALHES E AÇÕES -->
      <q-tab-panel name="details" class="q-pa-md">
        <div class="row q-col-gutter-lg">
          <!-- Coluna de Status e Informações -->
          <div class="col-12 col-sm-5">
            <q-list separator bordered padding class="rounded-borders">
              <q-item>
                <q-item-section avatar><q-icon color="primary" name="flag" /></q-item-section>
                <q-item-section><q-item-label overline>STATUS</q-item-label><q-item-label class="text-weight-bold">{{ order.status }}</q-item-label></q-item-section>
              </q-item>
              <q-item v-if="order.driver">
                <q-item-section avatar><q-icon color="primary" name="person" /></q-item-section>
                <q-item-section><q-item-label overline>MOTORISTA</q-item-label><q-item-label>{{ order.driver.full_name }}</q-item-label></q-item-section>
              </q-item>
              <q-item v-if="order.vehicle">
                <q-item-section avatar><q-icon color="primary" name="local_shipping" /></q-item-section>
                <q-item-section><q-item-label overline>VEÍCULO</q-item-label><q-item-label>{{ order.vehicle.brand }} {{ order.vehicle.model }}</q-item-label></q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Coluna de Ações -->
          <div class="col-12 col-sm-7">
            <!-- AÇÕES PARA O GESTOR -->
            <div v-if="authStore.isManager">
              <div class="text-subtitle1 text-weight-medium">Alocação (Gestor)</div>
              <q-select outlined dense v-model="allocationForm.vehicle_id" :options="vehicleOptions" label="Alocar Veículo" emit-value map-options clearable class="q-mt-sm" :loading="vehicleStore.isLoading" />
              <q-select outlined dense v-model="allocationForm.driver_id" :options="driverOptions" label="Alocar Motorista" emit-value map-options clearable class="q-mt-sm" :loading="userStore.isLoading" />
              <q-btn color="primary" label="Salvar Alocação" @click="handleManagerUpdate" class="q-mt-md full-width" :loading="isSubmitting" />
            </div>
            <!-- AÇÕES PARA O MOTORISTA -->
            <div v-else-if="!authStore.isManager && order.status === 'Aberta'">
              <div class="text-subtitle1 text-weight-medium">Atribuir a Mim</div>
              <q-form @submit.prevent="handleDriverClaim">
                <q-select outlined dense v-model="claimForm.vehicle_id" :options="vehicleOptions" label="Selecione um veículo disponível *" emit-value map-options :rules="[val => !!val || 'Selecione um veículo']" :loading="vehicleStore.isLoading" class="q-mt-sm" />
                <q-btn type="submit" color="positive" icon="check" label="Pegar este Frete" class="q-mt-md full-width" :loading="isSubmitting" />
              </q-form>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <!-- PAINEL DA ROTA -->
      <q-tab-panel name="route" class="q-pa-md">
        <q-timeline color="secondary">
          <q-timeline-entry heading>Rota Programada</q-timeline-entry>
          <q-timeline-entry
            v-for="stop in order.stop_points"
            :key="stop.id"
            :title="stop.type"
            :subtitle="new Date(stop.scheduled_time).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })"
            :icon="stop.type === 'Coleta' ? 'archive' : 'unarchive'"
            :color="stop.status === 'Concluído' ? 'positive' : 'secondary'"
          >
            <div class="text-body1">{{ stop.address }}</div>
            <div v-if="stop.cargo_description" class="text-caption text-grey-7">{{ stop.cargo_description }}</div>
          </q-timeline-entry>
        </q-timeline>
      </q-tab-panel>
    </q-tab-panels>
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

const tab = ref('details');
const isSubmitting = ref(false);
const allocationForm = ref<Partial<FreightOrderUpdate>>({});
const claimForm = ref<Partial<FreightOrderClaim>>({});

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