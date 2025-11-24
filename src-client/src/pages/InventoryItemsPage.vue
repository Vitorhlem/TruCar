<template>
  <q-page class="q-pa-md q-pa-lg-xl">
    
    <div class="row items-center justify-between q-mb-lg">
      <div class="col-12 col-md-auto">
        <h1 class="text-h4 text-weight-bolder q-my-none text-primary flex items-center gap-sm">
          <q-icon name="qr_code_scanner" size="md" />
          Rastreabilidade de Itens
        </h1>
        <div class="text-subtitle2 text-grey-7 q-mt-xs" :class="{ 'text-grey-5': $q.dark.isActive }">
          Auditoria individual e localização de cada item do estoque
        </div>
      </div>
      <div class="col-12 col-md-auto q-mt-md q-md-mt-none">
         <q-btn 
            outline 
            color="primary" 
            icon="file_download" 
            label="Exportar Relatório" 
            @click="exportTable"
            :disable="isDemo"
         />
      </div>
    </div>

    <q-card flat bordered class="q-mb-lg relative-position overflow-hidden">
      
      <div 
        v-if="isDemo" 
        class="absolute-full z-top flex flex-center column" 
        :style="$q.dark.isActive ? 'background: rgba(0,0,0,0.8)' : 'background: rgba(255,255,255,0.8)'"
        style="cursor: not-allowed; backdrop-filter: blur(3px);"
      >
        <q-icon name="lock_person" size="4em" color="primary" class="q-mb-sm" />
        <div class="text-h6 text-weight-bold">Rastreabilidade Avançada Bloqueada</div>
        <div class="text-caption q-mb-md text-center" style="max-width: 400px">
            O Plano Demo oferece uma visão limitada. Para auditar status, filtrar por serial e exportar relatórios, faça o upgrade para o <strong>Plano PRO</strong>.
        </div>
        <q-btn 
          color="primary" 
          label="Liberar Acesso Total"
          unelevated
          icon="rocket_launch"
          @click="showFilterUpgradeDialog"
          class="shadow-3"
        />
      </div>

      <div class="column" :class="{ 'blur-content': isDemo }">
          <div class="q-px-md q-pt-md border-bottom">
              <q-tabs
                v-model="filters.status"
                align="left"
                active-color="primary"
                indicator-color="primary"
                class="text-grey-7"
                :class="$q.dark.isActive ? 'text-grey-5' : ''"
                dense
                mobile-arrows
                outside-arrows
                @update:model-value="refreshTable"
              >
                <q-tab name="" label="Todos" />
                <q-tab name="Disponível" label="Em Estoque" icon="inventory_2" />
                <q-tab name="Em Uso" label="Em Uso" icon="directions_car" />
                <q-tab name="Fim de Vida" label="Descartados" icon="delete" />
              </q-tabs>
          </div>
          <q-separator />

          <q-card-section class="row q-col-gutter-md items-center q-py-md" :class="$q.dark.isActive ? '' : ''">
            <div class="col-grow">
              <q-input
                v-model="filters.search"
                label="Buscar Item"
                placeholder="Nome da peça, código identificador, serial ou marca..."
                dense outlined
                clearable
                :disable="isDemo" 
                @keyup.enter="refreshTable"
                :bg-color="$q.dark.isActive ? '' : 'white'"
              >
                <template v-slot:prepend><q-icon name="search" /></template>
              </q-input>
            </div>
            
            <div class="col-auto">
              <q-btn label="Atualizar" icon="refresh" flat color="primary" @click="refreshTable" :disable="isDemo" />
            </div>
          </q-card-section>
      </div>
    </q-card>

    <q-card flat bordered>
      <q-table
        :rows="partStore.masterItemList"
        :columns="columns"
        row-key="id"
        :loading="partStore.isMasterListLoading"
        flat
        :rows-per-page-options="[10, 25, 50]"
        v-model:pagination="pagination"
        @request="onTableRequest"
        :rows-number="pagination.rowsNumber"
        binary-state-sort
        :grid="$q.screen.lt.md"
        :card-class="$q.dark.isActive ? '' : 'text-grey-9'"
      >
        
        <template v-slot:header="props">
            <q-tr :props="props" :class="$q.dark.isActive ? '' : 'bg-grey-1'">
                <q-th v-for="col in props.cols" :key="col.name" :props="props" class="text-weight-bold text-uppercase text-caption text-grey-7">
                    {{ col.label }}
                </q-th>
            </q-tr>
        </template>

        <template v-slot:body-cell-item_identifier="props">
            <q-td :props="props">
                <div class="flex items-center no-wrap">
                    <q-icon name="qr_code" size="sm" class="q-mr-sm text-grey-6" />
                    <span class="text-weight-bold font-monospace">{{ props.value }}</span>
                </div>
            </q-td>
        </template>

        <template v-slot:body-cell-part_name="props">
          <q-td :props="props">
            <div class="text-weight-medium ellipsis" style="max-width: 200px" :title="props.row.part.name">{{ props.row.part.name }}</div>
            <div class="text-caption text-grey row items-center q-gutter-x-xs no-wrap">
               <span class="ellipsis" style="max-width: 100px">{{ props.row.part.brand || 'Genérico' }}</span>
               
               <q-badge v-if="props.row.part.serial_number" color="grey-3" text-color="grey-9" class="q-px-xs ellipsis" style="max-width: 120px">
                 SN: {{ props.row.part.serial_number }}
               </q-badge>
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-chip 
                :color="statusColor(props.value)" 
                text-color="white"
                size="sm"
                class="text-weight-bold"
                square
            >
              {{ props.value }}
            </q-chip>
          </q-td>
        </template>
        
        <template v-slot:body-cell-vehicle="props">
          <q-td :props="props">
            <router-link 
                v-if="props.value" 
                :to="{ name: 'vehicle-details', params: { id: props.value.id } }" 
                class="link-hover flex items-center text-grey-9 no-wrap" 
                :class="$q.dark.isActive ? 'text-white' : ''"
                style="text-decoration: none; max-width: 200px;"
            >
              <q-avatar icon="directions_car" size="sm" color="primary" text-color="white" class="q-mr-sm" font-size="16px" />
              <div class="ellipsis">
                  <div class="text-weight-medium ellipsis">{{ props.value.model }}</div>
                  <div class="text-caption text-grey ellipsis">{{ props.value.license_plate || props.value.identifier }}</div>
              </div>
            </router-link>
            <span v-else class="text-grey-5 text-italic flex items-center no-wrap">
                <q-icon name="warehouse" class="q-mr-xs" /> Estoque
            </span>
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn
              label="Rastrear"
              icon-right="arrow_forward"
              color="primary"
              flat
              dense
              size="sm"
              :to="{ name: 'item-details', params: { id: props.row.id } }"
            >
                <q-tooltip>Ver histórico completo</q-tooltip>
            </q-btn>
          </q-td>
        </template>

        <template v-slot:item="props">
            <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4">
              <q-card flat bordered class="full-height">
                <q-card-section class="row justify-between items-start">
                    <div class="col">
                        <div class="text-caption text-grey">ID: {{ props.row.item_identifier }}</div>
                        <div class="text-subtitle1 text-weight-bold ellipsis">{{ props.row.part.name }}</div>
                        <div class="text-caption text-grey-7">{{ props.row.part.brand }}</div>
                    </div>
                    <q-badge :color="statusColor(props.row.status)" rounded class="q-py-xs col-auto">{{ props.row.status }}</q-badge>
                </q-card-section>
                <q-separator />
                <q-card-section>
                    <div v-if="props.row.installed_on_vehicle" class="row items-center no-wrap">
                        <q-icon name="directions_car" class="q-mr-sm" color="grey-6" />
                        <div class="ellipsis">
                            <div class="text-weight-medium ellipsis">{{ props.row.installed_on_vehicle.model }}</div>
                            <div class="text-caption ellipsis">{{ props.row.installed_on_vehicle.license_plate }}</div>
                        </div>
                    </div>
                    <div v-else class="text-grey-6 text-italic row items-center">
                        <q-icon name="warehouse" class="q-mr-sm" /> Estoque
                    </div>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Detalhes" color="primary" :to="{ name: 'item-details', params: { id: props.row.id } }" />
                </q-card-actions>
              </q-card>
            </div>
        </template>

        <template v-slot:no-data>
            <div class="full-width column flex-center q-pa-xl text-grey-5">
                <q-icon name="search_off" size="4em" class="q-mb-md" />
                <div class="text-h6">Nenhum item encontrado</div>
                <div class="text-caption">Tente ajustar os filtros ou adicionar novos itens no inventário.</div>
                <q-btn label="Limpar Filtros" color="primary" outline class="q-mt-md" @click="resetFilters" v-if="filters.search || filters.status" />
            </div>
        </template>

      </q-table>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useQuasar, exportFile } from 'quasar';
