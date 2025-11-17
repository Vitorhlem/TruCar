<template>
  <q-card class="dashboard-card">

    <template v-if="!isDemo">
      <q-card-section>
        <div class="text-h6">{{ title }}</div>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <slot />
      </q-card-section>
    </template>
    

    <template v-else>
      <div class="premium-placeholder column flex-center full-height">
        <q-icon :name="icon" color="amber" size="60px" />
        <div class="text-h6 q-mt-sm">{{ title }}</div>
        <div class="text-body2 text-center q-mt-xs text-grey-8">
          {{ description }}<br/>Funcionalidade exclusiva do plano completo.
        </div>
        <q-btn
          @click="showUpgradeDialog"
          color="primary"
          label="Saber Mais"
          unelevated
          dense
          class="q-mt-md"
        />
      </div>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth-store';

defineProps<{
  title: string;
  icon: string;
  description: string;
}>();

const $q = useQuasar();
const authStore = useAuthStore();

const isDemo = computed(() => authStore.isDemo);

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para aceder a esta e outras funcionalidades premium, entre em contato com nossa equipe comercial.',
    ok: { label: 'Entendido', color: 'primary', unelevated: true },
    persistent: false
  });
}
</script>

<style scoped lang="scss">
.dashboard-card {
  border-radius: $generic-border-radius;
  box-shadow: none;
  border: 1px solid $grey-3;
  transition: all 0.2s ease-in-out;
  
  .body--dark & {
    border-color: $grey-8;
  }
}

.premium-placeholder {
  min-height: 382px;
  background-color: rgba($grey-5, 0.1);
  border: 1px dashed $grey-7;
  color: $grey-5;

  .body--dark & {
    background-color: rgba($grey-8, 0.2);
    border-color: $grey-7;
    color: $grey-5;
  }
}
</style>