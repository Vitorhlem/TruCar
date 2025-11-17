<template>
  <q-card flat bordered>

    <q-card-section class="bg-primary text-white">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-h6">Relatório Consolidado do Veículo</div>
          <div class="text-subtitle2">{{ report.vehicle_model }} ({{ report.vehicle_identifier }})</div>
        </div>
        <div class="q-gutter-sm">
          <q-btn @click="exportToPDF" icon="picture_as_pdf" label="PDF" dense unelevated color="white" text-color="primary" />
          <q-btn @click="exportToXLSX" icon="description" label="Excel" dense unelevated color="white" text-color="primary" />
        </div>
      </div>
      <div class="text-caption q-mt-sm">
        Período de Análise: {{ formatDate(report.report_period_start) }} a {{ formatDate(report.report_period_end) }}
      </div>
    </q-card-section>

    <q-card-section>

      <div class="row q-col-gutter-md">
        

        <div v-if="report.financial_summary" class="col-12 col-md-6">
          <q-card flat bordered>
            <q-card-section><div class="text-subtitle1">Resumo Financeiro</div></q-card-section>
            <q-list separator dense>
              <q-item>
                <q-item-section>Custo Total no Período:</q-item-section>
                <q-item-section side class="text-weight-bold">{{ formatCurrency(report.financial_summary.total_costs) }}</q-item-section>
              </q-item>

              <q-item v-if="report.financial_summary.cost_per_metric > 0">
                <q-item-section>

                  {{ report.financial_summary.metric_unit === 'km' ? 'Custo por KM (Período):' : 'Custo por Hora (Período):' }}
                </q-item-section>
                <q-item-section side class="text-weight-bold">
                  {{ formatCurrency(report.financial_summary.cost_per_metric) }} / {{ report.financial_summary.metric_unit }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
        

        <div v-if="report.performance_summary" class="col-12 col-md-6">
          <q-card flat bordered>
            <q-card-section><div class="text-subtitle1">Resumo de Performance</div></q-card-section>
            <q-list separator dense>
              

              <q-item>
                <q-item-section>
                  {{ report.performance_summary.activity_unit === 'km' ? 'Odômetro Atual:' : 'Horímetro Atual:' }}
                </q-item-section>
                <q-item-section side class="text-weight-bold">
                  {{ report.performance_summary.vehicle_total_activity.toFixed(2) }} {{ report.performance_summary.activity_unit }}
                </q-item-section>
              </q-item>


              <q-item v-if="report.performance_summary.period_total_activity > 0">
                <q-item-section>

                  {{ report.performance_summary.activity_unit === 'km' ? 'Distância (Período):' : 'Horas (Período):' }}
                </q-item-section>
                <q-item-section side class="text-weight-bold">
                  {{ report.performance_summary.period_total_activity.toFixed(2) }} {{ report.performance_summary.activity_unit }}
                </q-item-section>
              </q-item>
              

              <q-item v-if="report.performance_summary.period_total_fuel > 0">
                <q-item-section>
                  {{ report.performance_summary.activity_unit === 'km' ? 'Consumo Médio (km/l):' : 'Consumo Médio (l/h):' }}
                </q-item-section>
                <q-item-section side class="text-weight-bold">
                  {{ report.performance_summary.average_consumption.toFixed(2) }}
                  {{ report.performance_summary.activity_unit === 'km' ? 'km/l' : 'l/h' }}
                </q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </div>


      <div v-if="report.costs_detailed && report.costs_detailed.length > 0" class="q-mt-lg">
        <q-table title="Detalhamento de Custos" :rows="report.costs_detailed" :columns="costColumns" row-key="id" flat dense bordered />
      </div>


      <div v-if="report.fuel_logs_detailed && report.fuel_logs_detailed.length > 0" class="q-mt-lg">
        <q-table title="Histórico de Abastecimentos" :rows="report.fuel_logs_detailed" :columns="fuelColumns" row-key="id" flat dense bordered />
      </div>


      <div v-if="report.maintenance_detailed && report.maintenance_detailed.length > 0" class="q-mt-lg">
        <q-table title="Histórico de Manutenções" :rows="report.maintenance_detailed" :columns="maintenanceColumns" row-key="id" flat dense bordered />
      </div>


      <div v-if="report.fines_detailed && report.fines_detailed.length > 0" class="q-mt-lg">
        <q-table title="Detalhamento de Multas" :rows="report.fines_detailed" :columns="finesColumns" row-key="id" flat dense bordered />
      </div>


      <div v-if="report.journeys_detailed && report.journeys_detailed.length > 0" class="q-mt-lg">
        <q-table title="Histórico de Jornadas" :rows="report.journeys_detailed" :columns="journeysColumns" row-key="id" flat dense bordered />
      </div>
      

      <div v-if="report.documents_detailed && report.documents_detailed.length > 0" class="q-mt-lg">
        <q-table title="Documentos do Veículo" :rows="report.documents_detailed" :columns="documentsColumns" row-key="id" flat dense bordered />
      </div>
      

      <div v-if="report.tires_detailed && report.tires_detailed.length > 0" class="q-mt-lg">
        <q-table title="Gestão de Pneus" :rows="report.tires_detailed" :columns="tiresColumns" row-key="id" flat dense bordered />
      </div>

    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { type PropType } from 'vue';
import type { QTableColumn } from 'quasar';
import { format } from 'date-fns';
import { jsPDF } from 'jspdf';
import autoTable, { type UserOptions } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import type { VehicleConsolidatedReport } from 'src/models/report-models';
import type { Fine } from 'src/models/fine-models';
import type { Journey } from 'src/models/journey-models';
import type { DocumentPublic } from 'src/models/document-models';
import type { VehicleTire } from 'src/models/tire-models';
import type { MaintenanceRequest } from 'src/models/maintenance-models';
import type { FuelLog } from 'src/models/fuel-log-models';
import type { VehicleCost } from 'src/models/vehicle-cost-models';

interface AutoTableOptions extends UserOptions { startY?: number; }
interface jsPDFWithLastTable extends jsPDF { lastAutoTable: { finalY: number }; }

const props = defineProps({
  report: {
    type: Object as PropType<VehicleConsolidatedReport>,
    required: true,
  },
});


const formatDate = (dateString: string | Date | null | undefined) => {
  if (!dateString) return 'N/A';
  const date = typeof dateString === 'string' ? new Date(dateString.replace(/-/g, '/')) : dateString;
  try { return format(date, 'dd/MM/yyyy'); } catch (error) { console.error('Data Inválida:', error); return 'Data Inválida'; }
};
const formatDateTime = (dateString: string | Date | null | undefined) => {
  if (!dateString) return 'N/A';
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
   try { return format(date, 'dd/MM/yyyy HH:mm'); } catch (error) { console.error('Data Inválida:', error); return 'Data Inválida'; }
};
const formatCurrency = (value: number | null | undefined) => {
  if (value === null || value === undefined) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};



const costColumns: QTableColumn<VehicleCost>[] = [
  { name: 'date', label: 'Data', field: 'date', format: val => formatDate(val), align: 'left', sortable: true },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', align: 'left', sortable: true },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left' },
  { name: 'amount', label: 'Valor', field: 'amount', format: val => formatCurrency(val), align: 'right', sortable: true },
];

