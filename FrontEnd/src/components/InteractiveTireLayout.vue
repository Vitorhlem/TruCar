<template>
  <q-card flat bordered class="q-pa-md new-layout-card">
    <div v-if="layout" class="vehicle-schematic">
      <div class="chassis-beam"></div>
      <div
        v-for="(axle, axleIndex) in layout"
        :key="axleIndex"
        class="axle-assembly"
        :class="{ 'front-axle': axleIndex === 0 && layout.length > 1 }"
      >
        <div class="axle-bar"></div>
        <div class="tires-on-axle">
          <div
            v-for="position in axle"
            :key="position.code"
            class="tire-slot"
          >
            <q-card
              flat
              bordered
              class="tire-card"
              :class="getTireStatusClass(findTireByPosition(position.code))"
            >
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-8 ellipsis" :title="position.label">
                  {{ position.code }}
                  <q-tooltip>{{ position.label }}</q-tooltip>
                </div>
                <div class="tire-icon-wrapper">
                    <q-icon
                      v-if="findTireByPosition(position.code)"
                      name="img:src/assets/car-icon.png"
                      size="lg"
                    />
                    <q-icon v-else name="add_circle_outline" size="lg" class="text-grey-4" />
                </div>
                <div v-if="findTireByPosition(position.code)" class="tire-info">
                  <div class="text-weight-medium ellipsis" :title="findTireByPosition(position.code)?.part.brand || 'N/A'">
                    {{ findTireByPosition(position.code)?.part.brand || 'Marca' }}
                  </div>
                  <div class="text-caption text-grey-7 ellipsis" :title="findTireByPosition(position.code)?.part.serial_number || 'N/A'">
                    {{ findTireByPosition(position.code)?.part.serial_number || 'Série' }}
                  </div>
                </div>
                <div v-else class="tire-info empty">
                  <div class="text-caption text-grey">Vazio</div>
                </div>
              </q-card-section>
              <q-card-actions class="absolute-full column items-center justify-center tire-actions">
                 <div v-if="findTireByPosition(position.code)">
                    <q-btn fab-mini icon="info" @click="showTireDetails(findTireByPosition(position.code)!)" color="primary" class="q-mb-sm">
                      <q-tooltip>Ver Detalhes</q-tooltip>
                    </q-btn>
                    <q-btn fab-mini icon="delete" @click="onRemoveTire(findTireByPosition(position.code)!)" color="negative">
                       <q-tooltip>Remover Pneu</q-tooltip>
                    </q-btn>
                 </div>
                 <div v-else>
                    <q-btn fab-mini icon="add" @click="onInstallTire(position.code)" color="positive">
                      <q-tooltip>Instalar Pneu</q-tooltip>
                    </q-btn>
                 </div>
              </q-card-actions>
            </q-card>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center q-pa-lg">
        <div class="text-grey">Layout de eixos não encontrado para a configuração: {{ axleConfig }}</div>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';
import { useQuasar } from 'quasar';
import type { VehicleTire, TireWithStatus } from 'src/models/tire-models';
import { axleLayouts } from 'src/config/tire-layouts';

const $q = useQuasar();

const props = defineProps({
  axleConfig: {
    type: String as PropType<string | null>,
    required: true,
  },
  tires: {
    type: Array as PropType<TireWithStatus[]>,
    required: true,
  },
  isAgro: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['install', 'remove']);

const layout = computed(() => {
    if (!props.axleConfig || !(props.axleConfig in axleLayouts)) {
        return null;
    }
return axleLayouts[props.axleConfig];
});

const findTireByPosition = (positionCode: string): TireWithStatus | undefined => {
  return props.tires.find(tire => tire.position_code === positionCode);
};

const onInstallTire = (positionCode: string) => emit('install', positionCode);
const onRemoveTire = (tire: VehicleTire) => emit('remove', tire);

const getTireStatusClass = (tire: TireWithStatus | undefined) => {
  if (!tire) return 'tire-empty';
  if (tire.status === 'critical') return 'tire-status-critical';
  if (tire.status === 'warning') return 'tire-status-warning';
  return 'tire-status-ok';
};

const showTireDetails = (tire: TireWithStatus) => {
    const wearInfo = props.isAgro
        ? `${tire.horas_de_uso?.toFixed(0) || 0} / ${tire.lifespan_km || 0} horas`
        : `${tire.km_rodados?.toLocaleString('pt-BR') || 0} / ${tire.lifespan_km?.toLocaleString('pt-BR') || 0} km`;

    $q.dialog({
        title: `Detalhes do Pneu (Pos. ${tire.position_code})`,
        message: `
            <strong>Marca/Modelo:</strong> ${tire.part.brand || ''} ${tire.part.name} <br/>
            <strong>Série:</strong> ${tire.part.serial_number || 'N/A'} <br/>
            <strong>Desgaste:</strong> ${tire.wearPercentage?.toFixed(2) || 0}% (${wearInfo}) <br/>
            <strong>Status:</strong> <span class="text-weight-bold text-${tire.status === 'critical' ? 'negative' : (tire.status === 'warning' ? 'warning' : 'positive')}">${tire.status.toUpperCase()}</span>
        `,
        html: true,
        ok: { label: 'Fechar', flat: true }
    });
};
</script>

<style lang="scss" scoped>
.new-layout-card {
  background-color: #f7f9fc;
  padding: 24px;
}
.vehicle-schematic {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 40px 0;
}
.chassis-beam {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  background-color: #d8dde6;
  border-radius: 6px;
  z-index: 1;
}
.axle-assembly {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  z-index: 2;
}
.axle-bar {
  position: absolute;
  left: 10%;
  right: 10%;
  top: 50%;
  transform: translateY(-50%);
  height: 8px;
  background-color: #b0b8c9;
  border-radius: 4px;
}
.front-axle {
  margin-bottom: 40px;
}
.tires-on-axle {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tire-slot {
  flex-basis: 150px;
  max-width: 150px;
}
.tire-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease-in-out;
  cursor: pointer;
  position: relative;
  border: 1px solid #e0e7ee;
  .q-card__section {
    padding: 8px;
    z-index: 2;
    background-color: white;
    transition: opacity 0.3s ease-in-out;
  }
  .tire-actions {
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease-in-out;
    background: rgba(255, 255, 255, 0.85);
    z-index: 3;
    backdrop-filter: blur(4px);
  }
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    .q-card__section {
      opacity: 0;
    }
    .tire-actions {
      opacity: 1;
      visibility: visible;
    }
  }
}
.tire-icon-wrapper {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 4px 0;
}
.tire-info {
    height: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.tire-info.empty {
    color: #9e9e9e;
}
.tire-status-ok {
  border-left: 6px solid $positive;
}
.tire-status-warning {
  border-left: 6px solid $warning;
}
.tire-status-critical {
  border-left: 6px solid $negative;
}
.tire-empty {
    border-left: 6px solid #e0e0e0;
}
</style>