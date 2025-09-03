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
                <q-input
                  outlined
                  v-model="passwordForm.current_password"
                  type="password"
                  label="Senha Atual *"
                  lazy-rules
                  :rules="[val => !!val || 'Campo obrigatório']"
                />
                <q-input
                  outlined
                  v-model="passwordForm.new_password"
                  type="password"
                  label="Nova Senha *"
                  lazy-rules
                  :rules="[val => !!val || 'Campo obrigatório']"
                />
                <q-input
                  outlined
                  v-model="passwordForm.confirm_password"
                  type="password"
                  label="Confirmar Nova Senha *"
                  lazy-rules
                  :rules="[
                    val => !!val || 'Campo obrigatório',
                    val => val === passwordForm.new_password || 'As senhas não correspondem'
                  ]"
                />
                <div class="row justify-end">
                  <q-btn
                    type="submit"
                    label="Salvar Nova Senha"
                    color="primary"
                    unelevated
                    :loading="isSubmitting"
                  />
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
                    <q-item-label caption>
                      Escolha entre o tema claro, escuro ou o padrão do seu sistema.
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side >
                     <q-btn-toggle
                        v-model="settingsStore.darkMode"
                        @update:model-value="updateDarkMode"
                        push
                        unelevated
                        toggle-color="primary"
                        :options="[
                          {label: 'Claro', value: false},
                          {label: 'Auto', value: 'auto'},
                          {label: 'Escuro', value: true}
                        ]"
                      />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="notifications">
              <div class="text-h6">Notificações</div>
              <q-separator class="q-my-md" />
              <p>Em breve: Opções para configurar as suas preferências de notificação.</p>
            </q-tab-panel>

            <q-tab-panel v-if="authStore.isManager" name="organization">
              <div class="text-h6">Organização</div>
              <q-separator class="q-my-md" />
              <p>Em breve: Opções para gerir a sua faturação e configurar alertas.</p>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { isAxiosError } from 'axios';
import { useAuthStore } from 'stores/auth-store';
import { useSettingsStore } from 'stores/settings-store';
import { api } from 'boot/axios'; // Importamos a API para a chamada

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const $q = useQuasar();
const currentTab = ref('account');

// --- ESTADO E LÓGICA PARA ALTERAÇÃO DE SENHA ---
const isSubmitting = ref(false);
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
});

async function handleChangePassword() {
  isSubmitting.value = true;
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
    // Limpa o formulário após o sucesso
    passwordForm.value.current_password = '';
    passwordForm.value.new_password = '';
    passwordForm.value.confirm_password = '';
  } catch (error) {
    let message = 'Erro ao alterar a senha.';
    if (isAxiosError(error) && error.response?.data?.detail) {
      message = error.response.data.detail as string;
    }
    $q.notify({ type: 'negative', message });
  } finally {
    isSubmitting.value = false;
  }
}
// --- FIM DA LÓGICA DE SENHA ---


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