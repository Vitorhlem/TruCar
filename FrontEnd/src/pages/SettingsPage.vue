<template>
  <q-page padding>
    <h1 class="text-h4 text-weight-bold q-my-md">Configurações</h1>

    <div class="row q-col-gutter-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-list separator>
            <q-item
              v-for="tab in tabs"
              :key="tab.name"
              clickable
              v-ripple
              :active="currentTab === tab.name"
              @click="currentTab = tab.name"
              active-class="bg-blue-1 text-primary"
            >
              <q-item-section avatar>
                <q-icon :name="tab.icon" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ tab.label }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <div class="col-12 col-md-9">
        <q-card flat bordered>
          <q-tab-panels v-model="currentTab" animated>
            <q-tab-panel name="account">
              <div class="text-h6">Minha Conta</div>
              <q-separator class="q-my-md" />
              <q-form @submit.prevent="handleChangePassword" class="q-gutter-y-md" style="max-width: 400px">
                <div class="text-subtitle1 text-weight-medium">Alterar Senha</div>
                <q-input outlined v-model="passwordForm.current_password" type="password" label="Senha Atual *" lazy-rules :rules="[val => !!val || 'Campo obrigatório']"/>
                <q-input outlined v-model="passwordForm.new_password" type="password" label="Nova Senha *" lazy-rules :rules="[val => !!val || 'Campo obrigatório']"/>
                <q-input outlined v-model="passwordForm.confirm_password" type="password" label="Confirmar Nova Senha *" lazy-rules :rules="[val => !!val || 'Campo obrigatório', val => val === passwordForm.new_password || 'As senhas não correspondem']"/>
                <div class="row justify-end">
                  <q-btn type="submit" label="Salvar Nova Senha" color="primary" unelevated :loading="isSubmittingPassword"/>
                </div>
              </q-form>
            </q-tab-panel>

            <q-tab-panel name="appearance">
              <div class="text-h6 q-mb-md">Aparência</div>
              <q-list bordered separator padding>
                <q-item-label header>Tema da Aplicação</q-item-label>
                <q-item tag="label" v-ripple>
                  <q-item-section>
                    <q-item-label>Modo Escuro</q-item-label>
                    <q-item-label caption>Escolha entre o tema claro, escuro ou o padrão do seu sistema.</q-item-label>
                  </q-item-section>
                  <q-item-section side >
                     <q-btn-toggle v-model="settingsStore.darkMode" @update:model-value="updateDarkMode" push unelevated toggle-color="primary" :options="[{label: 'Claro', value: false}, {label: 'Auto', value: 'auto'}, {label: 'Escuro', value: true}]"/>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="notifications">
              <div class="text-h6 q-mb-md">Preferências de Notificação</div>
              <q-list bordered separator padding>
                <q-item-label header>Canais de Comunicação</q-item-label>
                <q-item tag="label" v-ripple>
                  <q-item-section>
                    <q-item-label>Notificações na Aplicação</q-item-label>
                    <q-item-label caption>Receber alertas através do ícone de sino.</q-item-label>
                  </q-item-section>
                  <q-item-section side top>
                    <q-toggle v-model="notificationPrefs.notify_in_app" color="primary" />
                  </q-item-section>
                </q-item>
                <q-item tag="label" v-ripple>
                  <q-item-section>
                    <q-item-label>Notificações por E-mail</q-item-label>
                    <q-item-label caption>Receber e-mails sobre atividades importantes.</q-item-label>
                  </q-item-section>
                  <q-item-section side top>
                    <q-toggle v-model="notificationPrefs.notify_by_email" color="primary" />
                  </q-item-section>
                </q-item>
                <q-slide-transition>
                  <div v-if="notificationPrefs.notify_by_email">
                    <q-item class="q-px-md q-pt-md">
                      <q-input
                        v-model="notificationPrefs.notification_email"
                        outlined
                        dense
                        label="E-mail para notificações"
                        class="full-width"
                        hint="Deixe em branco para usar o seu e-mail de login."
                      >
                        <template v-slot:prepend><q-icon name="email" /></template>
                      </q-input>
                    </q-item>
                  </div>
                </q-slide-transition>
              </q-list>
            </q-tab-panel>

            <q-tab-panel v-if="authStore.isManager" name="organization">
              <div class="text-h6">Organização</div>
              <q-separator class="q-my-md" />
              <q-list bordered separator padding>
                <q-item-label header>Plano e Faturação</q-item-label>
                <q-item>
                  <q-item-section avatar><q-icon name="workspace_premium" /></q-item-section>
                  <q-item-section>
                    <q-item-label>Plano Atual</q-item-label>
                    <q-item-label caption>
                      <q-chip
                        dense
                        :color="isDemo ? 'amber' : 'positive'"
                        text-color="white"
                        :label="isDemo ? 'Demonstração' : 'Ativo'"
                      />
                    </q-item-label>
                  </q-item-section>
                   <q-item-section side>
                    <q-btn
                      v-if="isDemo"
                      @click="showUpgradeDialog"
                      color="primary"
                      label="Fazer Upgrade"
                      unelevated
                      dense
                    />
                  </q-item-section>
                </q-item>
                <q-item>
                   <q-item-section avatar><q-icon name="credit_card" /></q-item-section>
                   <q-item-section>
                    <q-item-label>Faturação</q-item-label>
                    <q-item-label caption>Para alterar o seu plano ou dados de faturação, por favor, contacte o nosso suporte.</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { isAxiosError } from 'axios';
