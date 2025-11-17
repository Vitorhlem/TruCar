<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useSettingsStore } from 'stores/settings-store';

onMounted(() => {

  const settingsStore = useSettingsStore();
  settingsStore.init();
});
</script>