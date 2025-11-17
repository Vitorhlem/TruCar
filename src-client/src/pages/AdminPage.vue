<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Painel de Super Admin</h1>
    </div>

    <q-card flat bordered>
      <q-tabs
        v-model="tab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="pending_activations" label="Ativações Pendentes" />
        <q-tab name="manage_orgs" label="Gerir Organizações" />
        <q-tab name="manage_users" label="Gerir Utilizadores" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="pending_activations">
          <q-table
            :rows="adminStore.demoUsers"
            :columns="userColumns"
            row-key="id"
            :loading="adminStore.isLoading"
            no-data-label="Nenhum utilizador demo encontrado."
          >
            <template v-slot:top-right>
              <q-btn flat round dense icon="refresh" @click="adminStore.fetchDemoUsers" />
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn @click="promptToActivate(props.row)" color="positive" label="Ativar" unelevated dense class="q-mr-sm" />
                <q-btn @click="promptToImpersonate(props.row)" color="grey-7" icon="visibility" flat round dense>
                  <q-tooltip>Entrar como {{ props.row.full_name }}</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <q-tab-panel name="manage_orgs">
          <q-table
            :rows="adminStore.organizations"
            :columns="orgColumns"
            row-key="id"
            :loading="adminStore.isLoading"
            no-data-label="Nenhuma organização encontrada."
            :filter="orgFilter"
          >
            <template v-slot:top>
              <q-btn-toggle
                v-model="orgFilter"
                toggle-color="primary"
                unelevated
                :options="[
                  {label: 'Todas', value: ''},
                  {label: 'Demos', value: 'cliente_demo'},
                  {label: 'Ativas', value: 'cliente_ativo'}
                ]"
              />
              <q-space />
              <q-btn flat round dense icon="refresh" @click="() => adminStore.fetchOrganizations(orgFilter || null)" />
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn @click="openEditDialog(props.row)" color="primary" label="Editar" unelevated dense />
              </q-td>
            </template>
             <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-chip
                  :color="props.value === 'cliente_ativo' ? 'green' : 'amber'"
                  text-color="white"
                  dense
                  :label="props.value === 'cliente_ativo' ? 'Ativa' : 'Demo'"
                />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <q-tab-panel name="manage_users">
          <q-table
            :rows="adminStore.allUsers"
            :columns="allUsersColumns"
            row-key="id"
            :loading="adminStore.isLoading"
            no-data-label="Nenhum utilizador encontrado."
          >
            <template v-slot:top-right>
              <q-btn flat round dense icon="refresh" @click="adminStore.fetchAllUsers" />
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn
                  @click="promptToImpersonate(props.row)"
                  color="grey-7"
                  icon="visibility"
                  flat round dense
                >
                  <q-tooltip>Entrar como {{ props.row.full_name }}</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>

    <q-dialog v-model="isEditDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-card-section>
          <div class="text-h6">Editar Organização</div>
        </q-card-section>
        <q-form @submit.prevent="handleEditOrg">
          <q-card-section class="q-gutter-y-md">
            <q-input outlined v-model="editOrgForm.name" label="Nome da Empresa *" :rules="[val => !!val || 'Campo obrigatório']" />
            <q-select outlined v-model="editOrgForm.sector" :options="sectorOptions" label="Setor *" emit-value map-options />
            
            <q-separator class="q-mt-md" />
            <div class="text-subtitle2 q-mb-none">Definir Limites (-1 para Ilimitado)</div>
            
            <q-input
              outlined
              v-model.number="editOrgForm.vehicle_limit"
              type="number"
              label="Limite de Veículos"
            />
            <q-input
              outlined
              v-model.number="editOrgForm.driver_limit"
              type="number"
              label="Limite de Motoristas"
            />
            <q-input
              outlined
              v-model.number="editOrgForm.freight_order_limit"
              type="number"
              label="Limite de Ordens de Frete"
            />
            <q-input
              outlined
              v-model.number="editOrgForm.maintenance_limit"
              type="number"
              label="Limite de Manutenções"
            />
            </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar Alterações" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { useAdminStore } from 'stores/admin-store';
import type { User, UserSector } from 'src/models/auth-models';

