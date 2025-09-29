<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">Inventário</h1>
        <div class="text-subtitle1 text-grey-7">Controle o seu estoque de peças, fluídos e consumíveis.</div>
      </div>
      <q-btn color="primary" icon="add" label="Adicionar Novo Item" unelevated @click="openDialog()" />
    </div>

    <q-card flat bordered>
       <q-table
        :rows="partStore.parts"
        :columns="columns"
        row-key="id"
        :loading="partStore.isLoading"
        no-data-label="Nenhum item encontrado no inventário."
        flat
        :rows-per-page-options="[10, 20, 50]"
      >
        <template v-slot:top>
          <q-input dense debounce="300" v-model="searchQuery" placeholder="Procurar por nome, marca ou código..." style="width: 300px;">
            <template v-slot:append> <q-icon name="search" /> </template>
          </q-input>
        </template>
        
        <template v-slot:body-cell-photo_url="props">
          <q-td :props="props">
            <q-avatar rounded size="60px" font-size="32px" color="grey-3" text-color="grey-6" :icon="getCategoryIcon(props.row.category)">
              <img v-if="props.value" :src="`http://localhost:8000${props.value}`" alt="Foto do item">
            </q-avatar>
          </q-td>
        </template>

        <template v-slot:body-cell-stock="props">
          <q-td :props="props">
            <q-chip :color="getStockColor(props.row.stock, props.row.min_stock)" text-color="white" class="text-weight-bold" square>
              {{ props.row.stock }} / {{ props.row.min_stock }}
            </q-chip>
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn-dropdown unelevated color="primary" label="Ações" dense>
              <q-list dense>
                <q-item clickable v-close-popup @click="openStockDialog(props.row)">
                  <q-item-section avatar><q-icon name="sync_alt" /></q-item-section>
                  <q-item-section>Gerenciar Estoque</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="openHistoryDialog(props.row)">
                  <q-item-section avatar><q-icon name="history" /></q-item-section>
                  <q-item-section>Ver Histórico</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="openDialog(props.row)">
                  <q-item-section avatar><q-icon name="edit" /></q-item-section>
                  <q-item-section>Editar Item</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="confirmDelete(props.row)">
                  <q-item-section avatar><q-icon name="delete" color="negative" /></q-item-section>
                  <q-item-section><q-item-label class="text-negative">Excluir Item</q-item-label></q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="isDialogOpen" >
      <q-card style="width: 700px; max-width: 90vw;">
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">{{ isEditing ? 'Editar Item' : 'Adicionar Novo Item' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="resetForm" />
          </q-card-section>

          <q-card-section class="row q-col-gutter-md">
            <div class="col-12 col-md-8 q-gutter-y-md">
              <q-input outlined v-model="formData.name" label="Nome do Item *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-select outlined v-model="formData.category" :options="categoryOptions" label="Categoria *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-input outlined v-model="formData.part_number" label="Código / Part Number" />
              <q-input outlined v-model="formData.brand" label="Marca" />
              <q-input outlined v-model="formData.location" label="Localização (Ex: Prateleira A-03)" />
            </div>
            <div class="col-12 col-md-4">
              <q-file v-model="photoFile" label="Foto do Item" outlined clearable accept=".jpg, .jpeg, .png, .webp, .avif">
                <template v-slot:prepend><q-icon name="photo_camera" /></template>
              </q-file>
              <q-img v-if="!photoFile && formData.photo_url" :src="`http://localhost:8000${formData.photo_url}`" class="q-mt-md rounded-borders" style="height: 120px; max-width: 100%" fit="contain" />
            </div>
            <div class="col-12 col-sm-6">
              <q-input outlined v-model.number="formData.stock" type="number" :label="isEditing ? 'Estoque Inicial (só na criação)' : 'Estoque Inicial *'" :disable="isEditing" :hint="isEditing ? 'Use as Ações para alterar o estoque' : ''" :rules="[val => val >= 0 || 'Valor inválido']" />
            </div>
            <div class="col-12 col-sm-6">
              <q-input outlined v-model.number="formData.min_stock" type="number" label="Estoque Mínimo *" :rules="[val => val >= 0 || 'Valor inválido']" />
            </div>
            <div class="col-12">
               <q-input outlined v-model="formData.notes" type="textarea" label="Notas (Opcional)" autogrow />
            </div>
          </q-card-section>
          
          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" flat @click="resetForm" v-close-popup />
            <q-btn :label="isEditing ? 'Salvar Alterações' : 'Adicionar Item'" type="submit" color="primary" unelevated :loading="partStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <ManageStockDialog v-model="isStockDialogOpen" :part="selectedPart" />
    <PartHistoryDialog v-model="isHistoryDialogOpen" :part="selectedPart" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableProps } from 'quasar';
