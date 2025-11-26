<template>
  <q-page padding class="">
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <h1 class="text-h4 text-weight-bold text-primary q-my-none">Configurações</h1>
        <div class="text-caption text-grey-7">Gerencie suas preferências e dados do sistema</div>
      </div>
    </div>

    <div class="row q-col-gutter-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered class=" rounded-borders">
          <q-list separator class="text-grey-8">
            <q-item
              v-for="tab in visibleTabs"
              :key="tab.name"
              clickable
              v-ripple
              :active="currentTab === tab.name"
              @click="currentTab = tab.name"
              active-class="bg-primary text-white"
              class="q-py-md transition-generic"
            >
              <q-item-section avatar>
                <q-icon :name="tab.icon" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-medium">{{ tab.label }}</q-item-label>
                <q-item-label caption :class="currentTab === tab.name ? 'text-blue-2' : 'text-grey-6'">
                  {{ tab.caption }}
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <div class="col-12 col-md-9">
        <q-card flat bordered class="fit ">
          <q-tab-panels v-model="currentTab" animated transition-prev="fade" transition-next="fade">
            
            <q-tab-panel name="account" class="q-pa-lg">
              <div class="text-h6 q-mb-xs">Meu Perfil</div>
              <p class="text-grey-6 q-mb-lg">Gerencie suas informações pessoais e segurança.</p>
              
              <div class="row q-col-gutter-xl">
                <div class="col-12 col-md-5 text-center">
                  <div class="relative-position inline-block">
                    <q-avatar size="120px" class="shadow-3">
                      <img :src="getAvatarUrl(authStore.user?.avatar_url)">
                    </q-avatar>
                    
                    <input 
                      type="file" 
                      ref="fileInput" 
                      accept="image/*" 
                      style="display: none" 
                      @change="handleFileUpload"
                    />
                    
                    <q-btn 
                      round 
                      color="primary" 
                      icon="edit" 
                      size="sm" 
                      class="absolute-bottom-right" 
                      style="bottom: 5px; right: 5px"
                      @click="triggerFileInput"
                      :loading="isUploading"
                    >
                      <q-tooltip>Alterar Foto</q-tooltip>
                    </q-btn>
                  </div>
                  <div class="q-mt-md text-h6">{{ authStore.user?.full_name }}</div>
                  <div class="text-grey-6">{{ authStore.user?.role }}</div>
                </div>

                <div class="col-12 col-md-7">
                  <q-form @submit.prevent="handleUpdateProfile" class="q-gutter-y-md">
                    <q-input outlined v-model="profileForm.full_name" label="Nome Completo" dense />
                    <q-input outlined v-model="profileForm.email" label="E-mail" dense disable hint="Para alterar o e-mail, contate o suporte." />
                    <q-input outlined v-model="profileForm.phone" label="Telefone / WhatsApp" mask="(##) #####-####" dense />
                    
                    <div class="row justify-end">
                      <q-btn type="submit" label="Salvar Dados" color="primary" unelevated :loading="isUpdatingProfile" />
                    </div>
                  </q-form>
                </div>
              </div>

              <q-separator class="q-my-xl" />

              <div class="text-h6 q-mb-md text-negative">Segurança</div>
              <q-form @submit.prevent="handleChangePassword" class="row q-col-gutter-md items-start" style="max-width: 800px">
                <div class="col-12 col-md-4">
                  <q-input 
                    outlined 
                    v-model="passwordForm.current_password" 
                    type="password" 
                    label="Senha Atual" 
                    dense 
                    :rules="[val => !!val || 'Obrigatório']"
                  />
                </div>
                <div class="col-12 col-md-4">
                  <q-input 
                    outlined 
                    v-model="passwordForm.new_password" 
                    type="password" 
                    label="Nova Senha" 
                    dense 
                    :rules="[val => !!val || 'Obrigatório', val => val.length >= 6 || 'Mínimo 6 caracteres']"
                  />
                </div>
                <div class="col-12 col-md-4">
                  <q-input 
                    outlined 
                    v-model="passwordForm.confirm_password" 
                    type="password" 
                    label="Confirmar Nova Senha" 
                    dense 
                    :rules="[
                      val => !!val || 'Obrigatório',
                      val => val === passwordForm.new_password || 'As senhas não conferem'
                    ]"
                  />
                </div>
                <div class="col-2.5 text-right">
                  <q-btn type="submit" label="Alterar Senha" outline color="negative" :loading="isSubmittingPassword" />
                </div>
              </q-form>
            </q-tab-panel>

            <q-tab-panel name="interface" class="q-pa-lg">
              <div class="text-h6 q-mb-xs">Interface & Sistema</div>
              <p class="text-grey-6 q-mb-lg">Personalize a aparência e o vocabulário do sistema.</p>

              <div class="row q-col-gutter-md">


                <div class="col-12 q-mt-md">
                  <q-list bordered class="rounded-borders">
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="dark_mode" color="grey-7" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Tema Escuro</q-item-label>
                        <q-item-label caption>Alternar entre modo claro e escuro.</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn-toggle
                          v-model="settingsStore.darkMode"
                          @update:model-value="updateDarkMode"
                          push unelevated toggle-color="primary"
                          :options="[
                            {icon: 'light_mode', value: false},
                            {icon: 'brightness_auto', value: 'auto'},
                            {icon: 'dark_mode', value: true}
                          ]"
                        />
                      </q-item-section>
                    </q-item>
                    
                    <q-separator />

                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="language" color="grey-7" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Idioma</q-item-label>
                        <q-item-label caption>Português (Brasil) é o padrão.</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-badge color="grey-4" text-color="grey-8" label="Fixo: PT-BR" />
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </div>
            </q-tab-panel>

            <q-tab-panel name="notifications" class="q-pa-lg">
              <div class="text-h6 q-mb-xs">Notificações</div>
              <p class="text-grey-6 q-mb-lg">Escolha como você quer ser alertado.</p>

              <q-list bordered separator class="rounded-borders">
                <q-item-label header class="">Canais Gerais</q-item-label>
                
                <q-item tag="label" v-ripple>
                  <q-item-section avatar><q-icon name="notifications_active" color="orange" /></q-item-section>
                  <q-item-section>
                    <q-item-label>Alertas no Painel</q-item-label>
                    <q-item-label caption>Receber alertas no ícone de sino dentro do sistema.</q-item-label>
                  </q-item-section>
                  <q-item-section side><q-toggle v-model="notificationPrefs.notify_in_app" color="primary" /></q-item-section>
                </q-item>

                <q-item tag="label" v-ripple>
                  <q-item-section avatar><q-icon name="mail" color="blue" /></q-item-section>
                  <q-item-section>
                    <q-item-label>Alertas por E-mail</q-item-label>
                    <q-item-label caption>Receber resumos e alertas críticos no seu e-mail.</q-item-label>
                  </q-item-section>
                  <q-item-section side><q-toggle v-model="notificationPrefs.notify_by_email" color="primary" /></q-item-section>
                </q-item>

                <q-item v-if="notificationPrefs.notify_by_email" class="">
                  <q-item-section>
                    <q-input
                      v-model="notificationPrefs.notification_email"
                      outlined dense
                      label="E-mail alternativo para alertas"
                      placeholder="Ex: gestao@frota.com"
                      hint="Se vazio, usaremos seu e-mail de login."
                    >
                      <template v-slot:prepend><q-icon name="alternate_email" /></template>
                    </q-input>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="organization" class="q-pa-lg" v-if="authStore.isManager">
              <div class="row items-center justify-between q-mb-md">
                <div>
                  <div class="text-h6">Dados da Organização</div>
                  <p class="text-grey-6">Informações fiscais e de contato da empresa.</p>
                </div>
                <q-btn v-if="isDemo" label="Fazer Upgrade" color="amber-9" icon="star" unelevated @click="showUpgradeDialog" />
              </div>

              <q-form @submit.prevent="handleUpdateOrg" class="q-gutter-y-md">
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-input outlined v-model="orgForm.name" label="Razão Social / Nome Fantasia" :readonly="isDemo" />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-input outlined v-model="orgForm.cnpj" label="CNPJ" mask="##.###.###/####-##" :readonly="isDemo" />
                  </div>
                  <div class="col-12">
                    <q-input outlined v-model="orgForm.address" label="Endereço Completo" :readonly="isDemo" />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-input outlined v-model="orgForm.contact_phone" label="Telefone Comercial" mask="(##) ####-####" :readonly="isDemo" />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-input outlined v-model="orgForm.website" label="Website (Opcional)" :readonly="isDemo" />
                  </div>
                </div>
                <div class="text-right">
                  <q-btn 
                    type="submit" 
                    label="Salvar Dados da Empresa" 
                    color="primary" 
                    unelevated 
                    :loading="isSavingOrg" 
                    :disable="isDemo" 
                  />
                  <q-tooltip v-if="isDemo">Disponível apenas no plano Ativo</q-tooltip>
                </div>
              </q-form>
            </q-tab-panel>

            <q-tab-panel name="integrations" class="q-pa-lg" v-if="authStore.isManager">
              <div class="text-h6 q-mb-xs">Integrações</div>
              <p class="text-grey-6 q-mb-lg">Conecte o TruCar a serviços externos.</p>

              <div class="row q-col-gutter-lg">
                <div class="col-12 col-md-6">
                  <q-card flat bordered class="full-height">
                    <q-card-section>
                      <div class="row items-center no-wrap">
                        <q-avatar color="deep-orange-1" text-color="deep-orange" icon="local_gas_station" />
                        <div class="q-ml-md">
                          <div class="text-subtitle1 text-weight-bold">Cartão de Combustível</div>
                          <div class="text-caption text-grey">Ticket Log, Alelo, Sodexo</div>
                        </div>
                      </div>
                    </q-card-section>
                    <q-separator />
                    <q-card-section>
                      <q-form @submit.prevent="handleUpdateIntegration" class="q-gutter-y-sm">
                        <q-select outlined dense v-model="integrationForm.fuel_provider_name" :options="['Ticket Log', 'Alelo Frota', 'Sodexo Wizeo']" label="Provedor" />
                        <q-input outlined dense v-model="integrationForm.fuel_provider_api_key" label="API Key" type="password" />
                        <q-input outlined dense v-model="integrationForm.fuel_provider_api_secret" label="API Secret" type="password" />
                        <q-btn type="submit" label="Conectar" color="deep-orange" unelevated class="full-width q-mt-sm" :loading="settingsStore.isLoadingFuelSettings" />
                      </q-form>
                    </q-card-section>
                  </q-card>
                </div>

                <div class="col-12 col-md-6">
                  <q-card flat bordered class="full-height ">
                    <q-card-section>
                      <div class="row items-center no-wrap">
                        <q-avatar color="grey-3" text-color="grey-6" icon="satellite_alt" />
                        <div class="q-ml-md">
                          <div class="text-subtitle1 text-weight-bold text-grey-7">Rastreadores & GPS</div>
                          <div class="text-caption text-grey">Omnilink, Sascar, Cobli</div>
                        </div>
                        <q-space />
                        <q-chip dense color="grey-4" label="Em Breve" />
                      </div>
                    </q-card-section>
                    <q-separator />
                    <q-card-section class="text-center q-py-lg">
                      <p class="text-grey-6 text-caption">Importação automática de odômetro e rotas via API de telemetria.</p>
                      <q-btn label="Tenho Interesse" outline color="grey-6" size="sm" />
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </q-tab-panel>

          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, reactive } from 'vue';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth-store';
