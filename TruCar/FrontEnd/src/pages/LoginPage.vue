<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card flat bordered style="width: 400px; max-width: 90vw;">
      <q-card-section>
        <div class="text-center">
          <q-icon name="local_shipping" color="primary" size="64px" />
          <div class="text-h5 q-mt-sm text-weight-bold">Frota Ágil</div>
          <div class="text-subtitle1 text-grey-8">Acesso ao sistema</div>
        </div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="handleLogin">
          <q-input
            outlined
            v-model="email"
            label="E-mail"
            type="email"
            lazy-rules
            :rules="[val => !!val || 'Por favor, digite seu e-mail']"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="alternate_email" />
            </template>
          </q-input>

          <q-input
            outlined
            v-model="password"
            label="Senha"
            type="password"
            lazy-rules
            :rules="[val => !!val || 'Por favor, digite sua senha']"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
          </q-input>

          <div class="q-mt-lg">
            <q-btn
              type="submit"
              color="primary"
              label="Entrar"
              class="full-width text-weight-bold"
              unelevated
              :loading="isLoading"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth-store'; // <-- 1. Importe a store

const email = ref('');
const password = ref('');
const isLoading = ref(false);

const $q = useQuasar();
const router = useRouter();
const authStore = useAuthStore(); // <-- 2. Crie uma instância da store

async function handleLogin() {
  isLoading.value = true;
  try {
    // 3. Chame a ação de login da store com os dados do formulário
    await authStore.login({
      email: email.value,
      password: password.value,
    });
    
    // Se o login deu certo, notifica e redireciona
    $q.notify({
      color: 'positive',
      icon: 'check_circle',
      message: 'Login bem-sucedido!',
    });
    await router.push({ name: 'dashboard' });

  } catch (error) {
    // Se o login falhar (ex: senha errada), o back-end retornará um erro
    // que o Axios irá capturar.
    console.error('Falha no login:', error);
    $q.notify({
      color: 'negative',
      icon: 'error',
      message: 'E-mail ou senha inválidos. Por favor, tente novamente.',
    });
  } finally {
    isLoading.value = false;
  }
}
</script>