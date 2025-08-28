<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gerenciamento de Implementos</h1>
      <q-btn
        @click="openDialog()"
        color="primary"
        icon="add"
        label="Adicionar Implemento"
        unelevated
      />
    </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <q-input
          outlined
          dense
          debounce="300"
          v-model="searchTerm"
          placeholder="Buscar por nome, marca, modelo..."
        >
          <template v-slot:append><q-icon name="search" /></template>
        </q-input>
      </q-card-section>
    </q-card>

    <div v-if="implementStore.isLoading" class="row q-col-gutter-md">
      <div v-for="n in 4" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered><q-skeleton height="150px" square /></q-card>
      </div>
    </div>
    <div v-else-if="filteredImplements.length > 0" class="row q-col-gutter-md">
      <div v-for="implement in filteredImplements" :key="implement.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <HoverCard @click="openDialog(implement)">
          <q-card-section>
            <div class="text-h6 ellipsis">{{ implement.name }}</div>
            <div class="text-subtitle2 text-grey-8">{{ implement.brand }} - {{ implement.model }}</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="text-caption text-grey-7">Ano: {{ implement.year }}</div>
            <div v-if="implement.identifier" class="text-caption text-grey-7">Identificador: {{ implement.identifier }}</div>
          </q-card-section>
          <q-separator />
          <q-card-actions align="right">
            <q-btn flat dense icon="edit" label="Editar" @click.stop="openDialog(implement)" />
            <q-btn flat dense icon="delete" label="Excluir" color="negative" @click.stop="promptToDelete(implement)" />
          </q-card-actions>
        </HoverCard>
      </div>
    </div>
    <div v-else class="text-center q-pa-xl text-grey-7">
      <q-icon name="extension" size="4em" />
      <p class="q-mt-md">Nenhum implemento encontrado.</p>
    </div>

    <q-dialog v-model="isDialogOpen">
      <q-card style="width: 500px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Implemento' : 'Novo Implemento' }}</div>
        </q-card-section>
        <q-form @submit.prevent="handleSubmit" class="q-gutter-md q-pa-md">
          <q-input outlined v-model="formData.name" label="Nome do Implemento *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Ano inválido']" />
          <q-input outlined v-model="formData.identifier" label="Nº de Série / Identificador" />
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" color="primary" label="Salvar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useImplementStore } from 'stores/implement-store';
import type { Implement, ImplementCreate, ImplementUpdate } from 'src/models/implement-models';
import HoverCard from 'components/HoverCard.vue'; // <-- Importar o novo componente

const $q = useQuasar();
const implementStore = useImplementStore();
const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingImplement = ref<Implement | null>(null);
const isEditing = computed(() => !!editingImplement.value);
const searchTerm = ref(''); // Para a busca

const formData = ref<Partial<Implement>>({});

// Removi as colunas da q-table, pois agora estamos usando cards diretamente.
// Se quiser voltar para a q-table, pode reintroduzir as colunas.

const filteredImplements = computed(() => {
  if (!searchTerm.value) {
    return implementStore.implementList;
  }
  const lowerCaseSearch = searchTerm.value.toLowerCase();
  return implementStore.implementList.filter(implement =>
    implement.name.toLowerCase().includes(lowerCaseSearch) ||
    implement.brand.toLowerCase().includes(lowerCaseSearch) ||
    implement.model.toLowerCase().includes(lowerCaseSearch) ||
    implement.identifier?.toLowerCase().includes(lowerCaseSearch)
  );
});

function resetForm() {
  editingImplement.value = null;
  formData.value = {
    name: '', brand: '', model: '', year: new Date().getFullYear(), identifier: ''
  };
}

function openDialog(implement: Implement | null = null) {
  if (implement) {
    editingImplement.value = implement;
    formData.value = { ...implement };
  } else {
    resetForm();
  }
  isDialogOpen.value = true;
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value && editingImplement.value) {
      await implementStore.updateImplement(editingImplement.value.id, formData.value as ImplementUpdate);
    } else {
      await implementStore.addImplement(formData.value as ImplementCreate);
    }
    isDialogOpen.value = false;
  } finally {
    isSubmitting.value = false;
  }
}

function promptToDelete(implement: Implement) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem a certeza que deseja excluir o implemento "${implement.name}"?`,
    cancel: true,
    persistent: true,
    ok: { label: 'Excluir', color: 'negative', unelevated: true }
  }).onOk(() => {
    void implementStore.deleteImplement(implement.id);
  });
}

onMounted(() => {
  void implementStore.fetchAllImplements();
});
</script>

<style scoped>
/* Adicione estilos específicos da página se necessário, mas o HoverCard já tem o que precisamos */
</style>