const fuelColumns: QTableColumn<FuelLog>[] = [
  { name: 'timestamp', label: 'Data', field: 'timestamp', format: val => formatDateTime(val), align: 'left', sortable: true },
  { name: 'odometer', label: 'Odômetro', field: 'odometer', align: 'center', sortable: true },
  { name: 'liters', label: 'Litros', field: 'liters', align: 'right', sortable: true },
  { name: 'total_cost', label: 'Custo Total', field: 'total_cost', format: val => formatCurrency(val), align: 'right', sortable: true },
];

const maintenanceColumns: QTableColumn<MaintenanceRequest>[] = [
  { name: 'created_at', label: 'Data', field: 'created_at', format: val => formatDate(val), align: 'left', sortable: true },
  { name: 'category', label: 'Categoria', field: 'category', align: 'left', sortable: true },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'problem_description', label: 'Descrição', field: 'problem_description', align: 'left', style: 'white-space: normal; min-width: 200px;' },
];

const finesColumns: QTableColumn<Fine>[] = [
  { name: 'date', label: 'Data', field: 'date', format: val => formatDate(val), align: 'left', sortable: true },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left', style: 'white-space: normal; min-width: 200px;' },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'value', label: 'Valor', field: 'value', format: val => formatCurrency(val), align: 'right', sortable: true },
];

const journeysColumns: QTableColumn<Journey>[] = [
  { name: 'start_time', label: 'Início', field: 'start_time', format: val => formatDateTime(val), align: 'left', sortable: true },
  { name: 'end_time', label: 'Término', field: 'end_time', format: val => formatDateTime(val), align: 'left', sortable: true },
  { name: 'start_mileage', label: 'Odôm. Inicial', field: 'start_mileage', align: 'center' },
  { name: 'end_mileage', label: 'Odôm. Final', field: 'end_mileage', align: 'center' },
  { name: 'start_engine_hours', label: 'Horím. Inicial', field: 'start_engine_hours', align: 'center' },
  { name: 'end_engine_hours', label: 'Horím. Final', field: 'end_engine_hours', align: 'center' },
  { name: 'is_active', label: 'Status', field: 'is_active', format: val => (val ? 'Ativa' : 'Finalizada'), align: 'center', sortable: true },
];

