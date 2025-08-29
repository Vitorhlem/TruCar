<template>
  <q-card flat bordered class="freight-card">
    <q-card-section>
      <div class="text-caption text-grey-7">Cliente: {{ order.client.name }}</div>
      <div class="text-body1 text-weight-medium q-my-xs">{{ order.description || 'Ordem de Frete' }}</div>

      <div class="q-mt-sm q-gutter-y-xs">
        <div v-if="order.driver" class="flex items-center text-caption">
          <q-icon name="person" class="q-mr-xs" /> {{ order.driver.full_name }}
        </div>
        <div v-if="order.vehicle" class="flex items-center text-caption">
          <q-icon name="local_shipping" class="q-mr-xs" /> {{ order.vehicle.brand }} {{ order.vehicle.model }}
        </div>
      </div>
    </q-card-section>
    <q-separator />
    <q-card-section class="q-py-xs">
      <div class="text-caption text-grey-8">
        {{ order.stop_points.length }} {{ order.stop_points.length > 1 ? 'paradas' : 'parada' }}
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import type { FreightOrder } from 'src/models/freight-order-models';

defineProps<{
  order: FreightOrder;
}>();
</script>

<style scoped>
.freight-card {
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.freight-card:hover {
  border-color: var(--q-primary);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
</style>