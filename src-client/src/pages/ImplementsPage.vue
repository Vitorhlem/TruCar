<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gerenciamento de Implementos</h1>
      <q-btn
        v-if="authStore.isManager"
        @click="openDialog()"
        color="primary"
        icon="add"
        label="Adicionar Implemento"
        unelevated
      />
    </div>

    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-input
              outlined
              dense
              debounce="300"
              v-model="searchTerm"
              placeholder="Buscar por nome, tipo, marca, modelo..."
            >
              <template v-slot:append><q-icon name="search" /></template>
            </q-input>
          </div>
          <div class="col-6 col-sm-3">
            <q-select
              outlined
              dense
              v-model="filterStatus"
              :options="statusOptions"
              label="Filtrar por Status"
              emit-value
              map-options
              clearable
            />
          </div>
          <div class="col-6 col-sm-3">
            <q-select
              outlined
              dense
              v-model="filterType"
              :options="typeOptions"
              label="Filtrar por Tipo"
              clearable
              :disable="typeOptions.length === 0"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
    <div v-if="implementStore.isLoading" class="row q-col-gutter-md">
      <div v-for="n in 4" :key="n" class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card flat bordered><q-skeleton height="150px" square /></q-card>
      </div>
    </div>

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
            
            <div v-if="implement.type" class="text-caption text-primary text-weight-medium q-mt-xs">
              {{ implement.type }}
            </div>

          </q-card-section>

          <q-card-section class="q-pt-none">
            <div class="text-caption text-grey-7">Ano: {{ implement.year }}</div>
            <div v-if="implement.identifier" class="text-caption text-grey-7">Identificador: {{ implement.identifier }}</div>
            <div v-if="implement.acquisition_value" class="text-caption text-grey-7">
              Valor: {{ new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(implement.acquisition_value) }}
            </div>
            <div v-if="implement.acquisition_date" class="text-caption text-grey-7">
              Aquisição: {{ new Date(implement.acquisition_date).toLocaleDateString('pt-BR', { timeZone: 'UTC' }) }}
            </div>
          </q-card-section>

          <q-separator />
          <q-card-actions align="right">
            <template v-if="authStore.isManager">
              <q-btn flat dense round icon="edit" @click.stop="openDialog(implement)" />
              <q-btn flat dense round icon="delete" color="negative" @click.stop="promptToDelete(implement)" />
            </template>
          </q-card-actions>
        </HoverCard>
      </div>
    </div>

    <div v-else class="text-center q-pa-xl text-grey-7">
      <q-icon name="extension" size="4em" />
      <p class="q-mt-md" v-if="searchTerm || filterStatus || filterType">
        Nenhum implemento encontrado com os filtros atuais.
      </p>
      <p class="q-mt-md" v-else>
        Nenhum implemento cadastrado.
      </p>
      
      <q-btn
        v-if="authStore.isManager && !searchTerm && !filterStatus && !filterType"
        @click="openDialog()"
        color="primary"
        label="Adicionar Primeiro Implemento"
        unelevated
        class="q-mt-md"
      />
    </div>

    <q-dialog v-model="isDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Implemento' : 'Novo Implemento' }}</div>
        </q-card-section>

        <q-form @submit.prevent="handleSubmit" class="q-gutter-y-md">
          <q-card-section>
            
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <q-input outlined v-model="formData.name" label="Nome do Implemento *" :rules="[val => !!val || 'Campo obrigatório']" />
              </div>
              <div class="col-6">
                <q-input outlined v-model="formData.brand" label="Marca *" :rules="[val => !!val || 'Campo obrigatório']" />
              </div>
              <div class="col-6">
                <q-input outlined v-model="formData.model" label="Modelo *" :rules="[val => !!val || 'Campo obrigatório']" />
              </div>
              <div class="col-6">
                <q-input 
                  outlined 
                  v-model="formData.type" 
                  label="Tipo (Ex: Arado, Plantadeira)" 
                />
              </div>
              <div class="col-6">
                <q-input outlined v-model.number="formData.year" type="number" label="Ano *" :rules="[val => val > 1980 || 'Ano inválido']" />
              </div>
            </div>

            <q-input outlined v-model="formData.identifier" label="Nº de Série / Identificador" class="q-mt-md" />

            <div class="row q-col-gutter-md q-mt-xs">
              <div class="col-6">
                <q-input 
                  outlined 
                  v-model="formData.acquisition_date" 
                  label="Data de Aquisição"
                  type="date"
                  stack-label
                />
              </div>
              <div class="col-6">
                <q-input 
                  outlined 
                  v-model.number="formData.acquisition_value" 
                  label="Valor de Aquisição" 
                  type="number"
                  prefix="R$"
                  :step="0.01"
                />
              </div>
            </div>

            <q-input 
              outlined 
              v-model="formData.notes" 
              label="Notas" 
              type="textarea" 
              autogrow 
              class="q-mt-md"
            />

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
import { useAuthStore } from 'stores/auth-store';
import type { Implement, ImplementCreate, ImplementUpdate } from 'src/models/implement-models';
import HoverCard from 'components/HoverCard.vue';
import { ImplementStatus } from 'src/models/implement-models'; // Importando o Enum