import { usePartStore } from 'stores/part-store';
import { useAuthStore } from 'stores/auth-store';
import { InventoryItemStatus } from 'src/models/inventory-item-models';
import type { QTableProps } from 'quasar';

const $q = useQuasar();
const partStore = usePartStore();
const authStore = useAuthStore();

// --- LÓGICA DEMO ---
const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

function showFilterUpgradeDialog() {
  $q.dialog({
    title: 'Busca Avançada Bloqueada',
    message: 'No plano Demo, a busca e auditoria detalhada são limitadas. Desbloqueie o Plano PRO para rastreabilidade total.',
    ok: { label: 'Ver Planos', color: 'primary', unelevated: true },
    cancel: true
  });
}
// -------------------

// Filtros
const filters = ref({
  search: null as string | null,
  // CORREÇÃO 1: Permitir string vazia e null
  status: '' as InventoryItemStatus | '' | null,
  partId: null as number | null,
  vehicleId: null as number | null
});

const pagination = ref({
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0, 
  sortBy: 'created_at',
  descending: true,
});

const columns: QTableProps['columns'] = [
  { name: 'item_identifier', label: 'Identificador', field: 'item_identifier', align: 'left', sortable: true, style: 'width: 140px' },
  { name: 'part_name', label: 'Descrição do Item', field: (row) => row.part.name, align: 'left', sortable: true },
  { name: 'vehicle', label: 'Localização', field: 'installed_on_vehicle', align: 'left', sortable: false },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true, style: 'width: 120px' },
  { name: 'created_at', label: 'Entrada', field: 'created_at', align: 'right', sortable: true, format: (val: string) => new Date(val).toLocaleDateString(), style: 'width: 120px' },
  { name: 'actions', label: 'Auditoria', field: 'id', align: 'center', style: 'width: 100px' },
];

