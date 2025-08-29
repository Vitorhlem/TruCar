<template>
  <q-page padding>
    <div v-if="userStore.isLoading && !userStore.selectedUserStats" class="flex flex-center" style="height: 80vh">
      <q-spinner color="primary" size="3em" />
    </div>

    <div v-else-if="userStore.selectedUserStats" class="q-gutter-y-lg">
      <!-- CABEÇALHO DA PÁGINA -->
      <div class="row items-center q-gutter-md">
        <q-btn flat round dense icon="arrow_back" @click="router.back()" aria-label="Voltar" />
        <div>
          <h1 class="text-h4 text-weight-bold q-my-none">Painel de Performance</h1>
          <!-- CORREÇÃO #1: Agora acessa 'selectedUser' que existe na store -->
          <div class="text-subtitle1 text-grey-7">{{ userStore.selectedUser?.full_name }}</div>
        </div>
      </div>

      <!-- CARDS DE KPIs -->
      <div class="row q-col-gutter-md">
        <!-- MÉTRICA PRINCIPAL (CARD DE DESTAQUE) -->
        <div class="col-12 col-md-4">
          <q-card flat bordered class="full-height column items-center justify-center text-center floating-card q-pa-md">
            <q-card-section class="q-pa-none">
              <div class="text-overline text-grey-8">{{ stats.primary_metric_label }}</div>
              <div class="text-h2 text-weight-bolder text-primary q-my-sm">
                {{ stats.primary_metric_value.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) }}
              </div>
              <div class="text-h6 text-grey-8">{{ stats.primary_metric_unit }}</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- OUTROS KPIs -->
        <div class="col-12 col-md-8">
          <div class="row q-col-gutter-md full-height">
            <!-- KPIs de Combustível (Condicional) -->
            <template v-if="stats.primary_metric_unit === 'km' && stats.avg_km_per_liter !== null">
              <div class="col-12 col-sm-6">
                <KpiCard
                  label="Eficiência Média"
                  :value="(stats.avg_km_per_liter || 0).toFixed(2)"
                  unit="KM/L"
                  icon="local_gas_station"
                />
              </div>
              <div class="col-12 col-sm-6">
                <KpiCard
                  label="Custo Médio por KM"
                  :value="(stats.avg_cost_per_km || 0).toFixed(2)"
                  unit="R$"
                  prefix="R$"
                  icon="paid"
                />
              </div>
            </template>
            <!-- KPIs Comuns -->
            <div class="col-12 col-sm-6">
              <KpiCard
                label="Viagens Realizadas"
                :value="stats.total_journeys"
                icon="route"
              />
            </div>
            <div class="col-12 col-sm-6">
              <KpiCard
                label="Chamados de Manutenção"
                :value="stats.maintenance_requests_count"
                icon="build"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- GRÁFICOS -->
      <div class="row q-col-gutter-lg">
        <!-- Gráfico de Performance por Veículo (DINÂMICO) -->
        <div class="col-12" :class="shouldShowFuelChart ? 'col-lg-7' : 'col-lg-12'">
           <q-card flat bordered class="floating-card">
            <q-card-section>
              <div class="text-h6 text-weight-medium">Performance por Veículo</div>
              <ApexChart type="bar" height="350" :options="performanceByVehicleChart.options" :series="performanceByVehicleChart.series" />
            </q-card-section>
          </q-card>
        </div>
        <!-- Gráfico de Eficiência de Combustível (Condicional) -->
        <div v-if="shouldShowFuelChart" class="col-12 col-lg-5">
          <q-card flat bordered class="floating-card">
            <q-card-section>
              <div class="text-h6 text-weight-medium">Eficiência de Combustível</div>
              <ApexChart type="bar" height="350" :options="efficiencyChart.options" :series="efficiencyChart.series" />
            </q-card-section>
          </q-card>
        </div>
      </div>

    </div>

    <div v-else class="text-center q-pa-xl text-grey-7">
        <q-icon name="error_outline" size="4em" />
        <p class="q-mt-md">Não foi possível carregar as estatísticas do usuário.</p>
        <q-btn flat color="primary" label="Tentar Novamente" @click="fetchData" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from 'stores/user-store';