import { useSettingsStore } from 'stores/settings-store';
import { useUserStore } from 'stores/user-store';
import { api } from 'boot/axios';
import defaultAvatar from 'assets/default-avatar.png';

const $q = useQuasar();
const authStore = useAuthStore();
const settingsStore = useSettingsStore();

const userStore = useUserStore();

const currentTab = ref('account');
const isDemo = computed(() => authStore.isDemo);

// --- FUNÇÃO AUXILIAR PARA CORRIGIR URL DA IMAGEM ---
function getAvatarUrl(url: string | null | undefined): string {
  if (!url) return defaultAvatar; // <--- AQUI ESTÁ A MÁGICA
  if (url.startsWith('http')) return url;
  const backendUrl = 'http://127.0.0.1:8000'; 
  if (url.startsWith('/static') || url.startsWith('/')) {
    return `${backendUrl}${url}`;
  }
  return url;
}
// --- LÓGICA DE UPLOAD DE FOTO ---
const fileInput = ref<HTMLInputElement | null>(null);
const isUploading = ref(false);

function triggerFileInput() {
  fileInput.value?.click();
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    isUploading.value = true;

    try {
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await api.post('/upload-photo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const newAvatarUrl = uploadRes.data.file_url;

      await api.put('/users/me', { avatar_url: newAvatarUrl });
      
      // --- CORREÇÃO CRÍTICA PARA PERSISTÊNCIA ---
      if (authStore.user) {
        authStore.user.avatar_url = newAvatarUrl;
        // Salva manualmente no LocalStorage para garantir que o F5 não limpe
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            const parsed = JSON.parse(storedUser);
            parsed.avatar_url = newAvatarUrl;
            localStorage.setItem('user', JSON.stringify(parsed));
        }
      }
      // ------------------------------------------
      
      $q.notify({ type: 'positive', message: 'Foto atualizada!' });
    } catch (error) {
      console.error(error);
      $q.notify({ type: 'negative', message: 'Erro ao atualizar foto.' });
    } finally {
      isUploading.value = false;
    }
  }
}

