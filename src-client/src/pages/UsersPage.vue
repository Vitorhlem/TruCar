<template>
  <q-page padding>
    
    <div v-if="isDemo" class="q-mb-lg animate-fade">
      <div class="row">
        <div class="col-12">
          <q-card flat bordered class="">
            <q-card-section>
              <div class="row items-center justify-between no-wrap">
                <div class="col">
                  <div class="text-subtitle2 text-uppercase text-grey-8">Limite de Motoristas</div>
                  <div class="text-h4 text-primary text-weight-bold q-mt-sm">
                    {{ demoUsageCount }} <span class="text-h6 text-grey-6">/ {{ demoUsageLimitLabel }}</span>
                  </div>
                  <div class="text-caption text-grey-7 q-mt-sm">
                    <q-icon name="info" />
                    Você cadastrou {{ usagePercentage }}% dos motoristas permitidos no plano Demo.
                  </div>
                </div>
                <div class="col-auto q-ml-md">
                  <q-circular-progress
                    show-value
                    font-size="16px"
                    :value="usagePercentage"
                    size="70px"
                    :thickness="0.22"
                    :color="usageColor"
                    track-color="grey-3"
                  >
                    {{ usagePercentage }}%
                  </q-circular-progress>
                </div>
              </div>
              <q-linear-progress :value="usagePercentage / 100" class="q-mt-md" :color="usageColor" rounded />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gestão de Usuários</h1>
      
      <div class="d-inline-block relative-position">
        <q-btn 
          @click="openCreateDialog" 
          color="primary" 
          icon="add" 
          label="Adicionar Usuário" 
          unelevated 
          :disable="isDriverLimitReached"
        />
        
        <q-tooltip 
          v-if="isDriverLimitReached" 
          class="bg-negative text-body2 shadow-4" 
          anchor="bottom middle" 
          self="top middle"
          :offset="[10, 10]"
        >
          <div class="row items-center no-wrap">
              <q-icon name="lock" size="sm" class="q-mr-sm" />
              <div>
                  <div class="text-weight-bold">Limite Atingido</div>
                  <div class="text-caption">O plano Demo permite até {{ demoUsageLimitLabel }} motoristas.</div>
                  <div class="text-caption q-mt-xs text-yellow-2 cursor-pointer" @click="showComparisonDialog = true">Clique para saber mais</div>
              </div>
          </div>
        </q-tooltip>
      </div>
    </div>

    <q-card flat bordered>
      <q-table
        @row-click="goToUserDetails"
        class="cursor-pointer"
        :rows="userStore.users"
        :columns="columns"
        row-key="id"
        :loading="userStore.isLoading"
        no-data-label="Nenhum usuário cadastrado"
      >
        <template v-slot:body-cell-is_active="props">
          <q-td :props="props">
            <q-badge :color="props.value ? 'positive' : 'grey-7'" :label="props.value ? 'Ativo' : 'Inativo'" />
          </q-td>
        </template>
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
              <q-btn @click.stop="openEditDialog(props.row)" flat round dense icon="edit" class="q-mr-sm" />
            <q-btn @click.stop="promptToDelete(props.row)" flat round dense icon="delete" color="negative" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 700px; max-width: 95vw;">
        <q-card-section class="bg-primary text-white q-py-lg">
          <div class="text-h5 text-weight-bold text-center">Escale sua Equipe</div>
          <div class="text-subtitle1 text-center text-blue-2">Veja as vantagens do upgrade</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat separator="horizontal">
            <thead>
              <tr class="bg-grey-1 text-uppercase text-grey-7">
                <th class="text-left q-pa-md">Funcionalidade</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="engineering" color="grey-6" size="xs" /> Motoristas</td>
                <td class="text-center bg-amber-1 text-amber-10">Até {{ demoUsageLimitLabel }}</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="manage_accounts" color="grey-6" size="xs" /> Gestores</td>
                <td class="text-center bg-amber-1 text-amber-10">1 (Você)</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Múltiplos</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="analytics" color="grey-6" size="xs" /> Relatórios de Equipe</td>
                <td class="text-center bg-amber-1 text-amber-10">Básico</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Avançado</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg bg-grey-1">
          <div class="text-center full-width">
            <div class="text-grey-7 q-mb-md">Precisa cadastrar mais colaboradores?</div>
            <q-btn color="primary" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width" />
            <q-btn flat color="grey-7" label="Continuar no Demo" class="q-mt-sm" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isFormDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;" :dark="$q.dark.isActive">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Usuário' : 'Novo Usuário' }}</div>
        </q-card-section>

        <q-form @submit.prevent="onFormSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="formData.full_name" label="Nome Completo *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.email" type="email" label="E-mail *" :rules="[val => !!val || 'Campo obrigatório']" />
            
            <q-input outlined v-model="formData.employee_id" label="ID de Funcionário" hint="Ex: TRC-a1b2c3d4" />
            
            <q-input outlined v-model="formData.avatar_url" label="URL da Foto do Perfil" />
            
            <q-select
              outlined
              v-model="formData.role"
              :options="roleOptions"
              label="Função *"
              emit-value
              map-options
              :disable="isRoleSelectorDisabled"
            >
              <template v-if="isRoleSelectorDisabled" v-slot:append>
                <q-icon name="admin_panel_settings" color="grey-7">
                  <q-tooltip>Apenas Super Admins podem alterar papéis.</q-tooltip>
                </q-icon>
              </template>
            </q-select>

            <q-input outlined v-model="formData.password" type="password" :label="isEditing ? 'Nova Senha (deixe em branco para não alterar)' : 'Senha *'" :rules="isEditing ? [] : [val => !!val || 'Campo obrigatório']" />
            <q-toggle v-if="isEditing" v-model="formData.is_active" label="Usuário Ativo" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { useUserStore } from 'stores/user-store';
