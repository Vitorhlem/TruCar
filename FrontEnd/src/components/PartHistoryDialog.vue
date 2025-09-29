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
          :rows="partStore.selectedPartHistory"
          :columns="historyColumns"
          row-key="id"
          :loading="partStore.isHistoryLoading"
          no-data-label="Nenhuma movimentação encontrada para este item."
          flat bordered dense
        >
          <template v-slot:body-cell-quantity_change="props">
            <q-td :props="props">
              <q-chip
                :color="props.value > 0 ? 'positive' : 'negative'"
                text-color="white"
                :label="`${props.value > 0 ? '+' : ''}${props.value}`"
                square
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { usePartStore } from 'stores/part-store';
import type { Part } from 'src/models/part-models';
import type { QTableProps } from 'quasar';
import { format } from 'date-fns';

defineProps<{ modelValue: boolean, part: Part | null }>();
const emit = defineEmits(['update:modelValue']);

const partStore = usePartStore();

const historyColumns: QTableProps['columns'] = [
  { name: 'timestamp', label: 'Data', field: 'timestamp', sortable: true, align: 'left', format: (val) => format(new Date(val), 'dd/MM/yyyy HH:mm') },
  { name: 'transaction_type', label: 'Tipo', field: 'transaction_type', sortable: true, align: 'left' },
  { name: 'quantity_change', label: 'Alteração', field: 'quantity_change', align: 'center' },
  { name: 'stock_after_transaction', label: 'Estoque Final', field: 'stock_after_transaction', align: 'center' },
  { name: 'user', label: 'Usuário', field: (row) => row.user?.full_name || 'Sistema', align: 'left' },
  { name: 'notes', label: 'Notas', field: 'notes', align: 'left', style: 'white-space: pre-wrap;' },
];
</script>