// --- PERFIL ---
const profileForm = reactive({
  full_name: authStore.user?.full_name || '',
  email: authStore.user?.email || '',
  phone: authStore.user?.phone || '', // Agora carrega do store se existir
});
const isUpdatingProfile = ref(false);

async function handleUpdateProfile() {
  isUpdatingProfile.value = true;
  try {
    if (authStore.user?.id) {
      await userStore.updateUser(authStore.user.id, { 
          full_name: profileForm.full_name,
          phone: profileForm.phone 
      });
      
      // Atualiza store local
      if (authStore.user) {
          authStore.user.full_name = profileForm.full_name;
          // authStore.user.phone = profileForm.phone; (Se o tipo User tiver phone)
      }
      
      $q.notify({ type: 'positive', message: 'Perfil atualizado com sucesso!' });
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao atualizar perfil.' });
  } finally {
    isUpdatingProfile.value = false;
  }
}

// --- SENHA ---
const passwordForm = ref({ current_password: '', new_password: '', confirm_password: '' });
const isSubmittingPassword = ref(false);

async function handleChangePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    $q.notify({ type: 'warning', message: 'As senhas não conferem.' });
    return;
  }
  isSubmittingPassword.value = true;
  try {
    await api.put('/users/me/password', {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
    });
    $q.notify({ type: 'positive', message: 'Senha alterada!' });
    passwordForm.value = { current_password: '', new_password: '', confirm_password: '' };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) { // Mantendo any aqui conforme sua preferência para simplificar
    const msg = error.response?.data?.detail || 'Erro ao alterar senha.';
    $q.notify({ type: 'negative', message: msg });
  } finally {
    isSubmittingPassword.value = false;
  }
}

