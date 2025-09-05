<template>
  <q-page>
    <div class="row window-height">
      <!-- Coluna Esquerda: REFORMULADA com tema escuro e glassmorphism -->
      <div class="col-12 col-md-6 flex flex-center form-panel">
        <q-card flat class="register-card q-pa-md">
          
          <q-card-section class="text-center q-pb-none">
            <img src="https://placehold.co/150x40/transparent/FFFFFF?text=TruCar" alt="TruCar Logo" style="height: 40px; margin-bottom: 1rem;">
            <div class="text-h5 text-weight-bold text-white">Crie a sua Conta Gratuita</div>
            <div class="text-subtitle1 text-grey-5">Comece a otimizar a sua frota hoje mesmo.</div>
          </q-card-section>
          
          <q-stepper
            v-model="step"
            ref="stepper"
            color="primary"
            animated
            flat
            dark
            header-nav
            class="q-mt-md transparent-stepper"
          >
            <!-- Etapa 1: Empresa -->
            <q-step
              :name="1"
              title="Sua Empresa"
              icon="business"
              :done="step > 1"
            >
              <q-input 
                dark
                standout="bg-grey-10"
                v-model="formData.organization_name" 
                label="Nome da Empresa *" 
                :rules="[val => !!val || 'Campo obrigatório']"
                class="q-mb-md"
              >
                <template v-slot:prepend><q-icon name="business" /></template>
              </q-input>

              <q-select
                dark
                standout="bg-grey-10"
                v-model="formData.sector"
                :options="sectorOptions"
                label="Setor da Empresa *"
                emit-value
                map-options
                :rules="[val => !!val || 'Selecione um setor']"
              >
                <template v-slot:prepend>
                  <q-icon :name="sectorIcon" />
                </template>
              </q-select>

              <q-stepper-navigation class="q-mt-lg">
                <q-btn @click="() => stepper?.next()" color="primary" label="Continuar" class="full-width" unelevated />
              </q-stepper-navigation>
            </q-step>

            <!-- Etapa 2: Utilizador -->
            <q-step
              :name="2"
              title="Seus Dados"
              icon="account_circle"
            >
              <q-input dark standout="bg-grey-10" v-model="formData.full_name" label="Seu Nome Completo *" :rules="[val => !!val || 'Campo obrigatório']" class="q-mb-md">
                  <template v-slot:prepend><q-icon name="person" /></template>
              </q-input>
              <q-input dark standout="bg-grey-10" v-model="formData.email" type="email" label="Seu E-mail *" :rules="[val => !!val || 'Campo obrigatório']" class="q-mb-md">
                  <template v-slot:prepend><q-icon name="alternate_email" /></template>
              </q-input>
              <q-input dark standout="bg-grey-10" v-model="formData.password" type="password" label="Sua Senha *" :rules="[val => !!val || 'Campo obrigatório']">
                  <template v-slot:prepend><q-icon name="lock" /></template>
              </q-input>
              
              <q-stepper-navigation class="q-mt-lg row q-col-gutter-sm">
                <div class="col-6">
                    <q-btn flat @click="() => stepper?.previous()" color="primary" label="Voltar" class="full-width" />
                </div>
                  <div class="col-6">
                    <q-btn @click="onSubmit" color="primary" label="Criar Minha Conta" class="full-width" unelevated :loading="isLoading" />
                  </div>
              </q-stepper-navigation>
            </q-step>
          </q-stepper>
          
            <div class="text-center q-mt-md">
               <span>Já tem uma conta? <q-btn to="/auth/login" label="Faça o login" flat no-caps dense class="text-primary text-weight-bold"/></span>
            </div>

            <q-separator dark class="q-my-lg" />

            <!-- Selos de Segurança -->
            <div class="security-seals text-center">
              <div class="seal-item">
                <q-icon name="verified_user" color="positive" />
                <span>SSL Criptografado</span>
              </div>
              <div class="seal-item">
                <q-icon name="lock" color="positive" />
                <span>LGPD Compliant</span>
              </div>
              <div class="seal-item">
                <q-icon name="shield" color="positive" />
                <span>Dados Seguros</span>
              </div>
            </div>

        </q-card>
      </div>

      <!-- Coluna Direita: A Área Visual (Mantida) -->
      <div class="col-md-6 register-visual-container gt-sm">
        <div class="image-strip" style="background-image: url('https://pixabay.com/get/g6ba7cef8f76b1143adfb7b616c5b6cb37f1e875e876dc2a418932132003a62312bc9f5251a229d808ea70aee8c98f936.jpg');"></div>
        <div class="image-strip" style="background-image: url('https://pixabay.com/get/ga28d055e275545ea851c344afb5807456ec4125f23bbb6676a7a17d9c6d1f0f77fdbb5e8725168576d693207f0afbe3c.jpg');"></div>
        <div class="image-strip" style="background-image: url('https://pixabay.com/get/gce582312228bc092a57a25c6580c3077261faff6162d4f012f2b9080c43a7b6f511f1a39a4ee31df085cb2f999de2ee5.jpg');"></div>
        <div class="image-strip" style="background-image: url('https://pixabay.com/get/g0f13585a69a8dc2b46af7d7227418e566c9e56a350f8211bab68859228b0b6c6a677eabf131839fd28155342fa679a96.jpg');"></div>
        <div class="visual-content text-white">
            <h2 class="text-h2 text-weight-bolder">TruCar</h2>
            <h5 class="text-h5 text-weight-light q-mb-xl">A solução completa para a sua frota, seja qual for o seu setor.</h5>

            <q-list dark separator class="benefits-list">
              <q-item>
                <q-item-section avatar>
                  <q-icon color="white" name="check_circle" />
                </q-item-section>
                <q-item-section>Reduza custos com combustível e manutenção.</q-item-section>
              </q-item>
              <q-item>
                <q-item-section avatar>
                  <q-icon color="white" name="check_circle" />
                </q-item-section>
                <q-item-section>Aumente a produtividade da sua equipa em campo.</q-item-section>
              </q-item>
              <q-item>
                <q-item-section avatar>
                  <q-icon color="white" name="check_circle" />
                </q-item-section>
                <q-item-section>Tome decisões mais inteligentes com dados em tempo real.</q-item-section>
              </q-item>
            </q-list>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar, QStepper } from 'quasar';