import { useAuthStore } from 'stores/auth-store';
import { useDemoStore } from 'stores/demo-store';
import { useRouter } from 'vue-router';
import { isAxiosError } from 'axios';
import type { User } from 'src/models/auth-models';
import type { UserCreate, UserUpdate } from 'src/models/user-models';

const demoStore = useDemoStore();
const $q = useQuasar();
const userStore = useUserStore();
const authStore = useAuthStore();
const router = useRouter();
const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingUserId = ref<number | null>(null);

const isEditing = computed(() => editingUserId.value !== null);
const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

// --- LÓGICA DEMO E LIMITES ---
const showComparisonDialog = ref(false);

const demoUsageCount = computed(() => demoStore.stats?.driver_count ?? 0);
const demoUsageLimit = computed(() => authStore.user?.organization?.driver_limit ?? 3);
const demoUsageLimitLabel = computed(() => {
    const limit = authStore.user?.organization?.driver_limit;
    return (limit === undefined || limit === null || limit < 0) ? 'Ilimitado' : limit.toString();
});

const isDriverLimitReached = computed(() => {
  if (!isDemo.value) return false;
  const limit = authStore.user?.organization?.driver_limit;
  if (limit === undefined || limit === null || limit < 0) return false;
  return demoUsageCount.value >= limit;
});

const usagePercentage = computed(() => {
  if (!isDemo.value || demoUsageLimit.value <= 0) return 0;
  const pct = Math.round((demoUsageCount.value / demoUsageLimit.value) * 100);
  return Math.min(pct, 100);
});

const usageColor = computed(() => {
  if (usagePercentage.value >= 100) return 'negative';
  if (usagePercentage.value >= 80) return 'warning';
  return 'primary';
});

const roleOptions = [
  { label: 'Cliente Ativo (Gestor)', value: 'cliente_ativo' },
  { label: 'Cliente Demo (Gestor Limitado)', value: 'cliente_demo' },
  { label: 'Motorista', value: 'driver' }
];

const formData = ref<Partial<UserCreate & UserUpdate>>({});

const isRoleSelectorDisabled = computed(() => {
  return !authStore.isSuperuser;
});

const columns: QTableColumn[] = [
  { name: 'employee_id', label: 'ID Funcionário', field: 'employee_id', align: 'left', sortable: true },
  { name: 'full_name', label: 'Nome Completo', field: 'full_name', align: 'left', sortable: true },
  { name: 'email', label: 'E-mail', field: 'email', align: 'left', sortable: true },
  { name: 'role', label: 'Função', field: 'role', align: 'center', sortable: true, format: (val) => roleOptions.find(r => r.value === val)?.label || val },
  { name: 'is_active', label: 'Status', field: 'is_active', align: 'center', format: (val) => val ? 'Ativo' : 'Inativo' },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

function goToUserDetails(evt: Event, row: User) {
  void router.push({ name: 'user-stats', params: { id: row.id } });
}

function resetForm() {
  editingUserId.value = null;
  formData.value = { full_name: '', email: '', role: 'driver', password: '', is_active: true, employee_id: '' };
}

function openCreateDialog() {
  if (isDriverLimitReached.value && formData.value.role === 'driver') {
    showComparisonDialog.value = true; // Abre o modal bonito ao invés do alerta simples
    return;
  }
  resetForm();
  isFormDialogOpen.value = true;
}

function openEditDialog(user: User) {
  resetForm();
  editingUserId.value = user.id;
  formData.value = { 
    ...user, 
    avatar_url: user.avatar_url || '', 
    password: '' 
  };
  isFormDialogOpen.value = true;
}

async function onFormSubmit() {
  isSubmitting.value = true;
  try {
    const payload = { ...formData.value };

    if (
      !isEditing.value && 
      payload.role === 'driver' && 
      isDriverLimitReached.value
    ) {
      showComparisonDialog.value = true;
      isSubmitting.value = false;
      return;
    }

    if (isEditing.value && !payload.password) {
      delete payload.password;
    }

    if (isEditing.value && editingUserId.value) {
      await userStore.updateUser(editingUserId.value, payload as UserUpdate);
    } else {
      await userStore.addNewUser(payload as UserCreate);
      if (authStore.isDemo) {
        void demoStore.fetchDemoStats(true); // Atualização forçada dos stats
      }
    }
    isFormDialogOpen.value = false;
  } catch (error) {
    let message = 'Erro ao salvar o usuário.';
    if (isAxiosError(error) && error.response?.data?.detail) {
      message = error.response.data.detail as string;
    }
    $q.notify({ type: 'negative', message });
  } finally {
    isSubmitting.value = false;
  }
}

function promptToDelete(user: User) {
  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja excluir o usuário ${user.full_name}? Esta ação não pode ser desfeita.`,
    cancel: { label: 'Cancelar', flat: true },
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
    persistent: false,
}).onOk(() => {
  void (async () => {
    await vehicleStore.deleteVehicle(vehicle.id, {
      page: pagination.value.page, rowsPerPage: pagination.value.rowsPerPage, search: searchTerm.value,
    });
    if (authStore.isDemo) { await demoStore.fetchDemoStats(true); }
  })();
});
}

onMounted(async () => {
  await userStore.fetchAllUsers();
  if (authStore.isDemo) {
    void demoStore.fetchDemoStats();
  }
});
</script>