const documentsColumns: QTableColumn<DocumentPublic>[] = [
  { name: 'document_type', label: 'Tipo', field: 'document_type', align: 'left', sortable: true },
  { name: 'expiry_date', label: 'Vencimento', field: 'expiry_date', format: val => formatDate(val), align: 'center', sortable: true },
];

const tiresColumns: QTableColumn<VehicleTire>[] = [
  { name: 'brand', label: 'Marca', field: (row) => row.part.brand, align: 'left', sortable: true },
  { name: 'position', label: 'Posição', field: 'position_code', align: 'center', sortable: true },
  { name: 'install_date', label: 'Instalação', field: 'installation_date', format: val => formatDate(val), align: 'center', sortable: true },
  { name: 'cost', label: 'Custo', field: (row) => row.part.value, format: val => formatCurrency(val), align: 'right', sortable: true },
];




function exportToPDF() {
  const doc = new jsPDF() as jsPDFWithLastTable;
  const report = props.report;

  doc.setFontSize(18);
  doc.text(`Relatório Consolidado: ${report.vehicle_model} (${report.vehicle_identifier})`, 14, 22);
  doc.setFontSize(11);
  doc.setTextColor(100);
  doc.text(`Período: ${formatDate(report.report_period_start)} a ${formatDate(report.report_period_end)}`, 14, 30);
  
  let startY = 40;


  const summaryBody: (string | number)[][] = [];
  
  if (report.performance_summary) {
     const unit = report.performance_summary.activity_unit;
     const totalLabel = unit === 'km' ? 'Odômetro Atual' : 'Horímetro Atual';
     const totalValue = `${report.performance_summary.vehicle_total_activity.toFixed(2)} ${unit}`;
     summaryBody.push([totalLabel, totalValue]);
     
     if (report.performance_summary.period_total_activity > 0) {
        const periodLabel = unit === 'km' ? 'Distância (Período)' : 'Horas (Período)';
        const periodValue = `${report.performance_summary.period_total_activity.toFixed(2)} ${unit}`;
        summaryBody.push([periodLabel, periodValue]);
     }
     if (report.performance_summary.period_total_fuel > 0) {
        const consUnit = unit === 'km' ? 'km/l' : 'l/h';
        const label = `Consumo Médio (${consUnit})`;
        const value = `${report.performance_summary.average_consumption.toFixed(2)} ${consUnit}`;
        summaryBody.push([label, value]);
     }
  }

  if (report.financial_summary) {
    summaryBody.push(['Custo Total (Período)', formatCurrency(report.financial_summary.total_costs)]);
    if (report.financial_summary.cost_per_metric > 0) {
      const label = report.financial_summary.metric_unit === 'km' ? 'Custo por KM (Período)' : 'Custo por Hora (Período)';
      const value = `${formatCurrency(report.financial_summary.cost_per_metric)} / ${report.financial_summary.metric_unit}`;
      summaryBody.push([label, value]);
    }
  }

  if (summaryBody.length > 0) {
    autoTable(doc, {
      startY: startY,
      head: [['Métrica', 'Valor']],
      body: summaryBody,
    } as AutoTableOptions);
    startY = doc.lastAutoTable.finalY + 10;
  }
  
  const addTableToPdf = (title: string, head: string[][], body: (string | number | undefined | null)[][]) => {
    if (!body || body.length === 0) return;
    doc.setFontSize(14);
    doc.text(title, 14, startY);
    startY += 8;
    autoTable(doc, { startY: startY, head: head, body: body, headStyles: { fillColor: [41, 128, 185] } } as AutoTableOptions);
    startY = doc.lastAutoTable.finalY + 10;
  };

  addTableToPdf('Detalhamento de Custos',
    [['Data', 'Tipo', 'Descrição', 'Valor']],
    report.costs_detailed?.map(c => [formatDate(c.date), c.cost_type, c.description, formatCurrency(c.amount)]) || []
  );
  addTableToPdf('Histórico de Abastecimentos',
    [['Data', 'Odômetro', 'Litros', 'Valor']],
    report.fuel_logs_detailed?.map(f => [formatDateTime(f.timestamp), f.odometer, f.liters, formatCurrency(f.total_cost)]) || []
  );
  addTableToPdf('Histórico de Manutenções',
    [['Data', 'Categoria', 'Status', 'Descrição']],
    report.maintenance_detailed?.map(m => [formatDate(m.created_at), m.category, m.status, m.problem_description]) || []
  );
  addTableToPdf('Detalhamento de Multas',
    [['Data', 'Descrição', 'Status', 'Valor']],
    report.fines_detailed?.map(f => [formatDate(f.date), f.description, f.status, formatCurrency(f.value)]) || []
  );
  
  addTableToPdf('Histórico de Jornadas',
    [['Início', 'Término', 'Odôm. Início', 'Odôm. Fim', 'Status']],
    report.journeys_detailed?.map(j => [
      formatDateTime(j.start_time), 
      formatDateTime(j.end_time || ''), 
      j.start_mileage ?? 'N/A', 
      j.end_mileage ?? 'N/A', 
      j.is_active ? 'Ativa' : 'Finalizada'
    ]) || []
  );
  
  addTableToPdf('Documentos do Veículo',
    [['Tipo', 'Vencimento']],
    report.documents_detailed?.map(d => [d.document_type, formatDate(d.expiry_date)]) || []
  );
  addTableToPdf('Gestão de Pneus',
    [['Marca', 'Posição', 'Instalação', 'Custo']],
    report.tires_detailed?.map(t => [t.part.brand || 'N/A', t.position_code, formatDate(t.installation_date), formatCurrency(t.part.value)]) || []
  );
  
  doc.save(`relatorio_${report.vehicle_identifier}.pdf`);
}

