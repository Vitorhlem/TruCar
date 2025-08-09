<template>
  <q-layout view="lHh Lpr lFf" class="bg-grey-2">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          <q-avatar>
            <q-icon name="directions_car" />
          </q-avatar>
          Frota Ágil
        </q-toolbar-title>

        <div v-if="authStore.user" class="q-mr-md">
          Olá, {{ authStore.user.full_name }}
        </div>
        <q-btn
          @click="handleLogout"
          flat
          round
          dense
          icon="logout"
          aria-label="Sair do Sistema"
        />
      </q-toolbar>
    </q-header>

    

    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
      <q-scroll-area class="fit">
        <q-list padding>
          <q-item-label header class="text-weight-bold text-uppercase">Navegação</q-item-label>
          
          <template v-for="link in menuLinks" :key="link.title">
            <q-item
              v-if="!link.requiresManager || authStore.isManager"
              :to="link.route"
              clickable
              v-ripple
              exact
              class="menu-link"
            >
              <q-item-section avatar>
                <q-icon :name="link.icon" />
              </q-item-section>
              <q-item-section>
                {{ link.title }}
              </q-item-section>
            </q-item>
          </template>

        </q-list>
      </q-scroll-area>
    </q-drawer>

    
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const leftDrawerOpen = ref(true);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

async function handleLogout() {
  authStore.logout();
  await router.push({ name: 'login' });
}

const menuLinks = ref([
  { title: 'Dashboard', icon: 'dashboard', route: { name: 'dashboard' }, requiresManager: false },
  { title: 'Veículos', icon: 'local_shipping', route: { name: 'vehicles' }, requiresManager: false },
  { title: 'Viagens', icon: 'map', route: { name: 'journeys' }, requiresManager: false },
  { title: 'Usuários', icon: 'group', route: { name: 'users' }, requiresManager: true }
]);
</script>

<style lang="scss" scoped>
.q-item.q-router-link--active, .q-item--active {
  background-color: rgba($primary, 0.1);
  color: $primary;
  border-left: 4px solid $primary;
}
.menu-link .q-item__section--avatar {
  color: $grey-7;
}
.q-item.q-router-link--active .q-item__section--avatar {
  color: $primary;
}
</style>