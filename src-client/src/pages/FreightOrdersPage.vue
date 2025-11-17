<template>
  <q-page padding>

    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h4 text-weight-bold q-my-none">Ordens de Frete</h1>
      <q-btn
        v-if="authStore.isManager"
        @click="openCreateDialog"
        color="primary"
        icon="add"
        label="Nova Ordem de Frete"
        unelevated
      />
    </div>


    <div v-if="freightOrderStore.isLoading" class="text-center q-pa-xl">
      <q-spinner-dots color="primary" size="40px" />
    </div>


    <div v-else class="row q-col-gutter-md">

      <div class="col-12 col-md-3">
        <q-item-label header class="text-overline">Aberta ({{ openOrders.length }})</q-item-label>
        <div class="kanban-column q-gutter-y-md">
          <FreightOrderCard v-for="order in openOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
        </div>
      </div>

      <div class="col-12 col-md-3">
        <q-item-label header class="text-overline">Atribuída ({{ claimedOrders.length }})</q-item-label>
        <div class="kanban-column q-gutter-y-md">
          <FreightOrderCard v-for="order in claimedOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
        </div>
      </div>

      <div class="col-12 col-md-3">
        <q-item-label header class="text-overline">Em Trânsito ({{ inTransitOrders.length }})</q-item-label>
        <div class="kanban-column q-gutter-y-md">
          <FreightOrderCard v-for="order in inTransitOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
        </div>
      </div>

      <div class="col-12 col-md-3">
        <q-item-label header class="text-overline">Entregue ({{ deliveredOrders.length }})</q-item-label>
        <div class="kanban-column q-gutter-y-md">
          <FreightOrderCard v-for="order in deliveredOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
        </div>
      </div>
    </div>


    <q-dialog v-model="isCreateDialogOpen"  maximized>
      <CreateFreightOrderForm @close="isCreateDialogOpen = false" />
    </q-dialog>
    <q-dialog v-model="isDetailsDialogOpen">
      <FreightOrderDetailsDialog v-if="selectedOrderForAction" :order="selectedOrderForAction" @close="isDetailsDialogOpen = false" />
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useFreightOrderStore } from 'stores/freight-order-store';
import FreightOrderCard from '../components/FreightOrderCard.vue';
import CreateFreightOrderForm from '../components/CreateFreightOrderForm.vue';
import FreightOrderDetailsDialog from '../components/FreightOrderDetailsDialog.vue';
import type { FreightOrder } from 'src/models/freight-order-models';

const authStore = useAuthStore();
const freightOrderStore = useFreightOrderStore();
const isCreateDialogOpen = ref(false);
const isDetailsDialogOpen = ref(false);
const selectedOrderForAction = ref<FreightOrder | null>(null);

const openOrders = computed(() => freightOrderStore.freightOrders.filter(o => o.status === 'Aberta'));
const claimedOrders = computed(() => freightOrderStore.freightOrders.filter(o => o.status === 'Atribuída'));
const inTransitOrders = computed(() => freightOrderStore.freightOrders.filter(o => o.status === 'Em Trânsito'));
const deliveredOrders = computed(() => freightOrderStore.freightOrders.filter(o => o.status === 'Entregue'));

function openCreateDialog() {
  isCreateDialogOpen.value = true;
}

function openDetailsDialog(order: FreightOrder) {
  selectedOrderForAction.value = order;
  isDetailsDialogOpen.value = true;
}

onMounted(() => {
  void freightOrderStore.fetchAllFreightOrders();
});
</script>

<style scoped lang="scss">
.kanban-column {
  background-color: $grey-2;
  border-radius: 4px;
  padding: 8px;
  min-height: 50vh;
}
body.body--dark .kanban-column {
  background-color: $grey-9;
}
</style>
