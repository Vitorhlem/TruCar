<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gerenciamento de Clientes</h1>
      <q-btn @click="isDialogOpen = true" color="primary" icon="add" label="Novo Cliente" unelevated />
    </div>

    <q-card flat bordered>
      <q-table
        :rows="clientStore.clients"
        :columns="columns"
        row-key="id"
        :loading="clientStore.isLoading"
        no-data-label="Nenhum cliente encontrado."
      />
    </q-card>
    
    <q-dialog v-model="isDialogOpen" @hide="resetForm">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section><div class="text-h6">Novo Cliente</div></q-card-section>
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="formData.name" label="Nome do Cliente *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.contact_person" label="Pessoa de Contato" />
            <q-input outlined v-model="formData.phone" label="Telefone" mask="(##) #####-####" />
            <q-input outlined v-model="formData.email" label="Email" type="email" />
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
import { ref, onMounted } from 'vue';
import { useClientStore } from 'stores/client-store';
import type { ClientCreate } from 'src/models/client-models';
import type { QTableColumn } from 'quasar'; // <-- Importe o tipo QTableColumn


const clientStore = useClientStore();
const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const formData = ref<Partial<ClientCreate>>({});

const columns: QTableColumn[] = [
  { name: 'name', label: 'Nome', field: 'name', align: 'left', sortable: true },
  { name: 'contact', label: 'Contato', field: 'contact_person', align: 'left' },
  { name: 'phone', label: 'Telefone', field: 'phone', align: 'center' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
];

function resetForm() {
  formData.value = { name: '', contact_person: '', phone: '', email: '' };
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    await clientStore.addClient(formData.value as ClientCreate);
    isDialogOpen.value = false;
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  void clientStore.fetchAllClients();
});
</script>