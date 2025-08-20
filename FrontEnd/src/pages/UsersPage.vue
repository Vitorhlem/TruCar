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
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Usuário' : 'Novo Usuário' }}</div>
        </q-card-section>

        <q-form @submit.prevent="onFormSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="formData.full_name" label="Nome Completo *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.email" type="email" label="E-mail *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-input outlined v-model="formData.avatar_url" label="URL da Foto do Perfil" />
            <q-select outlined v-model="formData.role" :options="roleOptions" label="Função *" emit-value map-options />
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
import { useRouter } from 'vue-router';
import type { User } from 'src/models/auth-models';
import type { UserCreate, UserUpdate } from 'src/models/user-models';


const $q = useQuasar();
const userStore = useUserStore();
const router = useRouter();
const isFormDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingUserId = ref<number | null>(null);

const isEditing = computed(() => editingUserId.value !== null);
const roleOptions = [
  { label: 'Gestor', value: 'manager' },
  { label: 'Motorista', value: 'driver' }
];

const formData = ref<Partial<UserCreate & UserUpdate>>({});

const columns: QTableColumn[] = [
  { name: 'full_name', label: 'Nome Completo', field: 'full_name', align: 'left', sortable: true },
  { name: 'email', label: 'E-mail', field: 'email', align: 'left', sortable: true },
  { name: 'role', label: 'Função', field: 'role', align: 'center' },
  { name: 'is_active', label: 'Status', field: 'is_active', align: 'center' },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];


function goToUserDetails(evt: Event, row: User) {
  void router.push({ name: 'user-stats', params: { id: row.id } });
}

function resetForm() {
  editingUserId.value = null;
  formData.value = { full_name: '', email: '', role: 'driver', password: '', is_active: true };
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
      await userStore.updateUser(editingUserId.value, payload);
    } else {
      await userStore.addNewUser(payload as UserCreate);
    }
    isFormDialogOpen.value = false;
  } catch {
    console.log('O formulário não fecha pois a operação falhou.');
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