import { usePartStore, type PartCreatePayload } from 'stores/part-store';
import type { Part, PartCategory } from 'src/models/part-models';
// NOVOS IMPORTS DOS COMPONENTES
import ManageStockDialog from 'components/ManageStockDialog.vue';
import PartHistoryDialog from 'components/PartHistoryDialog.vue';

const $q = useQuasar();
const partStore = usePartStore();

// --- CONTROLE DOS DIÁLOGOS ---
const isDialogOpen = ref(false);
const isStockDialogOpen = ref(false);
const isHistoryDialogOpen = ref(false);
const selectedPart = ref<Part | null>(null);

const editingPart = ref<Part | null>(null);
const isEditing = computed(() => !!editingPart.value);
const searchQuery = ref('');
const photoFile = ref<File | null>(null);

const categoryOptions: PartCategory[] = ["Peça", "Fluído", "Consumível", "Outro"];

const initialFormData = {
  name: '',
  category: 'Peça' as PartCategory,
  part_number: '',
  brand: '',
  stock: 0,
  min_stock: 0,
  location: '',
  notes: '',
  photo_url: null,
};
const formData = ref<Partial<Part>>({ ...initialFormData });

const columns: QTableProps['columns'] = [
  { name: 'photo_url', label: 'Foto', field: 'photo_url', align: 'center' },
  { name: 'name', label: 'Item', field: 'name', align: 'left', sortable: true },
  { name: 'category', label: 'Categoria', field: 'category', align: 'left', sortable: true },
  { name: 'part_number', label: 'Código', field: 'part_number', align: 'left' },
  { name: 'stock', label: 'Estoque', field: 'stock', align: 'center', sortable: true },
  { name: 'location', label: 'Localização', field: 'location', align: 'left' },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'center' },
];

watch(searchQuery, () => {
  void partStore.fetchParts(searchQuery.value);
});

function getStockColor(current: number, min: number): string {
  if (current <= 0) return 'negative';
  if (current <= min) return 'warning';
  return 'positive';
}

function getCategoryIcon(category: PartCategory): string {
  const iconMap: Record<PartCategory, string> = {
    'Peça': 'settings',
    'Fluído': 'opacity',
    'Consumível': 'inbox',
    'Outro': 'category',
  };
  return iconMap[category] || 'inventory_2';
}

function resetForm() {
  editingPart.value = null;
  formData.value = { ...initialFormData };
  photoFile.value = null;
}

function openDialog(part: Part | null = null) {
  if (part) {
    editingPart.value = { ...part };
    formData.value = { ...part };
  } else {
    resetForm();
  }
  isDialogOpen.value = true;
}

function openStockDialog(part: Part) {
  selectedPart.value = part;
  isStockDialogOpen.value = true;
}

function openHistoryDialog(part: Part) {
  selectedPart.value = part;
  void partStore.fetchHistory(part.id);
  isHistoryDialogOpen.value = true;
}

async function handleSubmit() {
  const payload: PartCreatePayload = { ...formData.value };
  if (photoFile.value) {
    payload.photo_file = photoFile.value;
  }
  
  const success = isEditing.value && editingPart.value
    ? await partStore.updatePart(editingPart.value.id, payload)
    : await partStore.createPart(payload);
  
  if (success) {
    isDialogOpen.value = false;
    resetForm();
  }
}

function confirmDelete(part: Part) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja remover o item "${part.name}"? Todo o seu histórico de movimentações será perdido.`,
    cancel: true,
    persistent: false,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
  }).onOk(() => {
    void partStore.deletePart(part.id);
  });
}

onMounted(() => {
  void partStore.fetchParts();
});
</script>