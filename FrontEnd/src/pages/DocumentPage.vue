<template>
  <q-page padding>
    <div class="q-pa-md">
      <!-- Cabeçalho da Página -->
      <div class="flex items-center justify-between q-mb-md">
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">Gestão de Documentos</h1>
          <div class="text-subtitle1 text-grey-7">Centralize e controle os vencimentos de CNHs, CRLVs e mais.</div>
        </div>
        <q-btn
          color="primary"
          icon="add"
          label="Adicionar Documento"
          unelevated
          @click="openAddDialog"
        />
      </div>

      <!-- Tabela de Documentos -->
      <q-table
        :rows="documentStore.documents"
        :columns="columns"
        row-key="id"
        :loading="documentStore.isLoading"
        flat
        bordered
        card-class="dashboard-card"
        :rows-per-page-options="[10, 25, 50]"
      >
        <!-- Template para a coluna de Vencimento (com status de cor) -->
        <template v-slot:body-cell-expiry_date="props">
          <q-td :props="props">
            <q-chip
              :color="getExpiryStatusColor(props.row.expiry_date).color"
              :text-color="getExpiryStatusColor(props.row.expiry_date).textColor"
              :label="formatDate(props.row.expiry_date)"
              square
              class="text-weight-bold"
            />
          </q-td>
        </template>

        <!-- Template para a coluna de Ações -->
        <template v-slot:body-cell-actions="props">
          <q-td :props="props" class="q-gutter-sm">
            <q-btn :href="props.row.file_url" target="_blank" dense flat round color="primary" icon="visibility">
              <q-tooltip>Ver Documento</q-tooltip>
            </q-btn>
            <q-btn dense flat round color="negative" icon="delete" @click="confirmDelete(props.row)">
              <q-tooltip>Remover</q-tooltip>
            </q-btn>
          </q-td>
        </template>
      </q-table>
    </div>

    <!-- Diálogo para Adicionar Novo Documento -->
    <q-dialog v-model="isDialogOpen" >
      <q-card style="width: 600px; max-width: 90vw;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Novo Documento</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="onSubmit">
          <q-card-section class="q-gutter-md">
            <q-select
              outlined
              v-model="newDocument.document_type"
              :options="documentTypeOptions"
              label="Tipo de Documento"
              :rules="[val => !!val || 'Campo obrigatório']"
            />
            <q-select
              outlined
              v-model="ownerType"
              :options="['Veículo', 'Motorista']"
              label="Associar a"
              :rules="[val => !!val || 'Campo obrigatório']"
            />
            <q-select
              v-if="ownerType === 'Veículo'"
              outlined
              v-model="newDocument.vehicle_id"
              :options="vehicleOptions"
              label="Selecione o Veículo"
              emit-value
              map-options
              :rules="[val => !!val || 'Selecione um veículo']"
            />
            <q-select
              v-if="ownerType === 'Motorista'"
              outlined
              v-model="newDocument.driver_id"
              :options="driverOptions"
              label="Selecione o Motorista"
              emit-value
              map-options
              :rules="[val => !!val || 'Selecione um motorista']"
            />
            <q-input
              outlined
              v-model="newDocument.expiry_date"
              label="Data de Vencimento"
              mask="####-##-##"
              :rules="['date']"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="newDocument.expiry_date">
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Fechar" color="primary" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-file
              outlined
              v-model="newDocument.file"
              label="Anexar arquivo"
              accept=".pdf,.jpg,.jpeg,.png"
              :rules="[val => !!val || 'É necessário anexar um arquivo']"
            >
              <template v-slot:prepend><q-icon name="attach_file" /></template>
            </q-file>
            <q-input
              outlined
              v-model="newDocument.notes"
              label="Notas (Opcional)"
              type="textarea"
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" flat v-close-popup />
            <q-btn label="Salvar Documento" type="submit" color="primary" unelevated :loading="documentStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableProps } from 'quasar';
import { useDocumentStore, type DocumentCreatePayload } from 'stores/document-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useUserStore } from 'stores/user-store';
import type { DocumentPublic } from 'src/models/document-models';
import type { User } from 'src/models/auth-models';
import { format, parseISO, differenceInDays } from 'date-fns';

