<template>
  <q-page class="row items-stretch window-height">
    <div class="col-12 col-md-6 flex flex-center bg-white">
      <q-card flat class="q-pa-lg animated fadeInLeft" style="width: 400px; max-width: 90vw;">
        <q-card-section class="text-center">
          <img
            src="~assets/vytruve-connect-logo.png"
            alt="Vytruve Connect Logo"
            style="width: 120px; height: auto; margin-bottom: 16px;"
          >
          <div class="text-h5 q-mt-sm text-weight-bold">TruCar</div>
          <div class="text-subtitle1 text-grey-8">Acesso ao sistema</div>
        </q-card-section>
        <q-card-section>
          <q-form @submit.prevent="handleLogin" class="q-gutter-md">
            <q-input
              outlined
              v-model="email"
              label="E-mail"
              type="email"
              lazy-rules
              :rules="[val => !!val || 'Por favor, digite seu e-mail']"
            >
              <template v-slot:prepend><q-icon name="alternate_email" /></template>
            </q-input>
            <q-input
              outlined
              v-model="password"
              label="Senha"
              type="password"
              lazy-rules
              :rules="[val => !!val || 'Por favor, digite sua senha']"
            >
              <template v-slot:prepend><q-icon name="lock" /></template>
            </q-input>
            <div>
              <q-btn
                type="submit"
                color="primary"
                label="Entrar"
                class="full-width text-weight-bold q-py-md"
                unelevated
                :loading="isLoading"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>

    <div
      v-if="$q.platform.is.desktop"
      ref="animatedBackground"
      class="col-12 col-md-6 flex flex-center text-white animated-bg"
      @mousemove="handleMouseMove"
    >
      <canvas ref="particleCanvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0;"></canvas>
      <div class="text-center q-pa-xl animated fadeInRight" style="z-index: 1; background-color: rgba(0,0,0,0.2); border-radius: 15px;">
        <h2 class="text-h2 text-weight-bolder" style="text-shadow: 2px 2px 8px rgba(0,0,0,0.3);">
          {{ sidePanel.title }}
        </h2>
        <q-list dark separator class="q-mt-lg text-left" style="max-width: 450px">
            <q-item>
              <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
              <q-item-section>Dashboard com gráficos e KPIs em tempo real.</q-item-section>
            </q-item>
            <q-item>
              <q-item-section avatar><q-icon name="map" /></q-item-section>
              <q-item-section>Controle e histórico completo de viagens.</q-item-section>
            </q-item>
            <q-item>
              <q-item-section avatar><q-icon name="build" /></q-item-section>
              <q-item-section>Gestão de manutenção preventiva.</q-item-section>
            </q-item>
             <q-item>
              <q-item-section avatar><q-icon name="group" /></q-item-section>
              <q-item-section>Gerenciamento de motoristas e gestores.</q-item-section>
            </q-item>
          </q-list>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth-store';

const $q = useQuasar(); // Adicionado para usar $q.platform
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const router = useRouter();
const authStore = useAuthStore();

// Objeto facilmente modificável para o texto do painel direito
const sidePanel = ref({
  title: 'Sua frota começa aqui!',
});

// --- LÓGICA DA ANIMAÇÃO ---
const particleCanvas = ref<HTMLCanvasElement | null>(null);
const animatedBackground = ref<HTMLDivElement | null>(null);
const particles = ref<Particle[]>([]);
const mouse = ref({ x: -1000, y: -1000 });
const numParticles = 100;
const connectionDistance = 120;
let animationFrameId: number;

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

function initParticles() {
  if (!particleCanvas.value || !animatedBackground.value) return;
  const canvas = particleCanvas.value;
  canvas.width = animatedBackground.value.offsetWidth;
  canvas.height = animatedBackground.value.offsetHeight;
  particles.value = Array.from({ length: numParticles }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 0.3,
    vy: (Math.random() - 0.5) * 0.3,
    radius: Math.random() * 2 + 1,
  }));
}

function drawParticles() {
  if (!particleCanvas.value) return;
  const canvas = particleCanvas.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const allPoints = [...particles.value, { ...mouse.value, radius: 0, vx: 0, vy: 0 }];

  allPoints.forEach((p1, index) => {
    if (p1.radius > 0) {
        ctx.beginPath();
        ctx.arc(p1.x, p1.y, p1.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.fill();
    }

    for (let j = index + 1; j < allPoints.length; j++) {
      const p2 = allPoints[j];
      if (p2) {
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < connectionDistance) {
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(255, 255, 255, ${1 - distance / connectionDistance})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    if (p1.radius > 0) {
        p1.x += p1.vx;
        p1.y += p1.vy;
        if (p1.x < 0 || p1.x > canvas.width) p1.vx *= -1;
        if (p1.y < 0 || p1.y > canvas.height) p1.vy *= -1;
    }
  });

  animationFrameId = requestAnimationFrame(drawParticles);
}

function handleMouseMove(event: MouseEvent) {
  if (!animatedBackground.value) return;
  const rect = animatedBackground.value.getBoundingClientRect();
  mouse.value.x = event.clientX - rect.left;
  mouse.value.y = event.clientY - rect.top;
}

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

onMounted(() => {
  if ($q.platform.is.desktop) {
    setTimeout(() => {
      initParticles();
      drawParticles();
      window.addEventListener('resize', initParticles);
    }, 100);
  }
});

onUnmounted(() => {
  if ($q.platform.is.desktop) {
    window.removeEventListener('resize', initParticles);
    cancelAnimationFrame(animationFrameId);
  }
});
</script>

<style lang="scss" scoped>

.animated-bg {
  /* Altere as cores do gradiente aqui */
  background: linear-gradient(-45deg, $primary, $secondary, lighten($primary, 20%), $accent);
  background-size: 400% 400%;
  animation: gradientAnimation 15s ease infinite;
  position: relative;
  overflow: hidden;
}

@keyframes gradientAnimation {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style>