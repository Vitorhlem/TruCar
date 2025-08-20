<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card class="q-pa-md" style="width: 400px">
      <q-card-section>
        <div class="text-h6">Criar Nova Conta TruCar</div>
        <div class="text-subtitle2">Crie a sua organização e comece a gerir a sua frota.</div>
      </q-card-section>
      <q-form @submit.prevent="onSubmit">
        <q-card-section class="q-gutter-y-md">
          <q-input outlined v-model="formData.organization_name" label="Nome da Empresa *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-select
            outlined v-model="formData.sector" :options="sectorOptions" label="Setor da Empresa *"
            emit-value map-options :rules="[val => !!val || 'Selecione um setor']"
          />
          <q-input outlined v-model="formData.full_name" label="Seu Nome Completo *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model="formData.email" type="email" label="Seu E-mail *" :rules="[val => !!val || 'Campo obrigatório']" />
          <q-input outlined v-model="formData.password" type="password" label="Sua Senha *" :rules="[val => !!val || 'Campo obrigatório']" />
        </q-card-section>
        <q-card-actions class="q-px-md">
          <q-btn type="submit" color="primary" label="Registar e Entrar" class="full-width" unelevated :loading="isLoading" />
          <q-btn to="/auth/login" label="Já tenho uma conta" flat class="full-width q-mt-sm" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import axios from 'axios';
import { useAuthStore } from 'stores/auth-store';

const formData = ref({
  organization_name: '',
  sector: null as 'agronegocio' | 'construcao_civil' | 'servicos' | null,
  full_name: '',
  email: '',
  password: '',
});

// Em RegisterPage.vue
const sectorOptions = [
  { label: 'Agronegócio', value: 'agronegocio' }, // <-- CORRETO
  { label: 'Construção Civil', value: 'construcao_civil' }, // <-- CORRETO
  { label: 'Prestadores de Serviço', value: 'servicos' }, // <-- CORRETO
];

const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();
const isLoading = ref(false);

async function onSubmit() {
  isLoading.value = true;
  try {
    // Primeiro, regista a nova organização e o utilizador
    await api.post('/login/register', formData.value);
    
    // Depois, faz o login automaticamente para obter o token e os dados do utilizador
    await authStore.login({
      email: formData.value.email,
      password: formData.value.password
    });
    
    // Finalmente, redireciona para o dashboard
    await router.push({ name: 'dashboard' });

  } catch (error) {
    let errorMessage = 'Erro ao criar conta. Tente novamente.';
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    $q.notify({ type: 'negative', message: errorMessage });
  } finally {
    isLoading.value = false;
  }
}
</script>