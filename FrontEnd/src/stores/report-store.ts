// Em FrontEnd/src/stores/report-store.ts

import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { VehicleConsolidatedReport } from 'src/models/report-models';

interface ReportState {
  isLoading: boolean;
  vehicleReport: VehicleConsolidatedReport | null;
}

export const useReportStore = defineStore('report', {
  state: (): ReportState => ({
    isLoading: false,
    vehicleReport: null,
  }),

  actions: {
    async generateVehicleConsolidatedReport(vehicleId: number, startDate: string, endDate: string) {
      this.isLoading = true;
      this.vehicleReport = null; // Limpa o relatório anterior
      try {
        const payload = {
          vehicle_id: vehicleId,
          start_date: startDate,
          end_date: endDate,
        };
        const response = await api.post<VehicleConsolidatedReport>('/reports/vehicle-consolidated', payload);
        this.vehicleReport = response.data;
        Notify.create({ type: 'positive', message: 'Relatório gerado com sucesso!' });
      } catch (error) {
        console.error("Erro ao gerar relatório consolidado:", error);
        Notify.create({ type: 'negative', message: 'Falha ao gerar o relatório. Verifique os filtros e tente novamente.' });
      } finally {
        this.isLoading = false;
      }
    },

    clearReport() {
      this.vehicleReport = null;
    }
  },
});