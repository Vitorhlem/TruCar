<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h5 text-weight-bold q-my-none">Log de Auditoria</h1>
        <div class="text-caption text-grey-7">Rastreabilidade de ações no sistema</div>
      </div>
      <q-btn icon="refresh" flat round @click="loadData" :loading="store.isLoading" />
    </div>

    <q-card flat bordered>
      <q-table
        :rows="store.logs"
        :columns="columns"
        row-key="id"
        :loading="store.isLoading"
        :pagination="{ rowsPerPage: 15 }"
      >
        <template v-slot:body-cell-action="props">
          <q-td :props="props">
            <q-chip 
              dense 
              :color="getActionColor(props.value)" 
              text-color="white" 
              size="sm"
              class="text-weight-bold"
            >
              {{ translateAction(props.value) }}
            </q-chip>
          </q-td>
        </template>

        <template v-slot:body-cell-details="props">
          <q-td :props="props">
            <div class="text-caption text-grey-8 truncate-text" style="max-width: 300px;">
               {{ formatDetails(props.row) }}
            </div>
          </q-td>
        </template>
      </q-table>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
// Importa o tipo para usar na função formatDetails
import { useAuditLogStore, type AuditLog } from 'stores/audit-log-store';
// Importa o tipo de coluna do Quasar
import { date, type QTableColumn } from 'quasar';

const store = useAuditLogStore();

// CORREÇÃO: Tipagem explícita das colunas para evitar erro de alinhamento
const columns: QTableColumn[] = [
  { 
    name: 'created_at', 
    label: 'Data/Hora', 
    field: 'created_at', 
    align: 'left', 
    sortable: true, 
    format: (val: string) => date.formatDate(val, 'DD/MM/YYYY HH:mm') 
  },
  { name: 'user_name', label: 'Usuário', field: 'user_name', align: 'left', sortable: true },
  { name: 'action', label: 'Ação', field: 'action', align: 'center', sortable: true },
  { name: 'resource_type', label: 'Recurso', field: 'resource_type', align: 'left', sortable: true },
  { name: 'details', label: 'Detalhes', field: 'details', align: 'left' },
];

function getActionColor(action: string) {
  if (action.includes('CREATE')) return 'positive';
  if (action.includes('UPDATE')) return 'warning';
  if (action.includes('DELETE')) return 'negative';
  return 'primary';
}

function translateAction(action: string) {
  const map: Record<string, string> = {
    'CREATE': 'CRIAÇÃO',
    'UPDATE': 'EDIÇÃO',
    'DELETE': 'EXCLUSÃO',
    'LOGIN': 'ACESSO'
  };
  return map[action] || action;
}

// CORREÇÃO: Tipagem do parâmetro row
function formatDetails(row: AuditLog) {
  if (row.resource_id) return `ID: ${row.resource_id}`;
  return '-';
}

function loadData() {
  // CORREÇÃO: void para tratar a promise flutuante
  void store.fetchLogs();
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.truncate-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>