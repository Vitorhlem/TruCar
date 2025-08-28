<template>
  <q-card
    class="hover-card"
    :class="{ 'hovered': isHovered }"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    flat
    bordered
    :style="cardTransform"
  >
    <slot></slot>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const isHovered = ref(false);
const mouseX = ref(0);
const mouseY = ref(0);

// Uma forma mais robusta de pegar as dimensões do card
const cardWidth = ref(0);
const cardHeight = ref(0);

function handleMouseMove(event: MouseEvent) {
  isHovered.value = true;
  const card = event.currentTarget as HTMLElement;
  if (card) {
    const rect = card.getBoundingClientRect();
    mouseX.value = event.clientX - rect.left; // x position within the element.
    mouseY.value = event.clientY - rect.top; // y position within the element.
    cardWidth.value = rect.width;
    cardHeight.value = rect.height;
  }
}

function handleMouseLeave() {
  isHovered.value = false;
  mouseX.value = 0;
  mouseY.value = 0;
  cardWidth.value = 0;
  cardHeight.value = 0;
}

const cardTransform = computed(() => {
  if (!isHovered.value || cardWidth.value === 0 || cardHeight.value === 0) {
    return {
      transform: 'translateZ(0px) rotateX(0deg) rotateY(0deg) scale(1)',
      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)', // Sombra padrão
    };
  }

  const centerX = cardWidth.value / 2;
  const centerY = cardHeight.value / 2;

  // Ajuste a intensidade da rotação conforme necessário
  const rotateX = -((mouseY.value - centerY) / centerY) * 3; // Max 3deg rotation
  const rotateY = ((mouseX.value - centerX) / centerX) * 3; // Max 3deg rotation

  return {
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`, // Levemente maior
    boxShadow: '0 8px 16px rgba(0, 0, 0, 0.25)', // Sombra mais forte ao passar o mouse
  };
});
</script>

<style scoped>
.hover-card {
  transition: transform 0.3s ease-out, box-shadow 0.3s ease-out;
  will-change: transform, box-shadow; /* Otimização para performance */
}
</style>