import { api } from 'boot/axios';
import axios from 'axios';
import type { UserRegister, UserSector } from 'src/models/auth-models';

const router = useRouter();
const $q = useQuasar();
const isLoading = ref(false);

const step = ref(1);
const stepper = ref<QStepper | null>(null);

const formData = ref<UserRegister>({
  organization_name: '',
  sector: null,
  full_name: '',
  email: '',
  password: '',
});

const sectorOptions: { label: string, value: UserSector }[] = [
  { label: 'Agronegócio', value: 'agronegocio' },
  { label: 'Construção Civil', value: 'construcao_civil' },
  { label: 'Prestadores de Serviço', value: 'servicos' },
  { label: 'Fretes', value: 'frete' },
];

const sectorIcon = computed(() => {
  switch (formData.value.sector) {
    case 'agronegocio': return 'agriculture';
    case 'construcao_civil': return 'engineering';
    case 'servicos': return 'people';
    case 'frete': return 'local_shipping';
    default: return 'category';
  }
});

async function onSubmit() {
  isLoading.value = true;
  try {
    await api.post('/login/register', formData.value);
    
    $q.notify({
      type: 'positive',
      message: 'Conta criada com sucesso! Por favor, faça o login para continuar.',
      timeout: 5000
    });
    
    await router.push('/auth/login');

  } catch (error) {
    let errorMessage = 'Erro ao criar conta. Tente novamente.';
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      errorMessage = error.response.data.detail as string;
    }
    $q.notify({ type: 'negative', message: errorMessage });
  } finally {
    isLoading.value = false;
  }
}
</script>

<style lang="scss" scoped>
.form-panel {
  background-color: #050a14; // Fundo escuro sólido
}

.register-card {
  width: 500px;
  max-width: 90vw;
  // EFEITO DE VIDRO (GLASSMORPHISM)
  background: rgba(18, 23, 38, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.transparent-stepper {
  background-color: transparent !important;
}

// Estilos para o painel visual direito (mantidos)
.register-visual-container {
  position: relative;
  display: flex;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 2;
    transition: background-color 0.4s ease;
  }

  &:hover::before {
    background-color: rgba(0, 0, 0, 0.7);
  }
}

.image-strip {
  flex: 1;
  height: 100%;
  background-size: cover;
  background-position: center;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  filter: grayscale(50%);
}

.register-visual-container:hover .image-strip {
  filter: grayscale(100%);
}

.image-strip:hover {
  flex: 2;
  filter: grayscale(0%);
}

.visual-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 500px;
  z-index: 3;
  text-align: center;
  animation: fadeIn 1s ease-out;
}

.benefits-list {
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  border-radius: 8px;
  margin-top: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.security-seals {
  display: flex;
  justify-content: space-around;
  color: $positive;
  font-size: 0.8rem;
  font-weight: 500;
  opacity: 0.9;
  padding: 0 1rem;
}
.seal-item {
  display: flex;
  align-items: baseline; // Alinhamento corrigido
  gap: 8px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -40%); }
  to { opacity: 1; transform: translate(-50%, -50%); }
}
</style>