const $q = useQuasar();
const documentStore = useDocumentStore();
const vehicleStore = useVehicleStore();
const userStore = useUserStore();

// --- Lógica da Tabela ---
const columns: QTableProps['columns'] = [
  { name: 'document_type', required: true, label: 'Tipo', align: 'left', field: 'document_type', sortable: true },
  { name: 'expiry_date', label: 'Vencimento', field: 'expiry_date', align: 'center', sortable: true },
  { name: 'owner_info', label: 'Associado a', field: 'owner_info', align: 'left', sortable: true },
  { name: 'notes', label: 'Notas', field: 'notes', align: 'left', sortable: false },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right', sortable: false },
];

function formatDate(dateString: string): string {
  if (!dateString) return 'N/A';
  return format(parseISO(dateString), 'dd/MM/yyyy');
}

function getExpiryStatusColor(dateString: string): { color: string, textColor: string } {
  const daysUntilExpiry = differenceInDays(parseISO(dateString), new Date());
  if (daysUntilExpiry < 0) return { color: 'negative', textColor: 'white' };
  if (daysUntilExpiry <= 30) return { color: 'warning', textColor: 'black' };
  return { color: 'positive', textColor: 'white' };
}


// --- Lógica do Diálogo e Formulário ---
interface NewDocumentForm {
  document_type: string;
  expiry_date: string;
  notes: string;
  vehicle_id: number | undefined;
  driver_id: number | undefined;
  file: File | null;
}

const isDialogOpen = ref(false);
const ownerType = ref<'Veículo' | 'Motorista' | null>(null);

const initialNewDocumentState: NewDocumentForm = {
  document_type: '',
  expiry_date: '',
  notes: '',
  vehicle_id: undefined,
  driver_id: undefined,
  file: null,
};

const newDocument = ref<NewDocumentForm>({ ...initialNewDocumentState });

// Opções para os QSelects
const documentTypeOptions = ['CNH', 'CRLV', 'ANTT', 'ASO', 'Seguro', 'Outro'];
const vehicleOptions = computed(() => vehicleStore.vehicles.map(v => ({
  label: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`,
  value: v.id
})));

const drivers = computed(() => userStore.users.filter(u => u.role === 'driver'));
const driverOptions = computed(() => drivers.value.map((d: User) => ({
  label: d.full_name,
  value: d.id
})));


// Limpa os IDs associados quando o tipo de dono muda
watch(ownerType, () => {
  newDocument.value.vehicle_id = undefined;
  newDocument.value.driver_id = undefined;
});


function openAddDialog() {
  newDocument.value = { ...initialNewDocumentState };
  ownerType.value = null;
  isDialogOpen.value = true;
}

async function onSubmit() {
  if (!newDocument.value.file) return;

  const payload: DocumentCreatePayload = {
    document_type: newDocument.value.document_type,
    expiry_date: newDocument.value.expiry_date,
    notes: newDocument.value.notes,
    file: newDocument.value.file,
    ...(newDocument.value.vehicle_id !== undefined && { vehicle_id: newDocument.value.vehicle_id }),
    ...(newDocument.value.driver_id !== undefined && { driver_id: newDocument.value.driver_id }),
  };

  await documentStore.createDocument(payload);
  isDialogOpen.value = false;
}

function confirmDelete(document: DocumentPublic) {
  $q.dialog({
    title: 'Confirmar Remoção',
    message: `Tem a certeza de que deseja remover o documento "${document.document_type}" associado a "${document.owner_info}"? Esta ação não pode ser desfeita.`,
    cancel: true,
    persistent: false,
    ok: {
      label: 'Remover',
      color: 'negative',
      unelevated: true,
    },
  }).onOk(() => {
    void documentStore.deleteDocument(document.id);
  });
}


// --- Ciclo de Vida ---
onMounted(() => {
  void documentStore.fetchDocuments();
  void vehicleStore.fetchAllVehicles(); // Busca veículos para o formulário
  void userStore.fetchAllUsers();     // Busca motoristas para o formulário
});

</script>

<style scoped lang="scss">
.dashboard-card {
  border-radius: $generic-border-radius;
  box-shadow: none;
  border: 1px solid $grey-3;
  
  .body--dark & {
    border-color: $grey-8;
  }
}
</style>

