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
              <q-expansion-item icon="trending_up" label="Top 5 Maiores Custos Totais" header-class="text-negative">
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
import type { FleetManagementReport } from 'src/models/report-models';
import CostsPieChart from 'components/CostsPieChart.vue';
import RankingTable from 'components/reports/RankingTable.vue'; // Um novo componente reutilizável

const props = defineProps({
  report: {
    type: Object as PropType<FleetManagementReport>,
    required: true,
  },
});

const formatDate = (dateString: string) => format(new Date(dateString.replace(/-/g, '/')), 'dd/MM/yyyy');
const formatCurrency = (value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const hasCostData = computed(() => Object.keys(props.report.costs_by_category).length > 0);

// Transforma os dados para o formato que o CostsPieChart espera
const costsForChart = computed(() => {
  return Object.entries(props.report.costs_by_category).map(([type, amount]) => ({
    cost_type: type,
    amount: amount,
  }));
});

// Funções de exportação (PDF e Excel) podem ser adicionadas aqui,
// seguindo o mesmo padrão dos outros componentes de relatório.
function exportToPDF() { /* ... Lógica de exportação ... */ }
function exportToXLSX() { /* ... Lógica de exportação ... */ }

</script>