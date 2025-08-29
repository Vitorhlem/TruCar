<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Ordens de Frete</h1>
      <!-- Futuramente, um botão para criar um novo frete aqui -->
      <q-btn v-if="authStore.isManager" color="primary" icon="add" label="Nova Ordem de Frete" unelevated />
    </div>

    <!-- AINDA EM DESENVOLVIMENTO -->
    <q-card flat bordered>
      <q-card-section class="text-center q-pa-xl text-grey-7">
        <q-icon name="construction" size="4em" />
        <p class="q-mt-md text-h6">Página de Ordens de Frete</p>
        <p>Esta funcionalidade está em desenvolvimento.</p>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { useAuthStore } from 'stores/auth-store';
const authStore = useAuthStore();
</script>