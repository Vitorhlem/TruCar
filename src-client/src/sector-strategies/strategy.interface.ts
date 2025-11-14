// Define o "contrato" para todas as estratégias de setor
export interface ISectorStrategy {
  vehicleNoun: string;
  vehicleNounPlural: string;
  journeyNoun: string;
  journeyNounPlural: string;
  distanceUnit: string;
  plateOrIdentifierLabel: string;
  startJourneyButtonLabel: string;
  vehiclePageTitle: string;
  addVehicleButtonLabel: string;
  editButtonLabel: string;
  newButtonLabel: string;
  journeyPageTitle: string;
  journeyHistoryTitle: string;
    journeyStartSuccessMessage: string;
      journeyEndSuccessMessage: string;
      odometerLabel: string;


}