import { useAuthStore } from 'stores/auth-store';
import { useSettingsStore } from 'stores/settings-store';
import { api } from 'boot/axios';

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const $q = useQuasar();
const currentTab = ref('account');

const isSubmittingPassword = ref(false);
const passwordForm = ref({ current_password: '', new_password: '', confirm_password: '' });

// --- LÓGICA DE DEMO ADICIONADA ---
const isDemo = computed(() => authStore.isDemo);

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para aceder ao histórico completo e outras funcionalidades premium, entre em contato com nossa equipe comercial.',
    ok: { label: 'Entendido', color: 'primary', unelevated: true },
    persistent: true
  });
}
// --- FIM DA ADIÇÃO ---

const notificationPrefs = ref({
  notify_in_app: authStore.user?.notify_in_app ?? true,
  notify_by_email: authStore.user?.notify_by_email ?? true,
  notification_email: authStore.user?.notification_email || authStore.user?.email || '',
});

let debounceTimer: number;
watch(notificationPrefs, (newPrefs) => {
  clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(() => {
    void authStore.updateMyPreferences(newPrefs);
  }, 1500);
}, { deep: true });


async function handleChangePassword() {
  isSubmittingPassword.value = true;
  try {
    const payload = {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
    };
    await api.put('/users/me/password', payload);
    $q.notify({
      type: 'positive',
      message: 'Senha alterada com sucesso!'
    });
    const form = passwordForm.value;
    form.current_password = '';
    form.new_password = '';
    form.confirm_password = '';
  } catch (error) {
    let message = 'Erro ao alterar a senha.';
    if (isAxiosError(error) && error.response?.data?.detail) {
      message = error.response.data.detail as string;
    }
    $q.notify({ type: 'negative', message });
  } finally {
    isSubmittingPassword.value = false;
  }
}

const tabs = computed(() => {
  const allTabs = [
    { name: 'account', label: 'Minha Conta', icon: 'account_circle' },
    { name: 'appearance', label: 'Aparência', icon: 'visibility' },
    { name: 'notifications', label: 'Notificações', icon: 'notifications' },
    { name: 'organization', label: 'Organização', icon: 'business', managerOnly: true },
  ];

  if (authStore.isManager) {
    return allTabs;
  }
  return allTabs.filter(tab => !tab.managerOnly);
});

function updateDarkMode(value: boolean | 'auto') {
  settingsStore.setDarkMode(value);
}
</script>