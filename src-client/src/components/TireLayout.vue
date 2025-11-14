<template>
  <div v-if="layout"
       class="tire-layout-container"
       :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-1'">

    <div v-for="(axle, axleIndex) in layout.axles" :key="axleIndex" class="axle">
      <div class.="tire-slot" v-for="position in axle.positions" :key="position.code">

        <q-card flat bordered class="tire-card" :class="getTireStatusClass(position.tire)">
          <q-card-section class="q-pa-sm text-center relative-position">

            <div class="text-caption text-grey">{{ position.label }} ({{ position.code }})</div>

            <div v-if="!position.tire">
              <q-icon name="local_shipping" size="xl" color="grey-7" />
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
import { useQuasar } from 'quasar'; // Importar o useQuasar
import { axleLayouts } from 'src/config/tire-layouts';
import type { TireWithStatus } from 'src/models/tire-models';

const $q = useQuasar(); // Ativar o Quasar para usar no template

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
  // Adiciona uma classe de borda reativa ao tema
  if (statusInfo.status === 'warning') return 'warning-border';
  if (statusInfo.status === 'critical') return 'critical-border';
  return '';
}

function getTireStatusColor(status: 'ok' | 'warning' | 'critical' | undefined) {
  if (status === 'critical') return 'negative';
  if (status === 'warning') return 'warning';
  return 'primary';
}
</script>

<style scoped lang="scss">
.tire-layout-container {
  padding: 16px;
  border-radius: $generic-border-radius;
  overflow-x: auto;
  transition: background-color 0.3s;
  // REMOVIDO: background e border fixos
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
  }

  // 5. Classes de borda que usam variáveis de cor corretas
  &.warning-border {
    border-color: $warning;
  }
  &.critical-border {
    border-color: $negative;
  }
}
</style>