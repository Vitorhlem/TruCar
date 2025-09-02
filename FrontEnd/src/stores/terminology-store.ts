import { defineStore } from 'pinia';
import { computed, ref } from 'vue'; // Adicionado ref
import type { UserSector } from 'src/models/auth-models'; // Importamos o tipo
import { AgroStrategy, ServicesStrategy, ConstructionStrategy, FreightStrategy } from 'src/sector-strategies'; // Adicionada FreightStrategy
import type { ISectorStrategy } from 'src/sector-strategies/strategy.interface';

export const useTerminologyStore = defineStore('terminology', () => {
  // 1. Criamos um estado local para o setor
  const currentSector = ref<UserSector>(null);

  // 2. Criamos uma action para definir o setor
  function setSector(sector: UserSector) {
    currentSector.value = sector;
  }

  // 3. O 'computed' agora usa o estado local, que é controlado pela nossa action
  const activeStrategy = computed<ISectorStrategy>(() => {
    switch (currentSector.value) {
      case 'agronegocio':
        return AgroStrategy;
      case 'construcao_civil':
        return ConstructionStrategy;
      case 'servicos':
        return ServicesStrategy;
      // --- CASO 'frete' ADICIONADO ---
      case 'frete':
        return FreightStrategy;
      default:
        // Retorna uma estratégia padrão segura se o setor for nulo ou desconhecido
        return ServicesStrategy;
    }
  });

  // 4. Todos os getters continuam a funcionar da mesma forma
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
  const journeyStartSuccessMessage = computed(() => activeStrategy.value.journeyStartSuccessMessage);
  const journeyEndSuccessMessage = computed(() => activeStrategy.value.journeyEndSuccessMessage);

  return {
    // A nova action é exportada
    setSector,
    // E todos os getters continuam disponíveis
    vehicleNoun,
    vehicleNounPlural,
    journeyNoun,
    journeyNounPlural,
    distanceUnit,
    plateOrIdentifierLabel,
    journeyStartSuccessMessage,
    journeyEndSuccessMessage,
    startJourneyButtonLabel,
    vehiclePageTitle,
    addVehicleButtonLabel,
    editButtonLabel,
    newButtonLabel,
    journeyPageTitle,
    journeyHistoryTitle,
  };
});