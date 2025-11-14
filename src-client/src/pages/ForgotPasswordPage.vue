<template>
  <q-page class="window-height window-width flex flex-center main-container">
    <video ref="backgroundVideo" autoplay loop muted playsinline class="background-video">
      <source src="~assets/login-video.mp4" type="video/mp4">
    </video>
    <div class="video-overlay"></div>

    <div class="login-card-container">
      <q-card flat class="login-card q-pa-lg">
        <q-card-section class="text-center q-pb-none">
          <img
            src="~assets/trucar-logo-white.png"
            alt="TruCar Logo"
            class="animated-form-element"
            style="width: 120px; height: auto; margin-bottom: 16px; animation-delay: 0.1s;"
          >
          <div class="text-h5 q-mt-sm text-weight-bold text-white animated-form-element" style="animation-delay: 0.2s;">Recuperar Senha</div>
          <div class="text-subtitle1 text-grey-5 animated-form-element" style="animation-delay: 0.3s;">Insira o seu e-mail para continuar.</div>
        </q-card-section>

        <q-card-section class="q-pt-lg">
          <q-form @submit.prevent="handleRecoveryRequest" class="q-gutter-md">
            <q-input
              dark
              standout="bg-grey-10 text-white"
              v-model="email"
              label="Seu e-mail de registro"
              :rules="[val => !!val || 'Campo obrigatório', val => /.+@.+\..+/.test(val) || 'E-mail inválido']"
              class="animated-form-element"
              style="animation-delay: 0.4s;"
            >
              <template v-slot:prepend><q-icon name="alternate_email" /></template>
            </q-input>

            <div class="animated-form-element" style="animation-delay: 0.5s;">
              <q-btn
                type="submit"
                color="primary"
                class="full-width text-weight-bold q-py-md"
                unelevated
                :loading="isLoading"
                size="sml"
                label="Enviar Link de Recuperação"
              />
            </div>
          </q-form>
        </q-card-section>
        
        <q-card-section class="text-center animated-form-element" style="animation-delay: 0.6s;">
           <q-separator dark class="q-mb-md" />
           <span>Lembrou-se da senha? <q-btn to="/auth/login" label="Voltar ao Login" flat no-caps dense class="text-primary text-weight-bold"/></span>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useRouter } from 'vue-router';

const email = ref('');
const isLoading = ref(false);
const authStore = useAuthStore();
const router = useRouter();

async function handleRecoveryRequest() {
  if (isLoading.value) return;
  isLoading.value = true;
  
  try {
    await authStore.requestPasswordReset({ email: email.value });
    // A notificação de sucesso já é exibida pela store
    setTimeout(() => {
      // Redireciona para o login após um tempo para o usuário ver a notificação
      void router.push({ name: 'login' });
    }, 4000);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style lang="scss" scoped>
/* ESTES ESTILOS SÃO OS MESMOS DA LOGINPAGE.VUE PARA MANTER A CONSISTÊNCIA */
.main-container {
  background-image: url('~assets/login-background.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
  position: relative;
}

.background-video {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 105%;
  min-height: 105%;
  width: auto;
  height: auto;
  z-index: 1;
  transform: translateX(-50%) translateY(-50%) scale(1.1);
  transition: transform 0.3s ease-out;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(5, 10, 20, 0.4) 0%, rgba(5, 10, 20, 0.9) 100%);
  z-index: 2;
}

.login-card-container {
  perspective: 1500px;
  z-index: 3;
}

.login-card {
  width: 420px;
  max-width: 90vw;
  background: rgba(18, 23, 38, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: transform 0.3s ease-out;
  position: relative;
  overflow: hidden;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animated-form-element {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

:deep(.q-field--standout.q-field--focused .q-field__control) {
  box-shadow: 0 0 10px rgba(var(--q-color-primary-rgb), 0.5);
}
:deep(.q-field--standout .q-field__control) {
  transition: box-shadow 0.3s ease;
}
</style>