<template>
  <q-card flat class="freight-card" :class="statusClass">
    <q-card-section class="q-pb-xs">
      <div class="row items-center justify-between no-wrap">
        <div class="text-caption  text-weight-bold text-uppercase ellipsis">
          {{ order.client.name }}
        </div>
        <q-badge :color="statusColor" class="q-ml-sm shadow-1">
          #{{ order.id }}
        </q-badge>
      </div>
      
      <div class="text-body2 text-weight-medium q-mt-xs ellipsis-2-lines">
        {{ order.description || 'Frete sem descrição' }}
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section class="q-py-sm">
      <div class="route-preview q-mb-sm">
        <div class="flex items-center no-wrap">
          <q-icon name="trip_origin" size="xs" color="grey-5" class="q-mr-sm" />
          <div class="text-caption  ellipsis">{{ startPoint || 'Origem indefinida' }}</div>
        </div>
        <div class="route-line"></div>
        <div class="flex items-center no-wrap">
          <q-icon name="place" size="xs" color="primary" class="q-mr-sm" />
          <div class="text-caption  ellipsis">{{ endPoint || 'Destino indefinido' }}</div>
        </div>
      </div>

      <div class="row items-center justify-between q-mt-xs">
        <div class="flex items-center q-gutter-x-sm">
          <q-avatar size="24px" :color="order.driver ? 'primary' : 'grey-3'" text-color="white">
            <q-icon :name="order.driver ? 'person' : 'person_off'" size="14px" />
          </q-avatar>
          <q-avatar size="24px" :color="order.vehicle ? 'secondary' : 'grey-3'" text-color="white">
            <q-icon :name="order.vehicle ? 'local_shipping' : 'no_transfer'" size="14px" />
          </q-avatar>
        </div>
        <div class="text-caption text-grey-6">
          {{ order.stop_points.length }} paradas
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { FreightOrder } from 'src/models/freight-order-models';

const props = defineProps<{
  order: FreightOrder;
}>();

// Tenta pegar o primeiro ponto de coleta e o último de entrega
const startPoint = computed(() => {
  const point = props.order.stop_points.find(p => p.type === 'Coleta');
  // Adicionado (point as any)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return point ? (point as any).city || point.address : '---';
});

const endPoint = computed(() => {
  const points = [...props.order.stop_points];
  const delivery = points.reverse().find(p => p.type === 'Entrega');
  // Adicionado (delivery as any)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return delivery ? (delivery as any).city || delivery.address : '---';
});

const statusColor = computed(() => {
  // Adicionado (as string) para permitir 'Cancelada' caso não esteja no type
  switch (props.order.status as string) {
    case 'Pendente': return 'grey';
    case 'Agendada': return 'blue';
    case 'Em Trânsito': return 'orange';
    case 'Entregue': return 'positive';
    case 'Cancelada': return 'negative';
    default: return 'grey';
  }
});

const statusClass = computed(() => {
  return `border-${statusColor.value}`;
});
</script>

<style scoped lang="scss">
.freight-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  border-left-width: 4px;
  border-radius: 8px;
  background: white;

  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }
}

.border-blue-grey { border-left-color: #607d8b; }
.border-primary { border-left-color: var(--q-primary); }
.border-orange { border-left-color: #ff9800; }
.border-positive { border-left-color: var(--q-positive); }
.border-negative { border-left-color: var(--q-negative); }
.border-grey { border-left-color: #9e9e9e; }

.route-preview {
  position: relative;
  .route-line {
    width: 1px;
    height: 10px;
    background: #e0e0e0;
    margin-left: 7px; // Alinha com o centro dos ícones (aprox)
    margin-top: 2px;
    margin-bottom: 2px;
  }
}

// Dark Mode support
body.body--dark .freight-card {
  background: #1d1d1d;
  border-color: rgba(255,255,255,0.05);
}
</style>