async function fetchTableData() {
  await partStore.fetchMasterItems({
    page: pagination.value.page,
    rowsPerPage: pagination.value.rowsPerPage,
    // CORREÇÃO 2: Converter string vazia para null antes de enviar
    status: filters.value.status || null,
    partId: filters.value.partId,
    vehicleId: filters.value.vehicleId,
    search: filters.value.search,
  });
  pagination.value.rowsNumber = partStore.masterListTotal;
}

const onTableRequest: QTableProps['onRequest'] = (props) => {
  pagination.value.page = props.pagination.page;
  pagination.value.rowsPerPage = props.pagination.rowsPerPage;
  pagination.value.sortBy = props.pagination.sortBy;
  pagination.value.descending = props.pagination.descending;
  void fetchTableData();
};

function refreshTable() {
  if (isDemo.value) return;
  pagination.value.page = 1;
  void fetchTableData();
}

function resetFilters() {
  if (isDemo.value) return;
  // CORREÇÃO 3: Resetar para string vazia
  filters.value = { search: null, status: '', partId: null, vehicleId: null };
  refreshTable();
}

function exportTable() {
    if (isDemo.value) {
        showFilterUpgradeDialog();
        return;
    }
    
    const content = [
      ['ID', 'Nome', 'Código', 'Serial', 'Status', 'Veículo'].join(';'),
      ...partStore.masterItemList.map(row => [
        row.id,
        `"${row.part.name}"`,
        row.item_identifier,
        // CORREÇÃO 4: Acesso seguro a part.serial_number
        row.part.serial_number || '',
        row.status,
        row.installed_on_vehicle ? row.installed_on_vehicle.license_plate : 'Estoque'
      ].join(';'))
    ].join('\r\n');

    const status = exportFile(
      'inventario-export.csv',
      content,
      'text/csv'
    );

    if (!status) {
      $q.notify({
        message: 'Erro ao iniciar download',
        color: 'negative',
        icon: 'warning'
      });
    }
}

watch(filters, () => {
  if (!isDemo.value) refreshTable();
}, { deep: true });

onMounted(() => {
  void fetchTableData();
});

function statusColor(status: InventoryItemStatus): string {
  const map: Record<InventoryItemStatus, string> = {
    [InventoryItemStatus.DISPONIVEL]: 'positive',
    [InventoryItemStatus.EM_USO]: 'info',
    [InventoryItemStatus.FIM_DE_VIDA]: 'blue-grey' 
  };
  return map[status] || 'grey';
}
</script>

<style scoped>
.blur-content {
  filter: blur(4px);
  pointer-events: none;
  user-select: none;
  opacity: 0.5;
}

.border-bottom {
    border-bottom: 1px solid rgba(0,0,0,0.12);
}
.body--dark .border-bottom {
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.font-monospace {
    font-family: 'Roboto Mono', monospace;
}

.link-hover:hover {
    text-decoration: underline !important;
    opacity: 0.8;
}
</style>