// --- INTERFACE ---

function updateDarkMode(val: boolean | 'auto') {
  settingsStore.setDarkMode(val);
}

// --- NOTIFICAÇÕES ---
const notificationPrefs = ref({
  notify_in_app: authStore.user?.notify_in_app ?? true,
  notify_by_email: authStore.user?.notify_by_email ?? true,
  notification_email: authStore.user?.notification_email || '',
});

let debounceTimer: number | undefined;
watch(notificationPrefs, (newVal) => {
  clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(() => {
    void authStore.updateMyPreferences(newVal);
  }, 1000);
}, { deep: true });

// --- ORGANIZAÇÃO ---
const orgForm = reactive({
  name: '', // Inicialize vazio, vamos carregar da API
  cnpj: '',
  address: '',
  contact_phone: '',
  website: ''
});
const isSavingOrg = ref(false); // Estado de carregamento para o botão

async function fetchOrganizationData() {
  if (!authStore.isManager) return;
  
  try {
    const { data } = await api.get('/settings/organization');
    // Preenche o formulário com os dados vindos do backend
    orgForm.name = data.name || '';
    orgForm.cnpj = data.cnpj || '';
    orgForm.address = data.address || '';
    orgForm.contact_phone = data.contact_phone || '';
    orgForm.website = data.website || '';
  } catch (error) {
    console.error('Erro ao buscar dados da organização:', error);
    $q.notify({ type: 'negative', message: 'Falha ao carregar dados da empresa.' });
  }
}

