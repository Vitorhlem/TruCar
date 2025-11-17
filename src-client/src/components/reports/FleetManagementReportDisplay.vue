<template>
  <q-card flat bordered>
    <q-card-section class="bg-primary text-white">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-h6">Relatório Gerencial da Frota</div>
          <div class="text-subtitle2">Análise macro de custos e performance</div>
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
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-4">
          <q-card flat bordered><q-card-section><div class="text-caption text-grey">Custo Total da Frota</div><div class="text-h6 text-weight-bold">{{ formatCurrency(report.summary.total_cost) }}</div></q-card-section></q-card>
        </div>
        <div class="col-4">
          <q-card flat bordered><q-card-section><div class="text-caption text-grey">Distância Total (km)</div><div class="text-h6 text-weight-bold">{{ report.summary.total_distance_km.toFixed(2) }}</div></q-card-section></q-card>
        </div>
        <div class="col-4">
          <q-card flat bordered><q-card-section><div class="text-caption text-grey">Custo Médio (R$/km)</div><div class="text-h6 text-weight-bold">{{ report.summary.overall_cost_per_km.toFixed(2) }}</div></q-card-section></q-card>
        </div>
      </div>

      <div class="row q-col-gutter-lg">
        <div class="col-12 col-md-5">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6">Distribuição de Custos</div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <CostsPieChart v-if="hasCostData" :costs="costsForChart" style="height: 350px;" />
              <div v-else class="text-center text-grey q-pa-md">Sem dados de custo no período.</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-7">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6">Rankings de Veículos</div>
            </q-card-section>
            <q-separator />
            <q-list separator>
              <q-expansion-item icon="trending_up" label="Top 5 Maiores Custos Totais" header-class="text-negative" default-opened>
                <RankingTable :data="report.top_5_most_expensive_vehicles" />
              </q-expansion-item>
              <q-expansion-item icon="local_gas_station" label="Top 5 Mais Eficientes (km/l)" header-class="text-positive">
                <RankingTable :data="report.top_5_most_efficient_vehicles" />
              </q-expansion-item>
               <q-expansion-item icon="warning" label="Top 5 Maiores Custos por KM" header-class="text-orange">
                <RankingTable :data="report.top_5_highest_cost_per_km_vehicles" />
              </q-expansion-item>
            </q-list>
          </q-card>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { type PropType, computed } from 'vue';
import { format } from 'date-fns';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import type { FleetManagementReport, VehicleRankingEntry } from 'src/models/report-models';
import CostsPieChart from 'components/CostsPieChart.vue';
import RankingTable from 'components/reports/RankingTable.vue';




interface jsPDFWithPlugin extends jsPDF {
  lastAutoTable: { finalY: number };
}


const props = defineProps({
  report: {
    type: Object as PropType<FleetManagementReport>,
    required: true,
  },
});

const formatDate = (dateString: string) => format(new Date(dateString.replace(/-/g, '/')), 'dd/MM/yyyy');
const formatCurrency = (value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const hasCostData = computed(() => Object.keys(props.report.costs_by_category).length > 0);

const costsForChart = computed(() => {
  return Object.entries(props.report.costs_by_category).map(([type, amount]) => ({
    cost_type: type,
    amount: amount,
  }));
});

function exportToPDF() {
  const doc = new jsPDF();
  const report = props.report;
  const title = 'Relatório Gerencial da Frota';
  const period = `Período: ${formatDate(report.report_period_start)} a ${formatDate(report.report_period_end)}`;

  doc.setFontSize(18);
  doc.text(title, 14, 22);
  doc.setFontSize(11);
  doc.setTextColor(100);
  doc.text(period, 14, 30);

  const summaryBody = [
    ['Custo Total da Frota', formatCurrency(report.summary.total_cost)],
    ['Distância Total', `${report.summary.total_distance_km.toFixed(2)} km`],
    ['Custo Médio Geral', `${formatCurrency(report.summary.overall_cost_per_km)} / km`],
  ];
  autoTable(doc, { startY: 40, head: [['Métrica', 'Valor']], body: summaryBody });

  const createRankingBody = (data: VehicleRankingEntry[]) => data.map(item => [item.vehicle_identifier, `${item.value.toFixed(2)} ${item.unit}`]);



  autoTable(doc, {
    startY: (doc as jsPDFWithPlugin).lastAutoTable.finalY + 10,
    head: [['Top 5 - Maiores Custos (R$)']],
    body: createRankingBody(report.top_5_most_expensive_vehicles),
    theme: 'grid', headStyles: { fillColor: '#c0392b' }
  });

  autoTable(doc, {
    startY: (doc as jsPDFWithPlugin).lastAutoTable.finalY + 1,
    head: [['Top 5 - Maiores Custos por KM (R$/km)']],
    body: createRankingBody(report.top_5_highest_cost_per_km_vehicles),
    theme: 'grid', headStyles: { fillColor: '#f39c12' }
  });

  autoTable(doc, {
    startY: (doc as jsPDFWithPlugin).lastAutoTable.finalY + 1,
    head: [['Top 5 - Mais Eficientes (km/l)']],
    body: createRankingBody(report.top_5_most_efficient_vehicles),
    theme: 'grid', headStyles: { fillColor: '#27ae60' }
  });

  doc.save('relatorio_gerencial_frota.pdf');
}

function exportToXLSX() {
  const report = props.report;
  const wb = XLSX.utils.book_new();

  const summaryData = [
    ["Relatório Gerencial da Frota"], [],
    ["Período", `${formatDate(report.report_period_start)} a ${formatDate(report.report_period_end)}`], [],
    ["Resumo Geral"],
    ["Custo Total (R$)", report.summary.total_cost],
    ["Distância Total (km)", report.summary.total_distance_km],
    ["Custo Médio (R$/km)", report.summary.overall_cost_per_km],
  ];
  const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, wsSummary, "Resumo");
  
  const rankingsData = [
    ...report.top_5_most_expensive_vehicles.map(v => ({ Ranking: "Maiores Custos (R$)", Veículo: v.vehicle_identifier, Valor: v.value })),
    ...report.top_5_highest_cost_per_km_vehicles.map(v => ({ Ranking: "Maiores Custos por KM (R$/km)", Veículo: v.vehicle_identifier, Valor: v.value })),
    ...report.top_5_most_efficient_vehicles.map(v => ({ Ranking: "Mais Eficientes (km/l)", Veículo: v.vehicle_identifier, Valor: v.value })),
  ];
  const wsRankings = XLSX.utils.json_to_sheet(rankingsData);
  XLSX.utils.book_append_sheet(wb, wsRankings, "Rankings");

  XLSX.writeFile(wb, "relatorio_gerencial_frota.xlsx");
}
</script>