<template>
  <q-page padding>
    <!-- CABEÇALHO -->
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gerenciamento de Implementos</h1>
      <!-- INÍCIO DA CORREÇÃO DE SINTAXE E PERMISSÃO -->
      <q-btn
        v-if="authStore.isManager"
        @click="openDialog()"
        color="primary"
        icon="add"
        label="Adicionar Implemento"
        unelevated
      />
      <!-- FIM DA CORREÇÃO -->
    </div>

    <!-- BARRA DE BUSCA -->
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

    <!-- ESTADO DE CARREGAMENTO (SKELETON) -->
    <div v-if="implementStore.isLoading" class="row q-col-gutter-md">
      <div v-for="n in 4" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered><q-skeleton height="150px" square /></q-card>
      </div>
    </div>

    <!-- LISTA DE CARDS DE IMPLEMENTOS -->
    <div v-else-if="filteredImplements.length > 0" class="row q-col-gutter-md">
      <div v-for="implement in filteredImplements" :key="implement.id" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <HoverCard>
          <q-card-section>
            <div class="flex items-center justify-between no-wrap q-mb-xs">
              <div class="text-h6 ellipsis">{{ implement.name }}</div>
              <q-badge
                :color="getStatusColor(implement.status)"
                :label="getStatusLabel(implement.status)"
                class="q-ml-sm"
              />
            </div>
            <div class="text-subtitle2 text-grey-8">{{ implement.brand }} - {{ implement.model }}</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="text-caption text-grey-7">Ano: {{ implement.year }}</div>
            <div v-if="implement.identifier" class="text-caption text-grey-7">Identificador: {{ implement.identifier }}</div>
          </q-card-section>
          <q-separator />
          <q-card-actions align="right">
            <!-- BOTÕES DE AÇÃO VISÍVEIS APENAS PARA GESTORES -->
            <template v-if="authStore.isManager">
              <q-btn flat dense round icon="edit" @click.stop="openDialog(implement)" />
              <q-btn flat dense round icon="delete" color="negative" @click.stop="promptToDelete(implement)" />
            </template>
          </q-card-actions>
        </HoverCard>
      </div>
    </div>

    <!-- ESTADO VAZIO -->
    <div v-else class="text-center q-pa-xl text-grey-7">
      <q-icon name="extension" size="4em" />
      <p class="q-mt-md">Nenhum implemento encontrado.</p>
      <!-- BOTÃO PARA ADICIONAR O PRIMEIRO IMPLEMENTO -->
      <q-btn
        v-if="authStore.isManager"
        @click="openDialog()"
        color="primary"
        label="Adicionar Primeiro Implemento"
        unelevated
        class="q-mt-md"
      />
    </div>

    <!-- DIÁLOGO DE ADICIONAR/EDITAR -->
    <q-dialog v-model="isDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Implemento' : 'Novo Implemento' }}</div>
        </q-card-section>
        <q-form @submit.prevent="handleSubmit" class="q-gutter-y-md">
          <q-card-section>
            <q-input outlined v-model="formData.name" label="Nome do Implemento *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Ano inválido']" />
            <q-input outlined v-model="formData.identifier" label="Nº de Série / Identificador" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar" :loading="isSubmitting" />
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
// --- INÍCIO DA CORREÇÃO ---
// Importe a store de autenticação para verificar a role do usuário
import { useAuthStore } from 'stores/auth-store';
// --- FIM DA CORREÇÃO ---
import type { Implement, ImplementCreate, ImplementUpdate } from 'src/models/implement-models';
import HoverCard from 'components/HoverCard.vue';

const $q = useQuasar();
const implementStore = useImplementStore();
// --- INÍCIO DA CORREÇÃO ---
// Instancie a store para poder usá-la no template
const authStore = useAuthStore();
// --- FIM DA CORREÇÃO ---
const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingImplement = ref<Implement | null>(null);
const isEditing = computed(() => !!editingImplement.value);
const searchTerm = ref('');

const formData = ref<Partial<Implement>>({});

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

function getStatusColor(status: string) {
  switch (status) {
    case 'available': return 'positive';
    case 'in_use': return 'warning';
    case 'maintenance': return 'negative';
    default: return 'grey';
  }
}

function getStatusLabel(status: string) {
  switch (status) {
    case 'available': return 'Disponível';
    case 'in_use': return 'Em Uso';
    case 'maintenance': return 'Manutenção';
    default: return status;
  }
}

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
    persistent: false,
    ok: { label: 'Excluir', color: 'negative', unelevated: true }
  }).onOk(() => {
    void implementStore.deleteImplement(implement.id);
  });
}

onMounted(() => {
  void implementStore.fetchAllImplementsForManagement();
});
</script>