<template>
  <q-page
    class="window-height window-width flex flex-center main-container"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- 1. Fundo com Vídeo e Overlay -->
    <video ref="backgroundVideo" autoplay loop muted playsinline class="background-video">
      <source src="https://cdn.pixabay.com/video/2020/10/28/53582-475000650.mp4" type="video/mp4">
      O seu navegador não suporta o tag de vídeo.
    </video>
    <div class="video-overlay"></div>

    <!-- 2. Container do Formulário (para perspetiva 3D) -->
    <div class="login-card-container">
      <q-card ref="loginCard" flat class="login-card q-pa-lg">
        <q-card-section class="text-center q-pb-none">
          <img
            src="https://placehold.co/120x50/transparent/FFFFFF?text=TruCar"
            alt="TruCar Logo"
            style="width: 120px; height: auto; margin-bottom: 16px;"
          >
          <div class="text-h5 q-mt-sm text-weight-bold text-white">Bem-vindo ao TruCar</div>
          <div class="text-subtitle1 text-grey-5">Acesse a sua central de operações.</div>
        </q-card-section>

        <q-card-section class="q-pt-lg">
          <q-form @submit.prevent="handleLogin" class="q-gutter-md">
            <q-input
              dark
              standout="bg-grey-10 text-white"
              v-model="email"
              label="E-mail ou ID de Utilizador"
              :rules="[val => !!val || 'Campo obrigatório']"
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

            <div class="row items-center justify-between text-grey-5">
              <q-checkbox v-model="rememberMe" label="Lembrar-me" size="sm" dark />
              <q-btn label="Esqueceu a senha?" flat no-caps size="sm" class="text-primary" />
            </div>

            <div>
              <q-btn
                type="submit"
                color="primary"
                label="Acessar Plataforma"
                class="full-width text-weight-bold q-py-md"
                unelevated
                :loading="isLoading"
                size="lg"
              />
            </div>
          </q-form>
        </q-card-section>
        
        <q-card-section class="text-center">
           <q-separator class="q-mb-md" />
           <span>Não tem uma conta? <q-btn to="/auth/register" label="Registre-se" flat no-caps dense class="text-primary text-weight-bold"/></span>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
// LÓGICA CORRETA IMPORTADA
import { useAuthStore } from 'stores/auth-store';

// --- Refs para os Elementos do DOM ---
const loginCard = ref<HTMLElement | null>(null);
const backgroundVideo = ref<HTMLVideoElement | null>(null);

// --- Lógica do Formulário ---
const $q = useQuasar();
const email = ref('');
const password = ref('');
const rememberMe = ref(false); // Adicionado para consistência, embora não usado na função de login
const isLoading = ref(false);
const isPasswordVisible = ref(false);
const router = useRouter();
// LÓGICA CORRETA INSTANCIADA
const authStore = useAuthStore();

// LÓGICA DE LOGIN CORRETA RESTAURADA
async function handleLogin() {
  isLoading.value = true;
  try {
    await authStore.login({ email: email.value, password: password.value });
    await router.push({ name: 'dashboard' });
  } catch {
    $q.notify({ color: 'negative', icon: 'error', message: 'E-mail ou senha inválidos.' });
  } finally {
    isLoading.value = false;
  }
}

// --- Lógica de Interatividade (Parallax e Efeito 3D) ---
function handleMouseMove(event: MouseEvent) {
  const { clientX, clientY } = event;
  const width = window.innerWidth;
  const height = window.innerHeight;

  const mouseX = (clientX / width) * 2 - 1;
  const mouseY = (clientY / height) * 2 - 1;

  if (loginCard.value) {
    const rotateY = mouseX * 8;
    const rotateX = -mouseY * 8;
    loginCard.value.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
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
  }
  if (backgroundVideo.value) {
    backgroundVideo.value.style.transform = 'translateX(0px) translateY(0px) scale(1.1)';
  }
}
</script>

<style lang="scss" scoped>
.main-container {
  background-image: url('https://images.pexels.com/photos/1252890/pexels-photo-1252890.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2');
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
}
</style>

