<template>
  <q-page padding>
    <h1 class="text-h4 text-weight-bold q-my-md">Rastreabilidade de Itens</h1>
    <div class="text-subtitle1 text-grey-7 q-mb-md">
      Pesquise e audite todos os itens individuais do seu inventário.
    </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section class="row q-gutter-md items-center">
        <q-input
          v-model="filters.search"
          label="Buscar por nome da peça..."
          dense outlined
          class="col-12 col-sm-4"
          style="min-width: 200px;"
          clearable
          @keyup.enter="refreshTable"
        />
        <q-select
          v-model="filters.status"
          label="Status do Item"
          :options="statusOptions"
          emit-value map-options
          dense outlined
          class="col-12 col-sm-3"
          style="min-width: 180px;"
          clearable
        />
        <q-btn label="Buscar" color="primary" unelevated @click="refreshTable" />
        <q-btn label="Limpar" flat @click="resetFilters" />
      </q-card-section>
    </q-card>

    <q-card flat bordered>
      <q-table
        :rows="partStore.masterItemList"
        :columns="columns"
        row-key="id"
        :loading="partStore.isMasterListLoading"
        no-data-label="Nenhum item encontrado."
        flat
        :rows-per-page-options="[10, 20, 50]"
        v-model:pagination="pagination"
        @request="onTableRequest"
        :rows-number="pagination.rowsNumber"
        binary-state-sort
      >
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn
              label="Ver Detalhes"
              color="primary"
              flat dense
              :to="{ name: 'item-details', params: { id: props.row.id } }"
              title="Ver linha do tempo"
            />
          </q-td>
        </template>

        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-chip :color="statusColor(props.value)" text-color="white" square dense>
              {{ props.value }}
            </q-chip>
          </q-td>
        </template>
        
        <template v-slot:body-cell-vehicle="props">
          <q-td :props="props">
            <router-link v-if="props.value" :to="{ name: 'vehicle-details', params: { id: props.value.id } }" class="text-primary" style="text-decoration: none;">
              {{ props.value.brand }} {{ props.value.model }} ({{ props.value.license_plate || props.value.identifier }})
            </router-link>
            <span v-else class="text-grey">N/A</span>
          </q-td>
        </template>

      </q-table>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { usePartStore } from 'stores/part-store';
import { InventoryItemStatus } from 'src/models/inventory-item-models'; // <-- ADICIONE ESTA IMPORTAÇÃO
import type { QTableProps } from 'quasar';


const partStore = usePartStore();

// Filtros
const filters = ref({
  search: null as string | null,
  status: null as InventoryItemStatus | null,
  partId: null as number | null,
  vehicleId: null as number | null
});

const statusOptions: { label: string, value: InventoryItemStatus }[] = [
  { label: 'Disponível', value: InventoryItemStatus.DISPONIVEL },
  { label: 'Em Uso', value: InventoryItemStatus.EM_USO },
  { label: 'Fim de Vida', value: InventoryItemStatus.FIM_DE_VIDA },
];

// Paginação (controlada pelo servidor)
const pagination = ref({
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0, // Total de itens (virá da API)
  sortBy: 'part_id', // Ordenação padrão
  descending: false,
});

// Colunas da Tabela
const columns: QTableProps['columns'] = [
  { name: 'item_identifier', label: 'Cód. Item', field: 'item_identifier', align: 'left', sortable: true },
  { name: 'part_name', label: 'Nome da Peça', field: (row) => row.part.name, align: 'left', sortable: true },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'vehicle', label: 'Veículo Instalado', field: 'installed_on_vehicle', align: 'left', sortable: false },
  { name: 'created_at', label: 'Data de Entrada', field: 'created_at', align: 'left', sortable: true, format: (val: string) => new Date(val).toLocaleDateString() },
  { name: 'actions', label: 'Ações', field: 'id', align: 'center' },
];

// Função para carregar os dados
async function fetchTableData() {
  await partStore.fetchMasterItems({
    page: pagination.value.page,
    rowsPerPage: pagination.value.rowsPerPage,
    status: filters.value.status,
    partId: filters.value.partId,
    vehicleId: filters.value.vehicleId,
    search: filters.value.search,
    // TODO: Adicionar ordenação (sortBy, descending) se o backend suportar
  });
  // Atualiza o total da paginação com o valor da store
  pagination.value.rowsNumber = partStore.masterListTotal;
}

// Chamado quando a paginação/ordenação da tabela muda
const onTableRequest: QTableProps['onRequest'] = (props) => {
  pagination.value.page = props.pagination.page;
  pagination.value.rowsPerPage = props.pagination.rowsPerPage;
  pagination.value.sortBy = props.pagination.sortBy;
  pagination.value.descending = props.pagination.descending;
  void fetchTableData();
};

// Chamado pelos botões de filtro
function refreshTable() {
  pagination.value.page = 1; // Reseta para a primeira página
  void fetchTableData();
}

function resetFilters() {
  filters.value = { search: null, status: null, partId: null, vehicleId: null };
  refreshTable();
}

// Observa mudanças nos filtros e atualiza a tabela
watch(filters, refreshTable, { deep: true });

// Carregamento inicial
onMounted(() => {
  void fetchTableData();
});

// Função utilitária para cor do status
function statusColor(status: InventoryItemStatus): string {
  const map: Record<InventoryItemStatus, string> = {
    'Disponível': 'positive',
    'Em Uso': 'info',
    'Fim de Vida': 'negative'
  };
  return map[status] || 'grey';
}
</script>