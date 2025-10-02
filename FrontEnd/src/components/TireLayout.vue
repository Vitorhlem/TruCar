<template>
  <div v-if="layout" class="tire-layout-container">
    <div v-for="(axle, axleIndex) in layout.axles" :key="axleIndex" class="axle">
      <div class="tire-slot" v-for="position in axle.positions" :key="position.code">
        <q-card flat bordered class="tire-card" :class="[getTireStatusClass(position.tire), { 'empty': !position.tire }]">
          <q-card-section class="q-pa-sm text-center relative-position">
            
            <div class="text-caption text-grey-7">{{ position.label }} ({{ position.code }})</div>

            <div v-if="!position.tire">
                <q-icon name="local_shipping" size="xl" color="grey-4" />
            </div>

            <div v-else>
              <q-icon name="album" size="xl" :class="`text-${getTireStatusColor(position.tire?.status)}`" />
              <div class="text-caption text-weight-medium q-mt-xs">{{ position.tire.part.brand }}</div>
              <div class="text-caption">{{ position.tire.part.serial_number || position.tire.part.name }}</div>
              
              <q-linear-progress :value="position.tire.wearPercentage / 100" :color="getTireStatusColor(position.tire.status)" class="q-mt-xs" rounded />

              <q-icon 
                v-if="position.tire.status !== 'ok'"
                :name="position.tire.status === 'warning' ? 'warning' : 'error'" 
                :color="getTireStatusColor(position.tire.status)"
                class="absolute-top-right q-ma-xs"
                size="sm" 
              />
              
              <q-tooltip anchor="top middle" self="bottom middle">
                <div class="text-caption">
                  <div><strong>Vida Útil:</strong> {{ position.tire.lifespan_km.toLocaleString('pt-BR') }} {{ isAgro ? 'h' : 'km' }}</div>
                  <div v-if="isAgro"><strong>Horas de Uso:</strong> {{ position.tire.horas_de_uso?.toFixed(1) }} h</div>
                  <div v-else><strong>KM Rodados:</strong> {{ position.tire.km_rodados.toLocaleString('pt-BR') }} km</div>
                  <div><strong>Desgaste:</strong> {{ position.tire.wearPercentage.toFixed(1) }}%</div>
                </div>
              </q-tooltip>
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
    <div>Configuração de eixos não definida para este veículo.</div>
    <q-btn
      label="Definir Configuração"
      color="primary"
      unelevated
      class="q-mt-md"
      @click="$emit('define-config')"
      icon="settings"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { axleLayouts } from 'src/config/tire-layouts';
import type { TireWithStatus } from 'src/models/tire-models';

const props = defineProps<{
  axleConfig: string | null;
  tires: TireWithStatus[];
  isAgro: boolean;
}>();

defineEmits(['install', 'remove', 'define-config']);

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

function getTireStatusClass(statusInfo: TireWithStatus | undefined) {
  if (!statusInfo || statusInfo.status === 'ok') return '';
  return `tire-${statusInfo.status}`;
}

function getTireStatusColor(status: 'ok' | 'warning' | 'critical' | undefined) {
  if (status === 'critical') return 'negative';
  if (status === 'warning') return 'warning';
  return 'dark';
}
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
  align-items: center;
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
  &.tire-warning {
    border-color: $warning;
  }
  &.tire-critical {
    border-color: $negative;
  }
}
</style>

  