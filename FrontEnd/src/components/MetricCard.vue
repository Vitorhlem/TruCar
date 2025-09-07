<template>
  <q-card class="metric-card" flat>
    <q-card-section class="full-height flex items-center no-wrap">
      <!-- Ícone com fundo circular -->
      <div class="icon-wrapper q-mr-md flex flex-center">
        <q-icon :name="icon" color="white" size="24px" />
      </div>

      <!-- Texto e Valor -->
      <div class="col">
        <div class="metric-label">{{ label }}</div>
        <div v-if="!loading" class="metric-value">{{ value }}</div>
        <q-skeleton v-else type="text" width="80px" class="metric-value-skeleton" />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  icon: string;
  loading: boolean;
}>();
</script>

<style scoped lang="scss">
.metric-card {
  height: 90px;
  border-radius: $generic-border-radius;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  }

  // --- Estilos para o Tema Claro (Padrão) ---
  background-color: #ffffff;
  color: $dark;
  border: 1px solid $grey-3;

  .metric-label {
    color: $grey-7;
  }
  .metric-value-skeleton {
    background-color: rgba(0, 0, 0, 0.1);
  }
}

// --- Estilos para o Tema Escuro ---
.body--dark .metric-card {
  background-color: #2c3e50;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  .metric-label {
    color: $grey-5;
  }
  .metric-value-skeleton {
    background-color: rgba(255, 255, 255, 0.2);
  }
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #8e44ad; // Roxo
}

.metric-label {
  font-size: 14px;
  margin-bottom: 2px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.metric-value-skeleton {
  height: 28px;
}
</style>