async function handleUpdateOrg() {
  isSavingOrg.value = true;
  try {
    // Envia os dados para o backend
    await api.put('/settings/organization', orgForm);
    
    // Atualiza o nome da organização na store local se tiver mudado
    if (authStore.user && authStore.user.organization) {
      authStore.user.organization.name = orgForm.name;
    }

    $q.notify({ type: 'positive', message: 'Dados da empresa atualizados com sucesso!' });
  } catch (error) {
    console.error(error);
    $q.notify({ type: 'negative', message: 'Erro ao salvar dados da empresa.' });
  } finally {
    isSavingOrg.value = false;
  }
}

function showUpgradeDialog() {
  $q.dialog({
    title: 'Upgrade para Enterprise',
    message: 'Entre em contato com vendas@trucar.com para remover os limites.',
    ok: { label: 'OK', flat: true }
  });
}

// --- INTEGRAÇÕES ---
const integrationForm = ref({
  fuel_provider_name: '',
  fuel_provider_api_key: '',
  fuel_provider_api_secret: '',
});

watch(() => settingsStore.fuelIntegrationSettings, (newSettings) => {
  if (newSettings) {
    integrationForm.value.fuel_provider_name = newSettings.fuel_provider_name || '';
  }
}, { immediate: true });

async function handleUpdateIntegration() {
  await settingsStore.updateFuelIntegrationSettings(integrationForm.value);
}

// --- TABS ---
const visibleTabs = computed(() => {
  const tabs = [
    { name: 'account', label: 'Minha Conta', caption: 'Perfil e Segurança', icon: 'person' },
    { name: 'interface', label: 'Interface', caption: 'Tema e Vocabulário', icon: 'tune' },
    { name: 'notifications', label: 'Notificações', caption: 'Alertas e E-mails', icon: 'notifications' },
  ];
  if (authStore.isManager) {
    tabs.push(
      { name: 'organization', label: 'Organização', caption: 'Dados e Plano', icon: 'business' },
      { name: 'integrations', label: 'Integrações', caption: 'Combustível e GPS', icon: 'hub' }
    );
  }
  return tabs;
});
onMounted(() => {
  if (authStore.isManager) {
    void settingsStore.fetchFuelIntegrationSettings();
    void fetchOrganizationData(); // <--- ADICIONE ESTA CHAMADA
  }
});
</script>

<style lang="scss" scoped>
.border-blue-left {
  border-left: 4px solid var(--q-primary);
}
.transition-generic {
  transition: all 0.3s ease;
}
.opacity-8 { opacity: 0.8; }
.opacity-5 { opacity: 0.5; }
</style>