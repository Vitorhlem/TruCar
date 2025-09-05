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
        <div class="text-grey-8">{{ label }}</div>
        <div v-if="!loading" class="text-h4 text-weight-bolder">{{ value }}</div>
        <q-skeleton v-else type="text" width="50px" class="text-h4" />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const props = defineProps<{
  label: string;
  value: string | number;
  icon: string;
  color: string;
  loading: boolean;
  to?: string; // <-- Propriedade opcional para o link
}>();

const router = useRouter();

function handleClick() {
  if (props.to) {
    void router.push(props.to);
  }
}
</script>

<style scoped lang="scss">
.stat-card {
  border-radius: $generic-border-radius;
  box-shadow: none;
  border: 1px solid $grey-3;
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