import type { PerformanceByVehicle, UserStats } from 'src/models/user-models';
import ApexChart from 'vue3-apexcharts';
import { useQuasar } from 'quasar';
import KpiCard from 'components/KpiCard.vue'; // Componente reutilizável

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const $q = useQuasar();

// Usamos um alias para facilitar o acesso e garantir que não é nulo dentro do template
const stats = computed(() => userStore.selectedUserStats as UserStats);

const shouldShowFuelChart = computed(() => {
  return stats.value?.primary_metric_unit === 'km' && stats.value?.avg_km_per_liter !== null;
});

// --- CORREÇÃO #2: Interface para tipar o parâmetro 'opt' do formatter ---
interface ApexFormatterOptions {
  w: {
    globals: {
      labels: string[];
    };
  };
  dataPointIndex: number;
}

const efficiencyChart = computed(() => {
    const s = stats.value;
    const series = [{
      name: 'Eficiência',
      data: [(s.avg_km_per_liter || 0), (s.fleet_avg_km_per_liter || 0)]
    }];
    const options = {
      theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
      chart: { type: 'bar', height: 350, toolbar: { show: false } },
      plotOptions: { bar: { borderRadius: 4, horizontal: false, columnWidth: '50%', distributed: true } },
      dataLabels: { enabled: false },
      xaxis: { categories: ['Motorista', 'Média da Frota'], labels: { style: { colors: $q.dark.isActive ? '#fff' : '#000' } } },
      yaxis: { title: { text: 'KM/L', style: { color: $q.dark.isActive ? '#fff' : '#000' } }, labels: { style: { colors: $q.dark.isActive ? '#fff' : '#000' } } },
      legend: { show: false },
      tooltip: { y: { formatter: (val: number) => `${val.toFixed(2)} KM/L` } }
    };
    return { series, options };
});

const performanceByVehicleChart = computed(() => {
    const s = stats.value;
    const data = [...(s.performance_by_vehicle || [])].sort((a, b) => a.value - b.value); // Ordena para melhor visualização
    const series = [{ name: s.primary_metric_unit, data: data.map((item: PerformanceByVehicle) => item.value.toFixed(1)) }];
    const options = {
      theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
      chart: { type: 'bar', height: 350, toolbar: { show: false } },
      plotOptions: { bar: { borderRadius: 4, horizontal: true } },
      dataLabels: {
        enabled: true,
        textAnchor: 'start',
        style: { colors: ['#fff'] },
        // --- CORREÇÃO #2: Tipagem do parâmetro 'opt' ---
        formatter: (val: number, opt: ApexFormatterOptions) => {
          return opt.w.globals.labels[opt.dataPointIndex] + ":  " + val;
        },
        offsetX: 0,
      },
      xaxis: {
        categories: data.map((item: PerformanceByVehicle) => item.vehicle_info),
        labels: { style: { colors: $q.dark.isActive ? '#fff' : '#000' } }
      },
      yaxis: { labels: { show: false } },
      tooltip: {
        x: { show: false },
        y: {
          title: { formatter: () => '' },
          formatter: (val: number) => `${val} ${s.primary_metric_unit}`
        }
      }
    };
    return { series, options };
});

function fetchData() {
  const userId = Number(route.params.id);
  if (userId) {
    // --- CORREÇÃO #1: Chamar a nova action para buscar dados do usuário ---
    void Promise.all([
      userStore.fetchUserStats(userId),
      userStore.fetchUserById(userId) // Busca os dados do usuário (nome, etc.)
    ]);
  }
}
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.floating-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.floating-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}
</style>