import type { Organization, OrganizationUpdate } from 'src/models/organization-models'; 

const $q = useQuasar();
const adminStore = useAdminStore();
const tab = ref('pending_activations');
const isEditDialogOpen = ref(false);
const isSubmitting = ref(false);
const editingOrg = ref<Organization | null>(null);
const editOrgForm = ref<Partial<OrganizationUpdate>>({});
const orgFilter = ref('cliente_demo');

const sectorOptions: { label: string, value: UserSector }[] = [
  { label: 'Agronegócio', value: 'agronegocio' },
  { label: 'Construção Civil', value: 'construcao_civil' },
  { label: 'Prestadores de Serviço', value: 'servicos' },
  { label: 'Fretes', value: 'frete' },
];

const userColumns: QTableColumn[] = [
  { name: 'full_name', label: 'Nome do Utilizador', field: 'full_name', align: 'left', sortable: true },
  { name: 'email', label: 'E-mail', field: 'email', align: 'left', sortable: true },

  { name: 'organization', label: 'Empresa', field: (row: User) => row.organization?.name, align: 'left', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

const orgColumns: QTableColumn[] = [
  { name: 'name', label: 'Nome da Empresa', field: 'name', align: 'left', sortable: true },
  { name: 'sector', label: 'Setor', field: 'sector', align: 'center', sortable: true },
  { name: 'status', label: 'Status', field: (row: Organization) => row.users?.find(u => u.role !== 'driver')?.role, align: 'center', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];


const allUsersColumns: QTableColumn[] = [
  { name: 'full_name', label: 'Nome', field: 'full_name', align: 'left', sortable: true },
  { name: 'email', label: 'E-mail', field: 'email', align: 'left', sortable: true },
  { name: 'role', label: 'Papel', field: 'role', align: 'center', sortable: true },

  { name: 'organization', label: 'Empresa', field: (row: User) => row.organization?.name, align: 'left', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'center' },
];


function promptToActivate(user: User) {
  $q.dialog({
    title: 'Confirmar Ativação',

    message: `Tem a certeza que deseja ativar a conta de <strong>${user.full_name}</strong> (${user.organization?.name ?? 'Empresa não definida'})? O papel dele será alterado para CLIENTE_ATIVO.`,
    html: true,
    cancel: { label: 'Cancelar', flat: true },
    ok: { label: 'Sim, Ativar', color: 'positive', unelevated: true },
  }).onOk(() => {
    void adminStore.activateUser(user.id);
  });
}


function promptToImpersonate(user: User) {
  $q.dialog({
    title: 'Login Sombra',
    message: `Tem a certeza que deseja entrar no sistema como <strong>${user.full_name}</strong>? A sua sessão de administrador será guardada e você será redirecionado.`,
    html: true,
    cancel: { label: 'Cancelar', flat: true },
    ok: { label: 'Sim, Entrar', color: 'primary', unelevated: true },
  }).onOk(() => {
    void adminStore.impersonateUser(user);
  });
}


function openEditDialog(org: Organization) {
  editingOrg.value = org;

  editOrgForm.value = { 
    name: org.name, 
    sector: org.sector,
    vehicle_limit: org.vehicle_limit,
    driver_limit: org.driver_limit,
    freight_order_limit: org.freight_order_limit,
    maintenance_limit: org.maintenance_limit
  };

  isEditDialogOpen.value = true;
}

async function handleEditOrg() {
  if (!editingOrg.value) return;
  isSubmitting.value = true;
  try {

    await adminStore.updateOrganization(editingOrg.value.id, editOrgForm.value);
    isEditDialogOpen.value = false;
  } finally {
    isSubmitting.value = false;
  }
}

watch(tab, (newTab) => {
  if (newTab === 'pending_activations') {
    void adminStore.fetchDemoUsers();
  } else if (newTab === 'manage_orgs') {
    void adminStore.fetchOrganizations(orgFilter.value || null);
  } else if (newTab === 'manage_users') {
    void adminStore.fetchAllUsers();
  }
}, { immediate: true });

watch(orgFilter, (newStatus) => {
  if (tab.value === 'manage_orgs') {
    void adminStore.fetchOrganizations(newStatus || null);
  }
});
</script>