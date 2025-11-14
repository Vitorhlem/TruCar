<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useSettingsStore } from 'stores/settings-store';

onMounted(() => {
  // Inicializa a store de configurações para aplicar o tema guardado
  const settingsStore = useSettingsStore();
  settingsStore.init();
});
</script>