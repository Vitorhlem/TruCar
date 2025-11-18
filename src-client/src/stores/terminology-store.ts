import { defineStore } from 'pinia';
import type { UserSector } from 'src/models/auth-models';
import { AgroStrategy, ServicesStrategy, ConstructionStrategy, FreightStrategy } from 'src/sector-strategies';
import type { ISectorStrategy } from 'src/sector-strategies/strategy.interface';

interface TerminologyState {
  currentSector: UserSector;
}

export const useTerminologyStore = defineStore('terminology', {
  state: (): TerminologyState => ({
    currentSector: null,
  }),

  getters: {
    activeStrategy(state): ISectorStrategy {
      switch (state.currentSector) {
        case 'agronegocio':
          return AgroStrategy;
        case 'construcao_civil':
          return ConstructionStrategy;
        case 'servicos':
          return ServicesStrategy;
        case 'frete':
          return FreightStrategy;
        default:
          return ServicesStrategy;
      }
    },
    
    vehicleNoun(): string { return this.activeStrategy.vehicleNoun; },
    vehicleNounPlural(): string { return this.activeStrategy.vehicleNounPlural; },
    journeyNoun(): string { return this.activeStrategy.journeyNoun; },
    journeyNounPlural(): string { return this.activeStrategy.journeyNounPlural; },
    distanceUnit(): string { return this.activeStrategy.distanceUnit; },
    
    // --- NOVO GETTER (Calculado) ---
    // Define a unidade de combustível baseada na unidade de distância/tempo
    fuelUnit(): string {
      const dist = this.activeStrategy.distanceUnit.toLowerCase();
      // Se for km, retorna km/l. Se for horas (h), retorna l/h.
      return dist.includes('km') ? 'km/l' : 'l/h';
    },
    // ------------------------------

    plateOrIdentifierLabel(): string { return this.activeStrategy.plateOrIdentifierLabel; },
    startJourneyButtonLabel(): string { return this.activeStrategy.startJourneyButtonLabel; },
    vehiclePageTitle(): string { return this.activeStrategy.vehiclePageTitle; },
    addVehicleButtonLabel(): string { return this.activeStrategy.addVehicleButtonLabel; },
    editButtonLabel(): string { return this.activeStrategy.editButtonLabel; },
    newButtonLabel(): string { return this.activeStrategy.newButtonLabel; },
    journeyPageTitle(): string { return this.activeStrategy.journeyPageTitle; },
    journeyHistoryTitle(): string { return this.activeStrategy.journeyHistoryTitle; },
    journeyStartSuccessMessage(): string { return this.activeStrategy.journeyStartSuccessMessage; },
    journeyEndSuccessMessage(): string { return this.activeStrategy.journeyEndSuccessMessage; },
    odometerLabel(): string { return this.activeStrategy.odometerLabel; },
  },

  actions: {
    setSector(sector: UserSector) {
      this.currentSector = sector;
    },
  },
});