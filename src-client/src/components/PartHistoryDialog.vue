<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)">
    <q-card style="width: 800px; max-width: 90vw;" v-if="part">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Histórico: {{ part.name }}</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section>
        <q-table
          :rows="displayedHistory"
          :columns="historyColumns"
          row-key="id"
          :loading="partStore.isHistoryLoading"
          no-data-label="Nenhuma movimentação encontrada para este item."
          flat bordered dense
          :hide-bottom="isDemo && partStore.selectedPartHistory.length > demoLimit"
        >
          <template v-slot:body-cell-item_code="props">
            <q-td :props="props">
              <q-chip v-if="props.value" dense square label-color="" color="">
                #{{ props.value }}
              </q-chip>
              <span v-else>N/A</span>
            </q-td>
          </template>
        </q-table>

        <div v-if="isDemo && partStore.selectedPartHistory.length > demoLimit" class=" q-pa-md text-center ">
          <div class="q-mb-xs">
            <q-icon name="lock" size="sm" />
            <span class="text-weight-bold q-ml-sm">Histórico Antigo Bloqueado</span>
          </div>
          <div class="text-caption q-mb-sm">
            O plano Demo exibe apenas as últimas {{ demoLimit }} movimentações. 
            Existem mais {{ partStore.selectedPartHistory.length - demoLimit }} registros ocultos.
          </div>
          <q-btn 
            outline 
            color="primary" 
            label="Desbloquear Auditoria Completa" 
            size="sm" 
            icon-right="upgrade"
            @click="showUpgradeInfo"
          />
        </div>

      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuasar } from 'quasar';
import { usePartStore } from 'stores/part-store';
import { useAuthStore } from 'stores/auth-store'; // Importar AuthStore
import type { Part } from 'src/models/part-models';
import type { QTableProps } from 'quasar';
import { format } from 'date-fns';

defineProps<{ modelValue: boolean, part: Part | null }>();
const emit = defineEmits(['update:modelValue']);

const $q = useQuasar();
const partStore = usePartStore();
const authStore = useAuthStore(); // Instanciar

// --- LÓGICA DEMO ---
const isDemo = computed(() => authStore.user?.role === 'cliente_demo');
const demoLimit = 5; // Limite de linhas para mostrar

const displayedHistory = computed(() => {
  if (!isDemo.value) return partStore.selectedPartHistory;
  // Se for Demo, corta o array
  return partStore.selectedPartHistory.slice(0, demoLimit);
});

function showUpgradeInfo() {
  $q.dialog({
    title: 'Auditoria Profissional',
    message: 'No plano PRO, você tem acesso vitalício a todo o histórico de movimentação de cada peça, essencial para auditorias e controle de perdas.',
    ok: { label: 'Entendido', color: 'primary' }
  });
}
// -------------------

const historyColumns: QTableProps['columns'] = [
  { 
    name: 'timestamp', 
    label: 'Data', 
    field: 'timestamp', 
    sortable: true, 
    align: 'left', 
    format: (val) => format(new Date(val), 'dd/MM/yyyy HH:mm') 
  },
  { 
    name: 'transaction_type', 
    label: 'Tipo', 
    field: 'transaction_type', 
    sortable: true, 
    align: 'left' 
  },
  { 
    name: 'item_code', 
    label: 'Item (Cód.)', 
    field: (row) => row.item?.id, 
    align: 'center' 
  }, 
  { 
    name: 'user', 
    label: 'Usuário', 
    field: (row) => row.user?.full_name || 'Sistema', 
    align: 'left' 
  },
  { 
    name: 'notes', 
    label: 'Notas', 
    field: 'notes', 
    align: 'left', 
    style: 'white-space: pre-wrap;' 
  },
];
</script>

<style scoped>
.border-top-dashed {
  border-top: 2px dashed #e0e0e0;
}
</style>