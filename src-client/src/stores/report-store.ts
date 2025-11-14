import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar'; // Removido 'useQuasar'
import type {
  VehicleConsolidatedReport,
  DriverPerformanceReport,
  FleetManagementReport,
  DashboardSummary,
} from 'src/models/report-models';

interface ReportState {
  isLoading: boolean;
  vehicleReport: VehicleConsolidatedReport | null;
  driverPerformanceReport: DriverPerformanceReport | null;
  fleetManagementReport: FleetManagementReport | null;
  dashboardSummary: DashboardSummary | null;
}

export const useReportStore = defineStore('report', {
  state: (): ReportState => ({
    isLoading: false,
    vehicleReport: null,
    driverPerformanceReport: null,
    fleetManagementReport: null,
    dashboardSummary: null,
  }),

  actions: {
    clearReports() {
      this.vehicleReport = null;
      this.driverPerformanceReport = null;
      this.fleetManagementReport = null;
    },

    async getDashboardSummary() {
      // (Esta função estava faltando na sua store, mas estava sendo chamada)
      this.isLoading = true;
      try {
        const response = await api.get('/reports/dashboard-summary');
        this.dashboardSummary = response.data;
      } catch (error) {
        Notify.create({
          type: 'negative',
          message: 'Erro ao buscar resumo do dashboard.',
        });
        console.error('Erro ao buscar resumo do dashboard:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async generateVehicleConsolidatedReport(
      vehicleId: number,
      startDate: string,
      endDate: string,
      sections: Record<string, boolean>
    ) {
      this.clearReports();
      this.isLoading = true;
      try {
        const payload = {
          vehicle_id: vehicleId,
          start_date: startDate,
          end_date: endDate,
          sections: sections,
        };

        const response = await api.post<VehicleConsolidatedReport>(
          '/reports/vehicle-consolidated',
          payload
        );
        this.vehicleReport = response.data;
        Notify.create({
          type: 'positive',
          message: 'Relatório de Veículo gerado com sucesso!',
        });
      } catch (error: unknown) { // Corrigido: any -> unknown
        console.error('Erro ao gerar relatório consolidado:', error);
        // Adicionado type guard para o erro
        const apiError = error as { response?: { data?: { detail?: string } } };
        Notify.create({
          type: 'negative',
          message:
            apiError.response?.data?.detail || 'Falha ao gerar o relatório.',
        });
      } finally {
        this.isLoading = false;
      }
    },

    async generateDriverPerformanceReport(startDate: string, endDate: string) {
      this.clearReports();
      this.isLoading = true;
      try {
        const payload = { start_date: startDate, end_date: endDate };

        const response = await api.post<DriverPerformanceReport>(
          '/reports/driver-performance',
          payload
        );
        this.driverPerformanceReport = response.data;
        Notify.create({
          type: 'positive',
          message: 'Relatório de Desempenho gerado com sucesso!',
        });
      } catch (error: unknown) { // Corrigido: any -> unknown
        console.error('Erro ao gerar relatório de desempenho:', error);
        const apiError = error as { response?: { data?: { detail?: string } } };
        Notify.create({
          type: 'negative',
          message:
            apiError.response?.data?.detail || 'Falha ao gerar o relatório.',
        });
      } finally {
        this.isLoading = false;
      }
    },

    async generateFleetManagementReport(startDate: string, endDate: string) {
      this.clearReports();
      this.isLoading = true;
      try {
        const payload = { start_date: startDate, end_date: endDate };

        const response = await api.post<FleetManagementReport>(
          '/reports/fleet-management',
          payload
        );
        this.fleetManagementReport = response.data;
        Notify.create({
          type: 'positive',
          message: 'Relatório Gerencial gerado com sucesso!',
        });
      } catch (error: unknown) { // Corrigido: any -> unknown
        console.error('Erro ao gerar relatório gerencial:', error);
        const apiError = error as { response?: { data?: { detail?: string } } };
        Notify.create({
          type: 'negative',
          message:
            apiError.response?.data?.detail || 'Falha ao gerar o relatório.',
        });
      } finally {
        this.isLoading = false;
      }
    },
  },
});