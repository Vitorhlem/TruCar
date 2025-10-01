<template>
  <div v-if="layout" class="tire-layout-container">
    <div v-for="(axle, axleIndex) in layout.axles" :key="axleIndex" class="axle">
      <div class="tire-slot" v-for="position in axle.positions" :key="position.code">
        <q-card flat bordered class="tire-card" :class="{ 'empty': !position.tire }">
          <q-card-section class="q-pa-sm text-center">
            <div class="text-caption text-grey-7">{{ position.label }} ({{ position.code }})</div>
            <q-icon name="local_shipping" size="xl" color="grey-4" v-if="!position.tire" />
            <div v-else>
              <q-icon name="album" size="xl" color="dark" />
              <div class="text-caption text-weight-medium q-mt-xs">{{ position.tire.part.brand }}</div>
              <div class="text-caption">{{ position.tire.part.serial_number || position.tire.part.name }}</div>
            </div>
          </q-card-section>
          <q-card-actions class="q-pa-none">
            <q-btn v-if="!position.tire" flat color="positive" icon="add_circle" class="full-width" @click="$emit('install', position.code)">Instalar</q-btn>
            <q-btn v-else flat color="negative" icon="remove_circle" class="full-width" @click="$emit('remove', position.tire)">Remover</q-btn>
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </div>
  <div v-else class="text-center text-grey q-pa-lg">
    Configuração de eixos não definida para este veículo.
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { VehicleTire } from 'src/models/tire-models';

const props = defineProps<{
  axleConfig: string | null;
  tires: VehicleTire[];
}>();

defineEmits(['install', 'remove']);

// Lógica para gerar o layout a partir da configuração de eixos
const layout = computed(() => {
  if (!props.axleConfig) return null;
  const config = axleLayouts[props.axleConfig] || [];
  return {
    axles: config.map(axle => ({
      positions: axle.map(pos => ({
        ...pos,
        tire: props.tires.find(t => t.position_code === pos.code)
      }))
    }))
  };
});

// Mapeamento de configurações de eixos para posições
const axleLayouts: Record<string, { label: string; code: string; }[][]> = {
  '4x2': [
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }]
  ],
  '6x2': [
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }],
    [{ label: 'Eixo 3 - Esq. Int.', code: '3EI' }, { label: 'Eixo 3 - Esq. Ext.', code: '3EE' }, { label: 'Eixo 3 - Dir. Int.', code: '3DI' }, { label: 'Eixo 3 - Dir. Ext.', code: '3DE' }]
  ],
  // Adicione outras configurações conforme necessário
};
</script>

<style scoped lang="scss">
.tire-layout-container {
  padding: 16px;
  border: 1px solid $grey-4;
  border-radius: $generic-border-radius;
  background: $grey-2;
}
.axle {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
  &:last-child {
    margin-bottom: 0;
  }
}
.tire-card {
  width: 150px;
  transition: all 0.3s ease;
  &.empty:hover {
    border-color: $positive;
    box-shadow: 0 0 10px rgba($positive, 0.5);
  }
}
</style>