const $q = useQuasar();
const implementStore = useImplementStore();
const authStore = useAuthStore();
const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingImplement = ref<Implement | null>(null);
const isEditing = computed(() => !!editingImplement.value);

// --- 2. ADICIONAR REFS PARA OS FILTROS ---
const searchTerm = ref('');
const filterStatus = ref<ImplementStatus | null>(null);
const filterType = ref<string | null>(null);

const formData = ref<Partial<Implement>>({});

// --- 3. ADICIONAR OPÇÕES PARA OS FILTROS ---

// Opções de Status (baseado no seu modelo)
const statusOptions = [
  { label: 'Disponível', value: ImplementStatus.AVAILABLE },
  { label: 'Em Uso', value: ImplementStatus.IN_USE },
  { label: 'Manutenção', value: ImplementStatus.MAINTENANCE }
];

// Opções de Tipo (gerado dinamicamente da lista do store)
const typeOptions = computed(() => {
  const types = implementStore.implementList
    .map(impl => impl.type) // Pega todos os tipos (incluindo nulos e duplicados)
    .filter((type): type is string => !!type); // Filtra nulos/vazios
  
  // Retorna uma lista de strings únicas
  return [...new Set(types)];
});

// --- 4. ATUALIZAR 'filteredImplements' PARA USAR OS FILTROS ---
const filteredImplements = computed(() => {
  const lowerCaseSearch = searchTerm.value.toLowerCase();

  return implementStore.implementList.filter(implement => {
    // Filtro de Texto
    const searchMatch = !searchTerm.value || (
      implement.name.toLowerCase().includes(lowerCaseSearch) ||
      implement.brand.toLowerCase().includes(lowerCaseSearch) ||
      implement.model.toLowerCase().includes(lowerCaseSearch) ||
      (implement.identifier && implement.identifier.toLowerCase().includes(lowerCaseSearch)) ||
      (implement.type && implement.type.toLowerCase().includes(lowerCaseSearch))
    );

    // Filtro de Status
    const statusMatch = !filterStatus.value || implement.status === filterStatus.value;

    // Filtro de Tipo
    const typeMatch = !filterType.value || implement.type === filterType.value;

    return searchMatch && statusMatch && typeMatch;
  });
});

// FIX: Changed parameter type from 'string' to 'ImplementStatus'
function getStatusColor(status: ImplementStatus) {
  switch (status) {
    case ImplementStatus.AVAILABLE: return 'positive';
    case ImplementStatus.IN_USE: return 'warning';
    case ImplementStatus.MAINTENANCE: return 'negative';
    default: return 'grey';
  }
}

// FIX: Changed parameter type from 'string' to 'ImplementStatus'
function getStatusLabel(status: ImplementStatus) {
  switch (status) {
    case ImplementStatus.AVAILABLE: return 'Disponível';
    case ImplementStatus.IN_USE: return 'Em Uso';
    case ImplementStatus.MAINTENANCE: return 'Manutenção';
    default: return status;
  }
}

// ATUALIZADO 'resetForm' COM OS NOVOS CAMPOS
function resetForm() {
  editingImplement.value = null;
  formData.value = {
    name: '', 
    brand: '', 
    model: '', 
    type: '',
    year: new Date().getFullYear(), 
    identifier: '',
    acquisition_date: null,
    acquisition_value: null,
    notes: ''
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

// ATUALIZADO 'handleSubmit' PARA TRATAR VALORES NULOS
async function handleSubmit() {
  isSubmitting.value = true;
  try {
    const payload = { ...formData.value };
    // Limpa valores que podem ser 'undefined' ou vazios
    if (!payload.acquisition_date) payload.acquisition_date = null;
    if (!payload.acquisition_value) payload.acquisition_value = null;
    if (!payload.notes) payload.notes = null;
    if (!payload.type) payload.type = null;
    if (!payload.identifier) payload.identifier = null;

    if (isEditing.value && editingImplement.value) {
      await implementStore.updateImplement(editingImplement.value.id, payload as ImplementUpdate);
    } else {
      await implementStore.addImplement(payload as ImplementCreate);
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