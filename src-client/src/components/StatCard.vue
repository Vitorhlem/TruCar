<template>
  <q-card
    class="stat-card"
    :class="{ 'cursor-pointer': !!to }"
    flat
    bordered
    @click="handleClick"
  >
    <q-card-section class="flex items-center no-wrap">
      <q-icon :name="icon" :color="color" size="44px" class="q-mr-md" />
      <div>
        <div class="">{{ label }}</div>
        <div v-if="!loading" class="text-h4 text-weight-bolder">{{ formattedValue }}</div>
        <q-skeleton v-else type="text" width="50px" class="text-h4" />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'; // ADICIONADO
import { useRouter } from 'vue-router';

const props = defineProps<{
  label: string;
  value: string | number;
  icon: string;
  color: string;
  loading: boolean;
  to?: string;
  // --- NOVA PROP ADICIONADA ---
  limit?: number; // Opcional. Se não for passado ou for < 0, será "Ilimitado"
  // --- FIM DA ADIÇÃO ---
}>();

const router = useRouter();

// --- NOVA LÓGICA ADICIONADA ---
const formattedValue = computed(() => {
  // Se o limite não for fornecido ou for -1 (Ilimitado), mostre apenas o valor
  if (props.limit === undefined || props.limit < 0) {
    return props.value;
  }
  // Caso contrário, mostre "valor / limite"
  return `${props.value} / ${props.limit}`;
});
// --- FIM DA ADIÇÃO ---

function handleClick() {
  if (props.to) {
    void router.push(props.to);
  }
}
</script>

<style scoped lang="scss">

.dashboard-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  background: white;
  transition: all 0.2s;

  /* Borda Preta no Modo Claro */
  
  .body--dark & {
    background: #1d1d1d;
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
  }
}

.stat-card {
  border-radius: $generic-border-radius;
  border: 1px solid #000000;
  border: 1px solid $grey-7;
  transition: all 0.2s ease-in-out;
  
  &.cursor-pointer:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.07);
    border-color: $primary;
  }

  .body--dark & {
    border-color: $grey-8;

    &.cursor-pointer:hover {
      border-color: $primary;
    }
  }
}
</style>