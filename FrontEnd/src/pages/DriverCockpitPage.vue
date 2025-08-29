<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h4 text-weight-bold q-my-none">Meu Dia</h1>
      <q-btn flat round dense icon="refresh" :loading="store.isLoading" @click="refreshData" />
    </div>

    <!-- 1. TAREFA ATIVA -->
    <q-card v-if="store.activeFreightOrder" class="bg-primary text-white q-mb-lg floating-card">
      <q-card-section>
        <div class="text-overline">EM ROTA</div>
        <div class="text-h6 ellipsis">{{ store.activeFreightOrder.description || 'Frete sem descrição' }}</div>
      </q-card-section>
      <q-separator dark />
      <q-card-actions>
        <q-btn flat class="full-width" @click="openDriverDialog(store.activeFreightOrder)">
          Ver Próxima Parada / Concluir
        </q-btn>
      </q-card-actions>
    </q-card>

    <!-- 2. PRÓXIMAS TAREFAS -->
    <div class="q-mb-lg">
      <div class="text-h5 q-mb-sm">Próximas Tarefas ({{ store.claimedFreightOrders.length }})</div>
      <q-card flat bordered>
        <q-list separator>
          <q-item v-if="store.isLoading && store.claimedFreightOrders.length === 0"><q-item-section><q-skeleton type="text" /></q-item-section></q-item>
          <q-item v-if="!store.isLoading && store.claimedFreightOrders.length === 0" class="text-grey-7 q-pa-md">Nenhuma tarefa na fila.</q-item>
          <q-item v-else v-for="order in store.claimedFreightOrders" :key="order.id" clickable @click="openDriverDialog(order)">
            <q-item-section avatar><q-icon name="assignment_turned_in" color="secondary" /></q-item-section>
            <q-item-section>
              <q-item-label>{{ order.description || 'Frete sem descrição' }}</q-item-label>
              <q-item-label caption>{{ order.stop_points.length }} paradas. Cliente: {{ order.client.name }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>

    <!-- 3. MURAL DE OPORTUNIDADES -->
    <div>
      <div class="text-h5 q-mb-sm">Mural de Oportunidades ({{ store.openOrders.length }})</div>
      <q-card flat bordered>
        <q-list separator>
          <q-item v-if="store.isLoading && store.openOrders.length === 0"><q-item-section><q-skeleton type="text" /></q-item-section></q-item>
          <q-item v-if="!store.isLoading && store.openOrders.length === 0" class="text-grey-7 q-pa-md">Nenhuma oportunidade disponível.</q-item>
          <!-- --- INÍCIO DA CORREÇÃO: Adicionamos o @click de volta --- -->
          <q-item v-else v-for="order in store.openOrders" :key="order.id" clickable @click="openClaimDialog(order)">
          <!-- --- FIM DA CORREÇÃO --- -->
            <q-item-section avatar><q-icon name="add_shopping_cart" color="positive" /></q-item-section>
            <q-item-section>
              <q-item-label>{{ order.description || 'Frete sem descrição' }}</q-item-label>
              <q-item-label caption>{{ order.stop_points.length }} paradas. Cliente: {{ order.client.name }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>

    <!-- Diálogos -->
    <q-dialog v-model="isClaimDialogOpen">
      <ClaimFreightDialog v-if="selectedOrderForClaim" :order="selectedOrderForClaim" @close="isClaimDialogOpen = false" />
    </q-dialog>
    <q-dialog v-model="isDriverDialogOpen">
      <DriverFreightDialog @close="handleDriverDialogClose" />
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useFreightOrderStore } from 'stores/freight-order-store';
import ClaimFreightDialog from 'components/ClaimFreightDialog.vue';
import DriverFreightDialog from 'components/DriverFreightDialog.vue';
import type { FreightOrder } from 'src/models/freight-order-models';

const store = useFreightOrderStore();
const isClaimDialogOpen = ref(false);
const isDriverDialogOpen = ref(false);
const selectedOrderForClaim = ref<FreightOrder | null>(null);

// Esta função agora é usada pelo template
function openClaimDialog(order: FreightOrder) {
  selectedOrderForClaim.value = order;
  isClaimDialogOpen.value = true;
}

function openDriverDialog(order: FreightOrder) {
  void store.fetchOrderDetails(order.id);
  isDriverDialogOpen.value = true;
}

function handleDriverDialogClose() {
  isDriverDialogOpen.value = false;
  store.activeOrderDetails = null;
  refreshData();
}

function refreshData() {
  void store.fetchOpenOrders();
  void store.fetchMyPendingOrders();
}

onMounted(() => {
  refreshData();
});
</script>