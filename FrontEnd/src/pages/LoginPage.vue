<template>
  <q-page
    class="window-height window-width flex flex-center main-container"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- 1. Fundo com Vídeo Local e Overlay -->
    <video ref="backgroundVideo" autoplay loop muted playsinline class="background-video">
      <source src="~assets/login-video.mp4" type="video/mp4">
      O seu navegador não suporta o tag de vídeo.
    </video>
    <div class="video-overlay"></div>

    <!-- 2. Container do Formulário (para perspetiva 3D) -->
    <div class="login-card-container">
      <q-card ref="loginCard" flat class="login-card q-pa-lg">
        <!-- EFEITO DE BRILHO ADICIONADO -->
        <div class="card-shine"></div>
        <q-card-section class="text-center q-pb-none">
          <!-- ANIMAÇÕES SEQUENCIAIS ADICIONADAS -->
          <img
            src="~assets/trucar-logo-white.png"
            alt="TruCar Logo"
            class="animated-form-element"
            style="width: 120px; height: auto; margin-bottom: 16px; animation-delay: 0.1s;"
          >
          <div class="text-h5 q-mt-sm text-weight-bold text-white animated-form-element" style="animation-delay: 0.2s;">Bem-vindo ao Controlo</div>
          <div class="text-subtitle1 text-grey-5 animated-form-element" style="animation-delay: 0.3s;">Acesse a sua central de operações.</div>
        </q-card-section>

        <q-card-section class="q-pt-lg">
          <q-form @submit.prevent="handleLogin" class="q-gutter-md">
            <q-input
              dark
              standout="bg-grey-10 text-white"
              v-model="email"
              label="E-mail ou ID de Utilizador"
              :rules="[val => !!val || 'Campo obrigatório']"
              class="animated-form-element"
              style="animation-delay: 0.4s;"
            >
              <template v-slot:prepend><q-icon name="alternate_email" /></template>
            </q-input>

            <q-input
              dark
              standout="bg-grey-10 text-white"
              v-model="password"
              label="Senha"
              :type="isPasswordVisible ? 'text' : 'password'"
              :rules="[val => !!val || 'Campo obrigatório']"
              class="animated-form-element"
              style="animation-delay: 0.5s;"
            >
              <template v-slot:prepend><q-icon name="lock" /></template>
              <template v-slot:append>
                <q-icon
                  :name="isPasswordVisible ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPasswordVisible = !isPasswordVisible"
                />
              </template>
            </q-input>

            <div class="row items-center justify-between text-grey-5 animated-form-element" style="animation-delay: 0.6s;">
              <q-checkbox v-model="rememberMe" label="Lembrar-me" size="sm" dark />
              <q-btn label="Esqueceu a senha?" flat no-caps size="sm" class="text-primary" />
            </div>

            <div class="animated-form-element" style="animation-delay: 0.7s;">
              <!-- BOTÃO COM MICRO-INTERAÇÃO -->
              <q-btn
                type="submit"
                :color="getButtonColor"
                class="full-width text-weight-bold q-py-md login-btn"
                unelevated
                :loading="isLoading"
                size="lg"
              >
                <transition name="fade" mode="out-in">
                  <span v-if="!isLoading && loginStatus === 'idle'">Acessar Plataforma</span>
                  <q-icon v-else-if="!isLoading && loginStatus === 'success'" name="check" />
                  <q-icon v-else-if="!isLoading && loginStatus === 'error'" name="close" />
                </transition>
              </q-btn>
            </div>
          </q-form>
        </q-card-section>
        
        <q-card-section class="text-center animated-form-element" style="animation-delay: 0.8s;">
           <q-separator dark class="q-mb-md" />
           <span>Não tem uma conta? <q-btn to="/auth/register" label="Registre-se" flat no-caps dense class="text-primary text-weight-bold"/></span>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth-store';

const loginCard = ref<HTMLElement | null>(null);
const backgroundVideo = ref<HTMLVideoElement | null>(null);

const $q = useQuasar();
const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const isLoading = ref(false);
const isPasswordVisible = ref(false);
const loginStatus = ref<'idle' | 'success' | 'error'>('idle');
const router = useRouter();
const authStore = useAuthStore();

const getButtonColor = computed(() => {
  if (loginStatus.value === 'success') return 'positive';
  if (loginStatus.value === 'error') return 'negative';
  return 'primary';
});

async function handleLogin() {
  if (isLoading.value) return;
  isLoading.value = true;
  loginStatus.value = 'idle';

  try {
    await authStore.login({ email: email.value, password: password.value });
    loginStatus.value = 'success';
    isLoading.value = false;
    setTimeout(() => {
      void router.push({ name: 'dashboard' });
    }, 800);
  } catch {
    loginStatus.value = 'error';
    isLoading.value = false;
    $q.notify({ color: 'negative', icon: 'error', message: 'E-mail ou senha inválidos.' });
    setTimeout(() => {
      loginStatus.value = 'idle';
    }, 2000);
  }
}

function handleMouseMove(event: MouseEvent) {
  const { clientX, clientY } = event;
  const width = window.innerWidth;
  const height = window.innerHeight;

  const mouseX = (clientX / width) * 2 - 1;
  const mouseY = (clientY / height) * 2 - 1;

  if (loginCard.value) {
    // Rotação 3D
    const rotateY = mouseX * 8;
    const rotateX = -mouseY * 8;
    loginCard.value.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

    // Efeito de brilho
    const rect = loginCard.value.getBoundingClientRect();
    const shineX = event.clientX - rect.left;
    const shineY = event.clientY - rect.top;
    loginCard.value.style.setProperty('--shine-x', `${shineX}px`);
    loginCard.value.style.setProperty('--shine-y', `${shineY}px`);
    loginCard.value.style.setProperty('--shine-opacity', '1');
  }
  
  if (backgroundVideo.value) {
    const transX = -mouseX * 20;
    const transY = -mouseY * 20;
    backgroundVideo.value.style.transform = `translateX(${transX}px) translateY(${transY}px) scale(1.1)`;
  }
}

function handleMouseLeave() {
  if (loginCard.value) {
    loginCard.value.style.transform = 'rotateX(0deg) rotateY(0deg)';
    loginCard.value.style.setProperty('--shine-opacity', '0');
  }
  if (backgroundVideo.value) {
    backgroundVideo.value.style.transform = 'translateX(0px) translateY(0px) scale(1.1)';
  }
}
</script>

<style lang="scss" scoped>
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
  overflow: hidden; // Necessário para o efeito de brilho
}

/* 3. EFEITO DE BRILHO NO CARTÃO */
.card-shine {
  position: absolute;
  top: var(--shine-y, 0);
  left: var(--shine-x, 0);
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0) 60%);
  opacity: var(--shine-opacity, 0);
  transition: opacity 0.3s ease-out;
  pointer-events: none;
}

/* 2. ANIMAÇÃO DE ENTRADA SEQUENCIAL */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animated-form-element {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

/* 4. TRANSIÇÃO DE FOCO NOS INPUTS */
:deep(.q-field--standout.q-field--focused .q-field__control) {
  box-shadow: 0 0 10px rgba(var(--q-color-primary-rgb), 0.5);
}
:deep(.q-field--standout .q-field__control) {
  transition: box-shadow 0.3s ease;
}

/* 1. MICRO-INTERAÇÃO NO BOTÃO */
.login-btn {
  transition: background-color 0.3s ease;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

