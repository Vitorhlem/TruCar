import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { VehicleConsolidatedReport, DriverPerformanceReport } from 'src/models/report-models';

interface ReportState {
  isLoading: boolean;
  vehicleReport: VehicleConsolidatedReport | null;
  driverPerformanceReport: DriverPerformanceReport | null; // <-- ADICIONADO
}

export const useReportStore = defineStore('report', {
  state: (): ReportState => ({
    isLoading: false,
    vehicleReport: null,
    driverPerformanceReport: null, // <-- ADICIONADO
  }),

  actions: {
    // Limpa todos os relatórios para um novo começo
    clearReports() {
      this.vehicleReport = null;
      this.driverPerformanceReport = null;
    },

    async generateVehicleConsolidatedReport(vehicleId: number, startDate: string, endDate: string) {
      this.clearReports(); // Garante que apenas um relatório esteja ativo por vez
      this.isLoading = true;
      try {
        const payload = { vehicle_id: vehicleId, start_date: startDate, end_date: endDate };
        const response = await api.post<VehicleConsolidatedReport>('/reports/vehicle-consolidated', payload);
        this.vehicleReport = response.data;
        Notify.create({ type: 'positive', message: 'Relatório de Veículo gerado com sucesso!' });
      } catch (error) {
        console.error("Erro ao gerar relatório consolidado:", error);
        Notify.create({ type: 'negative', message: 'Falha ao gerar o relatório.' });
      } finally {
        this.isLoading = false;
      }
    },

    // --- NOVA AÇÃO ADICIONADA ---
    async generateDriverPerformanceReport(startDate: string, endDate: string) {
      this.clearReports(); // Garante que apenas um relatório esteja ativo por vez
      this.isLoading = true;
      try {
        const payload = { start_date: startDate, end_date: endDate };
        const response = await api.post<DriverPerformanceReport>('/reports/driver-performance', payload);
        this.driverPerformanceReport = response.data;
        Notify.create({ type: 'positive', message: 'Relatório de Desempenho gerado com sucesso!' });
      } catch (error) {
        console.error("Erro ao gerar relatório de desempenho:", error);
        Notify.create({ type: 'negative', message: 'Falha ao gerar o relatório.' });
      } finally {
        this.isLoading = false;
      }
    },
  },
});