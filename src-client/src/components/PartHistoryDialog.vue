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
          <template v-slot:body-cell-item_code="props">
            <q-td :props="props">
              <q-chip v-if="props.value" dense square label-color="white" color="grey-8">
                #{{ props.value }}
              </q-chip>
              <span v-else>N/A</span>
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