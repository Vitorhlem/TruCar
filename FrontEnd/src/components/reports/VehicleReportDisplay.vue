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
        <div class="col-12 col-md-6">
          <q-card flat bordered>
            <q-card-section><div class="text-subtitle1">Resumo Financeiro</div></q-card-section>
            <q-list separator dense>
              <q-item>
                <q-item-section>Custo Total no Período:</q-item-section>
                <q-item-section side class="text-weight-bold">{{ formatCurrency(report.financial_summary.total_costs) }}</q-item-section>
              </q-item>
              <q-item>
                <q-item-section>Custo por KM Rodado:</q-item-section>
                <q-item-section side class="text-weight-bold">{{ formatCurrency(report.financial_summary.cost_per_km) }} / km</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card flat bordered>
            <q-card-section><div class="text-subtitle1">Resumo de Performance</div></q-card-section>
            <q-list separator dense>
              <q-item>
                <q-item-section>Distância Percorrida:</q-item-section>
                <q-item-section side class="text-weight-bold">{{ report.performance_summary.total_distance_km.toFixed(2) }} km</q-item-section>
              </q-item>
              <q-item>
                <q-item-section>Consumo Médio:</q-item-section>
                <q-item-section side class="text-weight-bold">{{ report.performance_summary.average_consumption.toFixed(2) }} km/l</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </div>

      <div class="q-mt-lg">
        <q-table
          title="Detalhamento de Custos"
          :rows="report.costs_detailed"
          :columns="costColumns"
          row-key="id"
          flat dense
          bordered
        />
      </div>

      <div class="q-mt-lg">
        <q-table
          title="Histórico de Abastecimentos"
          :rows="report.fuel_logs_detailed"
          :columns="fuelColumns"
          row-key="id"
          flat dense
          bordered
        />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { type PropType } from 'vue';
import type { QTableColumn } from 'quasar';
import { format } from 'date-fns';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import type { VehicleConsolidatedReport } from 'src/models/report-models';

const props = defineProps({
  report: {
    type: Object as PropType<VehicleConsolidatedReport>,
    required: true,
  },
});

// Funções de formatação
const formatDate = (dateString: string) => format(new Date(dateString.replace(/-/g, '/')), 'dd/MM/yyyy');
const formatCurrency = (value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

// Colunas das tabelas
const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: val => formatDate(val), align: 'left' },
  { name: 'cost_type', label: 'Tipo', field: 'cost_type', align: 'left' },
  { name: 'description', label: 'Descrição', field: 'description', align: 'left' },
  { name: 'amount', label: 'Valor', field: 'amount', format: val => formatCurrency(val), align: 'right' },
];

const fuelColumns: QTableColumn[] = [
  { name: 'timestamp', label: 'Data', field: 'timestamp', format: val => format(new Date(val), 'dd/MM/yy HH:mm'), align: 'left' },
  { name: 'odometer', label: 'Odômetro', field: 'odometer', align: 'center' },
  { name: 'liters', label: 'Litros', field: 'liters', align: 'right' },
  { name: 'total_cost', label: 'Custo Total', field: 'total_cost', format: val => formatCurrency(val), align: 'right' },
];

// Funções de Exportação
function exportToPDF() {
  const doc = new jsPDF();
  const report = props.report;

  // Título e Cabeçalho
  doc.setFontSize(18);
  doc.text(`Relatório Consolidado: ${report.vehicle_model} (${report.vehicle_identifier})`, 14, 22);
  doc.setFontSize(11);
  doc.setTextColor(100);
  doc.text(`Período: ${formatDate(report.report_period_start)} a ${formatDate(report.report_period_end)}`, 14, 30);

  // AutoTable para os resumos
  (doc as any).autoTable({
    startY: 40,
    head: [['Métrica', 'Valor']],
    body: [
      ['Custo Total', formatCurrency(report.financial_summary.total_costs)],
      ['Custo por KM', `${formatCurrency(report.financial_summary.cost_per_km)} / km`],
      ['Distância Total', `${report.performance_summary.total_distance_km.toFixed(2)} km`],
      ['Consumo Médio', `${report.performance_summary.average_consumption.toFixed(2)} km/l`],
    ],
  });

  // AutoTable para Detalhamento de Custos
  if (report.costs_detailed.length > 0) {
    (doc as any).autoTable({
      startY: (doc as any).lastAutoTable.finalY + 10,
      head: [['Data', 'Tipo', 'Descrição', 'Valor']],
      body: report.costs_detailed.map(c => [
        formatDate(c.date), c.cost_type, c.description, formatCurrency(c.amount)
      ]),
      headStyles: { fillColor: [41, 128, 185] },
    });
  }
  
  doc.save(`relatorio_${report.vehicle_identifier}.pdf`);
}

function exportToXLSX() {
  const report = props.report;

  // Criação da Planilha
  const wb = XLSX.utils.book_new();
  
  // Aba de Resumo
  const summaryData = [
    ["Relatório Consolidado de Veículo"],
    [`${report.vehicle_model} (${report.vehicle_identifier})`],
    [`Período: ${formatDate(report.report_period_start)} a ${formatDate(report.report_period_end)}`],
    [], // Linha em branco
    ["Métrica", "Valor"],
    ['Custo Total', report.financial_summary.total_costs],
    ['Custo por KM', report.financial_summary.cost_per_km],
    ['Distância Total (km)', report.performance_summary.total_distance_km],
    ['Consumo Médio (km/l)', report.performance_summary.average_consumption],
  ];
  const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, wsSummary, "Resumo");

  // Aba de Custos Detalhados
  const costsData = report.costs_detailed.map(c => ({
    Data: formatDate(c.date),
    Tipo: c.cost_type,
    Descrição: c.description,
    Valor: c.amount,
  }));
  const wsCosts = XLSX.utils.json_to_sheet(costsData);
  XLSX.utils.book_append_sheet(wb, wsCosts, "Custos Detalhados");

  XLSX.writeFile(wb, `relatorio_${report.vehicle_identifier}.xlsx`);
}
</script>