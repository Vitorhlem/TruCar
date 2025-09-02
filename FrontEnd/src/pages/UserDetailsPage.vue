<template>
  <q-page padding>

    <div v-if="isDemo" class="column flex-center text-center q-pa-md" style="min-height: 80vh;">
      <div>
        <q-icon name="workspace_premium" color="amber" size="100px" />
        <div class="text-h5 q-mt-sm">Esta é uma funcionalidade do plano completo</div>
        <div class="text-body1 text-grey-8 q-mt-sm">
          A análise detalhada de performance de cada motorista é um recurso premium.<br />
          Faça o upgrade para desbloquear estes insights.
        </div>
        <q-btn
          @click="showUpgradeDialog"
          color="primary"
          label="Saber Mais sobre o Plano Completo"
          unelevated
          class="q-mt-lg"
        />
        
        <q-btn flat color="grey-8" label="Voltar" @click="router.back()" class="q-mt-sm" />
      </div>
    </div>
    
    <div v-else>
      <div v-if="userStore.isLoading && !userStore.selectedUserStats" class="flex flex-center" style="height: 80vh">
        <q-spinner color="primary" size="3em" />
      </div>

      <div v-else-if="userStore.selectedUserStats" class="q-gutter-y-lg">
        <div class="row items-center q-gutter-md">
          <q-btn flat round dense icon="arrow_back" @click="router.back()" aria-label="Voltar" />
          <div>
            <h1 class="text-h4 text-weight-bold q-my-none">Painel de Performance</h1>
            <div class="text-subtitle1 text-grey-7">{{ userStore.selectedUser?.full_name }}</div>
          </div>
        </div>

        <div class="row q-col-gutter-md">
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

          <div class="col-12 col-md-8">
            <div class="row q-col-gutter-md full-height">
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

        <div class="row q-col-gutter-lg">
          <div class="col-12" :class="shouldShowFuelChart ? 'col-lg-7' : 'col-lg-12'">
             <q-card flat bordered class="floating-card">
              <q-card-section>
                <div class="text-h6 text-weight-medium">Performance por Veículo</div>
                <ApexChart type="bar" height="350" :options="performanceByVehicleChart.options" :series="performanceByVehicleChart.series" />
              </q-card-section>
            </q-card>
          </div>
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
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useUserStore } from 'stores/user-store';
import { useAuthStore } from 'stores/auth-store'; // <-- ADICIONADO
import type { PerformanceByVehicle, UserStats } from 'src/models/user-models';
import ApexChart from 'vue3-apexcharts';
import KpiCard from 'components/KpiCard.vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const $q = useQuasar();
const authStore = useAuthStore(); // <-- ADICIONADO

// --- LÓGICA DE BLOQUEIO ADICIONADA ---
const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para aceder a esta e outras funcionalidades premium, entre em contato com nossa equipe comercial.',
    ok: { label: 'Entendido', color: 'primary', unelevated: true },
    persistent: true
  });
}
// --- FIM DA ADIÇÃO ---

const stats = computed(() => userStore.selectedUserStats as UserStats);

const shouldShowFuelChart = computed(() => {
  return stats.value?.primary_metric_unit === 'km' && stats.value?.avg_km_per_liter !== null;
});

interface ApexFormatterOptions {
  w: { globals: { labels: string[] } };
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
    const data = [...(s.performance_by_vehicle || [])].sort((a, b) => a.value - b.value);
    const series = [{ name: s.primary_metric_unit, data: data.map((item: PerformanceByVehicle) => item.value.toFixed(1)) }];
    const options = {
      theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
      chart: { type: 'bar', height: 350, toolbar: { show: false } },
      plotOptions: { bar: { borderRadius: 4, horizontal: true } },
      dataLabels: {
        enabled: true,
        textAnchor: 'start',
        style: { colors: ['#fff'] },
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
    void Promise.all([
      userStore.fetchUserStats(userId),
      userStore.fetchUserById(userId)
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
