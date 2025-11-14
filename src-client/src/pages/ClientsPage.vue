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
          <q-card-section>
            <!-- Adicionado q-gutter-y-md para espaçamento vertical -->
            <div class="q-gutter-y-md">
              <q-input outlined v-model="formData.name" label="Nome do Cliente *" :rules="[val => !!val || 'Campo obrigatório']" autofocus />
              <q-input outlined v-model="formData.contact_person" label="Pessoa de Contato" />
              
              <!-- CAMPOS DE ENDEREÇO COM BUSCA DE CEP -->
              <q-input 
                outlined 
                v-model="formData.cep" 
                label="CEP" 
                mask="#####-###"
                unmasked-value
                :loading="isCepLoading"
                @blur="handleCepBlur"
              >
                <!-- Ícone corrigido para um mais apropriado -->
                <template v-slot:prepend><q-icon name="location_pin" /></template>
              </q-input>

              <q-input outlined v-model="formData.address_street" label="Rua / Logradouro" />

              <div>
                <div class="col-8"><q-input outlined v-model="formData.address_neighborhood" label="Bairro" /></div>
                </div>

                  <div>
                <div class="col-4"><q-input outlined v-model="formData.address_number" label="Nº" /></div>
                   </div>
                   
                   <div></div>
              <div class="row q-col-gutter-md">
                <div class="col-8"><q-input outlined v-model="formData.address_city" label="Cidade" /></div>
                <div class="col-4"><q-input outlined v-model="formData.address_state" label="UF" /></div>
              </div>
              <!-- FIM DOS CAMPOS DE ENDEREÇO -->
              
              <q-input outlined v-model="formData.phone" label="Telefone" mask="(##) #####-####" />
              <q-input outlined v-model="formData.email" label="Email" type="email" />
            </div>
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
import type { QTableColumn } from 'quasar';
import { useCepApi } from 'src/composables/useCepApi';

const clientStore = useClientStore();
const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const formData = ref<Partial<ClientCreate>>({});
const { isCepLoading, fetchAddressByCep } = useCepApi();

const columns: QTableColumn[] = [
  { name: 'name', label: 'Nome', field: 'name', align: 'left', sortable: true },
  { name: 'contact', label: 'Contato', field: 'contact_person', align: 'left' },
  { name: 'phone', label: 'Telefone', field: 'phone', align: 'center' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
];

function resetForm() {
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

