<template>
  <q-page padding>
    <!-- CABEÇALHO DA PÁGINA -->
    <div class="flex items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">Inventário de Peças</h1>
        <div class="text-subtitle1 text-grey-7">Controle o seu stock de peças e consumíveis.</div>
      </div>
      <q-btn
        color="primary"
        icon="add"
        label="Adicionar Nova Peça"
        unelevated
        @click="openDialog()"
      />
    </div>

    <!-- TABELA DE PEÇAS -->
    <q-card flat bordered>
       <q-table
        :rows="partStore.parts"
        :columns="columns"
        row-key="id"
        :loading="partStore.isLoading"
        no-data-label="Nenhuma peça encontrada no inventário."
        flat
        :rows-per-page-options="[10, 20, 50]"
      >
        <!-- Filtro/Busca no Topo -->
        <template v-slot:top>
          <q-input dense debounce="300" v-model="searchQuery" placeholder="Procurar por nome, marca ou código..." style="width: 300px;">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </template>
        
        <!-- Célula de Foto -->
        <template v-slot:body-cell-photo_url="props">
          <q-td :props="props">
            <q-avatar rounded size="60px" font-size="32px" color="grey-3" text-color="grey-6" icon="inventory_2">
              <img v-if="props.value" :src="`http://localhost:8000${props.value}`" alt="Foto da peça">
            </q-avatar>
          </q-td>
        </template>

        <!-- Célula de Stock com Cores -->
        <template v-slot:body-cell-stock="props">
          <q-td :props="props">
            <q-chip
              :color="getStockColor(props.row.stock, props.row.min_stock)"
              text-color="white"
              class="text-weight-bold"
              square
            >
              {{ props.row.stock }} / {{ props.row.min_stock }}
            </q-chip>
          </q-td>
        </template>

        <!-- Célula de Ações -->
        <template v-slot:body-cell-actions="props">
          <q-td :props="props" class="q-gutter-x-sm">
            <q-btn flat round dense icon="edit" color="primary" @click="openDialog(props.row)">
              <q-tooltip>Editar</q-tooltip>
            </q-btn>
            <q-btn flat round dense icon="delete" color="negative" @click="confirmDelete(props.row)">
              <q-tooltip>Remover</q-tooltip>
            </q-btn>
          </q-td>
        </template>

      </q-table>
    </q-card>

    <!-- DIÁLOGO DE ADICIONAR/EDITAR PEÇA -->
    <q-dialog v-model="isDialogOpen" persistent>
      <q-card style="width: 700px; max-width: 90vw;">
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">{{ isEditing ? 'Editar Peça' : 'Adicionar Nova Peça' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="resetForm" />
          </q-card-section>

          <q-card-section class="row q-col-gutter-md">
            <div class="col-12 col-md-8 q-gutter-y-md">
              <q-input outlined v-model="formData.name" label="Nome da Peça *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-input outlined v-model="formData.part_number" label="Código / Part Number" />
              <q-input outlined v-model="formData.brand" label="Marca" />
              <q-input outlined v-model="formData.location" label="Localização no Stock (Ex: Prateleira A-03)" />
            </div>
            <div class="col-12 col-md-4">
              <q-file
                v-model="photoFile"
                label="Foto da Peça"
                outlined
                clearable
                accept=".jpg, .jpeg, .png, .webp, .avif"
              >
                <template v-slot:prepend><q-icon name="photo_camera" /></template>
              </q-file>
              <q-img
                v-if="!photoFile && formData.photo_url"
                :src="`http://localhost:8000${formData.photo_url}`"
                class="q-mt-md rounded-borders"
                style="height: 120px; max-width: 100%"
                fit="contain"
              />
            </div>
            <div class="col-12 col-sm-6">
              <q-input outlined v-model.number="formData.stock" type="number" label="Quantidade em Stock *" :rules="[val => val >= 0 || 'Valor inválido']" />
            </div>
            <div class="col-12 col-sm-6">
              <q-input outlined v-model.number="formData.min_stock" type="number" label="Stock Mínimo *" :rules="[val => val >= 0 || 'Valor inválido']" />
            </div>
            <div class="col-12">
               <q-input outlined v-model="formData.notes" type="textarea" label="Notas (Opcional)" autogrow />
            </div>
          </q-card-section>
          
          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" flat @click="resetForm" v-close-popup />
            <q-btn :label="isEditing ? 'Guardar Alterações' : 'Adicionar Peça'" type="submit" color="primary" unelevated :loading="partStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableProps } from 'quasar';
import { usePartStore, type PartCreatePayload } from 'stores/part-store';
import type { Part } from 'src/models/part-models';

const $q = useQuasar();
const partStore = usePartStore();

const isDialogOpen = ref(false);
const editingPart = ref<Part | null>(null);
const isEditing = computed(() => !!editingPart.value);
const searchQuery = ref('');
const photoFile = ref<File | null>(null);

const initialFormData = {
  name: '',
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
  { name: 'name', label: 'Nome da Peça', field: 'name', align: 'left', sortable: true, required: true },
  { name: 'part_number', label: 'Código', field: 'part_number', align: 'left', sortable: true },
  { name: 'brand', label: 'Marca', field: 'brand', align: 'left', sortable: true },
  { name: 'stock', label: 'Stock (Atual / Mínimo)', field: 'stock', align: 'center', sortable: true },
  { name: 'location', label: 'Localização', field: 'location', align: 'left', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

watch(searchQuery, () => {
  void partStore.fetchParts(searchQuery.value);
});

function getStockColor(current: number, min: number): string {
  if (current <= 0) return 'negative';
  if (current <= min) return 'warning';
  return 'positive';
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
    title: 'Confirmar Remoção',
    message: `Tem a certeza de que deseja remover a peça "${part.name}"? Esta ação não pode ser desfeita.`,
    cancel: true,
    persistent: false,
    ok: { label: 'Remover', color: 'negative', unelevated: true },
  }).onOk(() => {
    void partStore.deletePart(part.id);
  });
}

onMounted(() => {
  void partStore.fetchParts();
});
</script>

