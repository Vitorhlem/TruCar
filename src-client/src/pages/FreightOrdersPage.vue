<template>
  <q-page padding class="bg-grey-1">
    
    <div class="row q-col-gutter-md q-mb-lg">
      <div class="col-12 flex items-center justify-between">
        <div>
           <h1 class="text-h4 text-weight-bold q-my-none">Gestão de Fretes</h1>
           <div class="text-subtitle2 text-grey-7">Acompanhe o fluxo de entregas em tempo real</div>
        </div>
        <q-btn
          v-if="authStore.isManager"
          @click="openCreateDialog"
          color="primary"
          icon="add"
          label="Nova Ordem"
          unelevated
          size="md"
          class="shadow-2"
        />
      </div>
    </div>

    <div class="row q-col-gutter-md q-mb-lg">
       <div class="col-6 col-sm-3">
          <q-card flat bordered class="bg-white">
             <q-card-section class="row items-center justify-between q-py-sm">
                <div>
                   <div class="text-caption text-grey-7 text-uppercase">Abertas</div>
                   <div class="text-h4 text-weight-bold text-blue-grey">{{ openOrders.length }}</div>
                </div>
                <q-icon name="pending_actions" size="md" color="blue-grey-3" />
             </q-card-section>
          </q-card>
       </div>
       <div class="col-6 col-sm-3">
          <q-card flat bordered class="bg-white">
             <q-card-section class="row items-center justify-between q-py-sm">
                <div>
                   <div class="text-caption text-grey-7 text-uppercase">Atribuídas</div>
                   <div class="text-h4 text-weight-bold text-primary">{{ claimedOrders.length }}</div>
                </div>
                <q-icon name="assignment_ind" size="md" color="blue-2" />
             </q-card-section>
          </q-card>
       </div>
       <div class="col-6 col-sm-3">
          <q-card flat bordered class="bg-white">
             <q-card-section class="row items-center justify-between q-py-sm">
                <div>
                   <div class="text-caption text-grey-7 text-uppercase">Em Trânsito</div>
                   <div class="text-h4 text-weight-bold text-orange">{{ inTransitOrders.length }}</div>
                </div>
                <q-icon name="local_shipping" size="md" color="orange-2" />
             </q-card-section>
          </q-card>
       </div>
       <div class="col-6 col-sm-3">
          <q-card flat bordered class="bg-white">
             <q-card-section class="row items-center justify-between q-py-sm">
                <div>
                   <div class="text-caption text-grey-7 text-uppercase">Entregues</div>
                   <div class="text-h4 text-weight-bold text-positive">{{ deliveredOrders.length }}</div>
                </div>
                <q-icon name="check_circle" size="md" color="green-2" />
             </q-card-section>
          </q-card>
       </div>
    </div>

    <div v-if="freightOrderStore.isLoading" class="flex flex-center" style="height: 400px">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <div v-else class="row q-col-gutter-md" style="min-height: 60vh;">
      
      <div class="col-12 col-md-3">
        <div class="kanban-column">
          <div class="column-header text-blue-grey-9 bg-blue-grey-1 border-blue-grey">
            <div class="text-subtitle2 text-weight-bold">ABERTA</div>
            <q-badge color="blue-grey" text-color="white" :label="openOrders.length" />
          </div>
          <q-scroll-area class="column-body">
            <div class="q-gutter-y-md q-pa-sm">
              <FreightOrderCard v-for="order in openOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
              <div v-if="openOrders.length === 0" class="text-center text-grey-5 q-pa-md text-caption">Nenhuma ordem.</div>
            </div>
          </q-scroll-area>
        </div>
      </div>

      <div class="col-12 col-md-3">
        <div class="kanban-column">
          <div class="column-header text-primary bg-blue-1 border-primary">
            <div class="text-subtitle2 text-weight-bold">ATRIBUÍDA</div>
            <q-badge color="primary" text-color="white" :label="claimedOrders.length" />
          </div>
          <q-scroll-area class="column-body">
            <div class="q-gutter-y-md q-pa-sm">
              <FreightOrderCard v-for="order in claimedOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
            </div>
          </q-scroll-area>
        </div>
      </div>

      <div class="col-12 col-md-3">
        <div class="kanban-column">
          <div class="column-header text-orange-9 bg-orange-1 border-orange">
            <div class="text-subtitle2 text-weight-bold">EM TRÂNSITO</div>
            <q-badge color="orange-8" text-color="white" :label="inTransitOrders.length" />
          </div>
          <q-scroll-area class="column-body">
            <div class="q-gutter-y-md q-pa-sm">
              <FreightOrderCard v-for="order in inTransitOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
            </div>
          </q-scroll-area>
        </div>
      </div>

      <div class="col-12 col-md-3">
        <div class="kanban-column">
          <div class="column-header text-green-9 bg-green-1 border-green">
            <div class="text-subtitle2 text-weight-bold">ENTREGUE</div>
            <q-badge color="positive" text-color="white" :label="deliveredOrders.length" />
          </div>
          <q-scroll-area class="column-body">
            <div class="q-gutter-y-md q-pa-sm">
              <FreightOrderCard v-for="order in deliveredOrders" :key="order.id" :order="order" @click="openDetailsDialog(order)" />
            </div>
          </q-scroll-area>
        </div>
      </div>

    </div>

    <q-dialog v-model="isCreateDialogOpen" maximized transition-show="slide-up" transition-hide="slide-down">
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
  background-color: #ebecf0; // Cor clássica de fundo Kanban
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 280px); // Altura dinâmica
  min-height: 500px;
}

.column-header {
  padding: 12px 16px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  border-top: 3px solid transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.column-body {
  flex-grow: 1;
  height: 100%; // Importante para o q-scroll-area
}

/* Cores das bordas dos headers */
.border-blue-grey { border-top-color: #607d8b; }
.border-primary { border-top-color: var(--q-primary); }
.border-orange { border-top-color: #ff9800; }
.border-green { border-top-color: var(--q-positive); }

/* Dark Mode Adjustments */
body.body--dark .bg-grey-1 { background-color: #121212 !important; }
body.body--dark .bg-white { background-color: #1d1d1d !important; color: #fff; }
body.body--dark .kanban-column { background-color: #1d1d1d; border: 1px solid rgba(255,255,255,0.1); }
body.body--dark .column-header { background-color: #2d2d2d !important; color: #fff !important; }
</style>