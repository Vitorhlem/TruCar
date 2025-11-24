<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gerenciamento de Clientes</h1>
      
      <q-btn 
        @click="openCreateDialog" 
        color="primary" 
        icon="add" 
        label="Novo Cliente" 
        unelevated 
      />
    </div>

    <q-card flat bordered>
      <q-table
        :rows="clientStore.clients"
        :columns="columns"
        row-key="id"
        :loading="clientStore.isLoading"
        no-data-label="Nenhum cliente encontrado."
      >
        <template v-slot:body-cell-location="props">
          <q-td :props="props">
            <div v-if="props.row.address_city">
              {{ props.row.address_city }} <span v-if="props.row.address_state">- {{ props.row.address_state }}</span>
            </div>
            <div v-else class="text-grey-6">---</div>
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props" auto-width>
            <q-btn flat round dense color="primary" icon="edit" @click="openEditDialog(props.row)">
              <q-tooltip>Editar / Ver Detalhes</q-tooltip>
            </q-btn>
            <q-btn flat round dense color="negative" icon="delete" @click="promptToDelete(props.row)">
              <q-tooltip>Excluir</q-tooltip>
            </q-btn>
          </q-td>
        </template>
      </q-table>
    </q-card>
    
    <q-dialog v-model="isDialogOpen" @hide="resetForm">
      <q-card style="width: 600px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Cliente' : 'Novo Cliente' }}</div>
        </q-card-section>

        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="q-pt-none q-gutter-y-md">
            
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input outlined v-model="formData.name" label="Nome do Cliente *" :rules="[val => !!val || 'Campo obrigatório']" autofocus />
              </div>
              <div class="col-12 col-sm-6">
                 <q-input outlined v-model="formData.contact_person" label="Pessoa de Contato" />
              </div>
            </div>

            <q-separator class="q-my-sm" />
            <div class="text-subtitle2 text-grey-8">Endereço</div>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-4">
                <q-input 
                  outlined 
                  v-model="formData.cep" 
                  label="CEP" 
                  mask="#####-###"
                  unmasked-value
                  :loading="isCepLoading"
                  @blur="handleCepBlur"
                >
                  <template v-slot:append><q-icon name="search" /></template>
                </q-input>
              </div>
              <div class="col-12 col-sm-8">
                <q-input outlined v-model="formData.address_street" label="Rua / Logradouro" />
              </div>
            </div>

            <div class="row q-col-gutter-md">
              <div class="col-8">
                <q-input outlined v-model="formData.address_neighborhood" label="Bairro" />
              </div>
              <div class="col-4">
                <q-input outlined v-model="formData.address_number" label="Nº" />
              </div>
            </div>

            <div class="row q-col-gutter-md">
              <div class="col-8">
                <q-input outlined v-model="formData.address_city" label="Cidade" />
              </div>
              <div class="col-4">
                <q-input outlined v-model="formData.address_state" label="UF" />
              </div>
            </div>

            <q-separator class="q-my-sm" />
            <div class="text-subtitle2 text-grey-8">Contato</div>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input outlined v-model="formData.phone" label="Telefone" mask="(##) #####-####" />
              </div>
              <div class="col-12 col-sm-6">
                <q-input outlined v-model="formData.email" label="Email" type="email" />
              </div>
            </div>

          </q-card-section>

          <q-card-actions align="right" class="q-pa-md bg-grey-1">
            <q-btn flat label="Cancelar" v-close-popup color="grey-8" />
            <q-btn type="submit" unelevated color="primary" :label="isEditing ? 'Salvar Alterações' : 'Criar Cliente'" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { useClientStore } from 'stores/client-store';
import type { Client, ClientCreate, ClientUpdate } from 'src/models/client-models';
import { useCepApi } from 'src/composables/useCepApi';

const $q = useQuasar();
const clientStore = useClientStore();
const { isCepLoading, fetchAddressByCep } = useCepApi();

const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingId = ref<number | null>(null);
const isEditing = computed(() => editingId.value !== null);

const formData = ref<Partial<ClientCreate>>({});

const columns: QTableColumn[] = [
  { name: 'name', label: 'Nome', field: 'name', align: 'left', sortable: true },
  { name: 'contact', label: 'Contato', field: 'contact_person', align: 'left' },
  { name: 'phone', label: 'Telefone', field: 'phone', align: 'center' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'location', label: 'Localização', field: 'address_city', align: 'left' },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

function resetForm() {
  editingId.value = null;
  formData.value = { 
    name: '', 
    contact_person: '', 
    phone: '', 
    email: '',
    cep: '', 
    address_street: '', 
    address_number: '', 
    address_neighborhood: '', 
    address_city: '', 
    address_state: '' 
  };
}

function openCreateDialog() {
  resetForm();
  isDialogOpen.value = true;
}

function openEditDialog(client: Client) {
  editingId.value = client.id;
  // Copia os dados do cliente para o form
  formData.value = { ...client };
  isDialogOpen.value = true;
}

function promptToDelete(client: Client) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja excluir o cliente "${client.name}"?`,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
    cancel: { label: 'Cancelar', flat: true }
  }).onOk(() => {
    void (async () => {
      await clientStore.deleteClient(client.id);
    })();
  });
}

async function handleCepBlur() {
  if (formData.value.cep) {
    const address = await fetchAddressByCep(formData.value.cep);
    if (address) {
      formData.value.address_street = address.street;
      formData.value.address_neighborhood = address.neighborhood;
      formData.value.address_city = address.city;
      formData.value.address_state = address.state;
    }
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    // Limpeza de dados: campos vazios viram null
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const payload: any = { ...formData.value };
    Object.keys(payload).forEach((key) => {
      if (typeof payload[key] === 'string' && payload[key].trim() === '') {
        payload[key] = null;
      }
    });

    if (isEditing.value && editingId.value) {
      await clientStore.updateClient(editingId.value, payload as ClientUpdate);
      $q.notify({ type: 'positive', message: 'Cliente atualizado com sucesso!' });
    } else {
      await clientStore.addClient(payload as ClientCreate);
      $q.notify({ type: 'positive', message: 'Cliente criado com sucesso!' });
    }
    isDialogOpen.value = false;
  } catch (error) {
    console.error(error);
    // O Notify de erro detalhado já costuma ser exibido pela store
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  void clientStore.fetchAllClients();
});
</script>

<style scoped>
/* Garante que a barra de ações do modal tenha cor de fundo correta no modo escuro */
body.body--dark .bg-grey-1 {
  background: #1d1d1d !important;
}
</style>