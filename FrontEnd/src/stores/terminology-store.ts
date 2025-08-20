import { defineStore } from 'pinia';
import { computed } from 'vue';
import { useAuthStore } from './auth-store';
import { AgroStrategy, ServicesStrategy, ConstructionStrategy } from 'src/sector-strategies';
import type { ISectorStrategy } from 'src/sector-strategies/strategy.interface';

export const useTerminologyStore = defineStore('terminology', () => {
  const authStore = useAuthStore();

  // 1. O PONTO CENTRAL: Escolhe a estratégia correta com base no setor do utilizador
  const activeStrategy = computed<ISectorStrategy>(() => {
    const sector = authStore.userSector;
    switch (sector) {
      case 'agronegocio':
        return AgroStrategy;
      case 'construcao_civil':
        return ConstructionStrategy;
      case 'servicos':
        return ServicesStrategy;
      default:
        return ServicesStrategy; // Retorna a estratégia padrão se o setor for desconhecido
    }
  });

  // 2. Todos os getters agora simplesmente "delegam" para a estratégia ativa.
  //    Não há mais lógica de if/else aqui!
  const vehicleNoun = computed(() => activeStrategy.value.vehicleNoun);
  const vehicleNounPlural = computed(() => activeStrategy.value.vehicleNounPlural);
  const journeyNoun = computed(() => activeStrategy.value.journeyNoun);
  const journeyNounPlural = computed(() => activeStrategy.value.journeyNounPlural);
  const distanceUnit = computed(() => activeStrategy.value.distanceUnit);
  const plateOrIdentifierLabel = computed(() => activeStrategy.value.plateOrIdentifierLabel);
  const startJourneyButtonLabel = computed(() => activeStrategy.value.startJourneyButtonLabel);
  const vehiclePageTitle = computed(() => activeStrategy.value.vehiclePageTitle);
  const addVehicleButtonLabel = computed(() => activeStrategy.value.addVehicleButtonLabel);
  const editButtonLabel = computed(() => activeStrategy.value.editButtonLabel);
  const newButtonLabel = computed(() => activeStrategy.value.newButtonLabel);
  const journeyPageTitle = computed(() => activeStrategy.value.journeyPageTitle);
  const journeyHistoryTitle = computed(() => activeStrategy.value.journeyHistoryTitle);

  return {
    vehicleNoun,
    vehicleNounPlural,
    journeyNoun,
    journeyNounPlural,
    distanceUnit,
    plateOrIdentifierLabel,
    startJourneyButtonLabel,
    vehiclePageTitle,
    addVehicleButtonLabel,
    editButtonLabel,
    newButtonLabel,
    journeyPageTitle,
    journeyHistoryTitle,
  };
});