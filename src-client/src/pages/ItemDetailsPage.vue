<template>
  <q-page padding>

    <div v-if="!isItemDetailsLoading && item">
      

      <h1 class="text-h4 text-weight-bold q-my-none">
        {{ item.part.name }} (Cód. {{ item.item_identifier }})
      </h1>
      <div class="text-subtitle1 text-grey">
        ID Global: #{{ item.id }} | 
        <a href="#" @click.prevent="openPartHistory" class="text-primary">
          Ver template de peça
        </a>
      </div>


      <div class="row q-col-gutter-md q-my-md">
        <div class="col-12 col-sm-6 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Status Atual</div>
              <div class="text-h6 text-weight-bold">
                <q-chip :color="statusColor(item.status)" text-color="white" square>
                  {{ item.status }}
                </q-chip>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Custo de Aquisição</div>
              <div class="text-h6 text-weight-bold">
                {{ formatCurrency(item.part.value) }}
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Data de Entrada</div>
              <div class="text-h6 text-weight-bold">
                {{ formatDate(item.created_at) }}
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey">Veículo Atual</div>
              <div class="text-h6 text-weight-bold">
                <router-link v-if="item.status === 'Em Uso' && item.installed_on_vehicle_id" :to="{ name: 'vehicle-details', params: { id: item.installed_on_vehicle_id } }">
                  Ver Veículo
                </router-link>
                <span v-else class="text-grey-7">N/A</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>


      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6">Linha do Tempo do Item</div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <q-timeline color="secondary" v-if="sortedTransactions.length > 0" class="q-pa-md">
            
            <q-timeline-entry
              v-for="tx in sortedTransactions"
              :key="tx.id"
              :title="tx.transaction_type"
              :subtitle="`${formatDate(tx.timestamp, true)} - por ${tx.user?.full_name || 'Sistema'}`"
              :icon="getIconForType(tx.transaction_type)"
              :color="getColorForType(tx.transaction_type)"
            >
              <div>
                <p v-if="tx.notes" class="q-my-none"><strong>Notas:</strong> {{ tx.notes }}</p>
                <p v-if="tx.related_vehicle" class="q-my-none">
                  <strong>Veículo:</strong> 
                  <router-link :to="{ name: 'vehicle-details', params: { id: tx.related_vehicle.id } }">
                    {{ tx.related_vehicle.brand }} {{ tx.related_vehicle.model }} ({{ tx.related_vehicle.license_plate || tx.related_vehicle.identifier }})
                  </router-link>
                </p>
              </div>
            </q-timeline-entry>

          </q-timeline>
          <div v-else class="text-center text-grey q-pa-md">
            Nenhuma transação encontrada para este item.
          </div>
        </q-card-section>
      </q-card>
    </div>
    

    <div v-else>
      <q-skeleton type="text" class="text-h4" width="300px" />
      <q-skeleton type="text" class="text-subtitle1" width="200px" />
      <div class="row q-col-gutter-md q-my-md">
        <q-skeleton v-for="n in 4" :key="n" height="90px" class="col-12 col-sm-6 col-md-3" />
      </div>
      <q-skeleton type="rect" height="300px" />
    </div>


    <PartHistoryDialog v-model="isPartHistoryDialogOpen" :part="item ? item.part : null" />

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { usePartStore } from 'stores/part-store';
import { storeToRefs } from 'pinia';
import { format } from 'date-fns';
import type { TransactionType } from 'src/models/inventory-transaction-models';
import type { InventoryItemStatus } from 'src/models/inventory-item-models';
import PartHistoryDialog from 'components/PartHistoryDialog.vue';

const route = useRoute();
const partStore = usePartStore();

const { selectedItemDetails: item, isItemDetailsLoading } = storeToRefs(partStore);

const itemId = Number(route.params.id);
const isPartHistoryDialogOpen = ref(false);

onMounted(async () => {
  await partStore.fetchItemDetails(itemId);
});

const sortedTransactions = computed(() => {
  if (!item.value?.transactions) return [];

  return [...item.value.transactions].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
});



function openPartHistory() {
  if (!item.value) return;

  void partStore.fetchHistory(item.value.part_id);
  isPartHistoryDialogOpen.value = true;
}

function formatDate(dateStr: string, withTime = false): string {
  try {
    const formatStr = withTime ? 'dd/MM/yyyy HH:mm' : 'dd/MM/yyyy';
    return format(new Date(dateStr), formatStr);
  } catch {
    return 'Data inválida';
  }
}

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function statusColor(status: InventoryItemStatus): string {
  const map: Record<InventoryItemStatus, string> = {
    'Disponível': 'positive',
    'Em Uso': 'info',
    'Fim de Vida': 'negative'
  };
  return map[status] || 'grey';
}

function getIconForType(type: TransactionType): string {
  const iconMap: Record<string, string> = {
    'Entrada': 'add_shopping_cart',
    'Instalação': 'build',
    'Saída para Uso': 'build',
    'Fim de Vida': 'delete_forever',
    'Retorno': 'undo',
    'Ajuste Inicial': 'add_shopping_cart',
    'Ajuste Manual': 'edit'
  };
  return iconMap[type] || 'history';
}

function getColorForType(type: TransactionType): string {
  const colorMap: Record<string, string> = {
    'Entrada': 'positive',
    'Instalação': 'info',
    'Saída para Uso': 'info',
    'Fim de Vida': 'negative',
    'Retorno': 'warning',
    'Ajuste Inicial': 'positive',
    'Ajuste Manual': 'grey'
  };
  return colorMap[type] || 'grey';
}
</script>
