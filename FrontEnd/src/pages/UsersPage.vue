<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Gestão de Usuários</h1>
      <q-btn @click="openCreateDialog" color="primary" icon="add" label="Adicionar Usuário" unelevated />
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

    <q-dialog v-model="isFormDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;" :dark="$q.dark.isActive">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Usuário' : 'Novo Usuário' }}</div>
        </q-card-section>

        <q-form @submit.prevent="onFormSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="formData.full_name" label="Nome Completo *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.email" type="email" label="E-mail *" :rules="[val => !!val || 'Campo obrigatório']" />
            
            <!-- CAMPO EMPLOYEE_ID ADICIONADO AO FORMULÁRIO -->
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
import { useRouter } from 'vue-router';
import { isAxiosError } from 'axios';
import type { User } from 'src/models/auth-models';
import type { UserCreate, UserUpdate } from 'src/models/user-models';


const $q = useQuasar();
const userStore = useUserStore();
const authStore = useAuthStore();
const router = useRouter();
const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingUserId = ref<number | null>(null);

const isEditing = computed(() => editingUserId.value !== null);

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
  // --- COLUNA EMPLOYEE_ID ADICIONADA À TABELA ---
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
  resetForm();
  isFormDialogOpen.value = true;
}

function openEditDialog(user: User) {
  resetForm();
  editingUserId.value = user.id;
  formData.value = { ...user, password: '' };
  isFormDialogOpen.value = true;
}

async function onFormSubmit() {
  isSubmitting.value = true;
  try {
    const payload = { ...formData.value };
    if (isEditing.value && !payload.password) {
      delete payload.password;
    }

    if (isEditing.value && editingUserId.value) {
      await userStore.updateUser(editingUserId.value, payload as UserUpdate);
    } else {
      await userStore.addNewUser(payload as UserCreate);
    }
    isFormDialogOpen.value = false;
    $q.notify({ type: 'positive', message: 'Usuário salvo com sucesso!' });
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
    persistent: true,
  }).onOk(() => {
    void userStore.deleteUser(user.id);
  });
}

onMounted(async () => {
  await userStore.fetchAllUsers();
});
</script>