function exportToXLSX() {
  const report = props.report;
  const wb = XLSX.utils.book_new();
  
  const summaryData: (string | number)[][] = [
    ["Relatório Consolidado de Veículo"],
    [`${report.vehicle_model} (${report.vehicle_identifier})`],
    [`Período: ${formatDate(report.report_period_start)} a ${formatDate(report.report_period_end)}`],
    [],
    ["Métrica", "Valor"],
  ];
  
  if (report.performance_summary) {
    const unit = report.performance_summary.activity_unit;
    const totalLabel = unit === 'km' ? 'Odômetro Atual (km)' : 'Horímetro Atual (h)';
    summaryData.push([totalLabel, report.performance_summary.vehicle_total_activity]);
    
    if (report.performance_summary.period_total_activity > 0) {
        const periodLabel = unit === 'km' ? 'Distância (Período) (km)' : 'Horas (Período) (h)';
        summaryData.push([periodLabel, report.performance_summary.period_total_activity]);
    }
    if (report.performance_summary.period_total_fuel > 0) {
        const consLabel = unit === 'km' ? 'Consumo Médio (km/l)' : 'Consumo Médio (l/h)';
        summaryData.push([consLabel, report.performance_summary.average_consumption]);
    }
  }

  if (report.financial_summary) {
    summaryData.push(['Custo Total (Período)', report.financial_summary.total_costs]);
    if (report.financial_summary.cost_per_metric > 0) {
      const label = report.financial_summary.metric_unit === 'km' ? 'Custo por KM (Período)' : 'Custo por Hora (Período)';
      summaryData.push([label, report.financial_summary.cost_per_metric]);
    }
  }
  
  const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, wsSummary, "Resumo");


  const addSheet = (sheetName: string, data: Record<string, any>[] | undefined) => {
    if (data && data.length > 0) {
      const ws = XLSX.utils.json_to_sheet(data);
      XLSX.utils.book_append_sheet(wb, ws, sheetName);
    }
  };

  addSheet("Custos", report.costs_detailed?.map(c => ({
    Data: formatDate(c.date), Tipo: c.cost_type, Descrição: c.description, Valor: c.amount
  })));
  addSheet("Abastecimentos", report.fuel_logs_detailed?.map(f => ({
    Data: formatDateTime(f.timestamp), Odômetro: f.odometer, Litros: f.liters, Custo_Total: f.total_cost
  })));
  addSheet("Manutenções", report.maintenance_detailed?.map(m => ({
    Data: formatDate(m.created_at), Categoria: m.category, Status: m.status, Descrição: m.problem_description
  })));
  addSheet("Multas", report.fines_detailed?.map(f => ({
    Data: formatDate(f.date), Descrição: f.description, Status: f.status, Valor: f.value
  })));
  addSheet("Jornadas", report.journeys_detailed?.map(j => ({
    Início: formatDateTime(j.start_time), 
    Término: formatDateTime(j.end_time || ''), 
    'Odôm. Inicial': j.start_mileage,
    'Odôm. Final': j.end_mileage,
    'Horím. Inicial': j.start_engine_hours,
    'Horím. Final': j.end_engine_hours,
    Status: j.is_active ? 'Ativa' : 'Finalizada'
  })));
  addSheet("Documentos", report.documents_detailed?.map(d => ({
    Tipo: d.document_type, Vencimento: formatDate(d.expiry_date)
  })));
  addSheet("Pneus", report.tires_detailed?.map(t => ({
    Marca: t.part.brand, Posição: t.position_code, Instalação: formatDate(t.installation_date), Custo: t.part.value
  })));

  XLSX.writeFile(wb, `relatorio_${report.vehicle_identifier}.xlsx`);
}
</script>