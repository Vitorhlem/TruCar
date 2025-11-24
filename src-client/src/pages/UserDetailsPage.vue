<template>
  <q-page class="q-pa-md q-pa-lg-xl">
    
    <div v-if="isLockedForDemo" class="absolute-full flex flex-center bg-grey-2 text-center q-pa-md" style="z-index: 2000;">
      <q-card flat class="bg-white shadow-24" style="max-width: 500px; width: 100%; border-radius: 16px;">
        <q-card-section class="q-pt-xl q-pb-lg">
          <div class="bg-amber-1 q-pa-lg rounded-borders inline-block q-mb-md" style="border-radius: 50%">
             <q-icon name="workspace_premium" color="amber-9" size="64px" />
          </div>
          <div class="text-h5 text-weight-bold text-grey-9">Relatório Gerencial Pro</div>
          <div class="text-body1  q-mt-md q-px-md">
            A visualização consolidada de custos, multas e abastecimentos é exclusiva do Plano PRO.
          </div>
        </q-card-section>
        <q-card-actions align="center" class="q-pb-xl q-gutter-sm">
          <q-btn flat label="Voltar" color="grey-8" @click="router.back()" />
          <q-btn color="primary" label="Desbloquear PRO" unelevated size="lg" icon="lock_open" @click="showUpgradeDialog" />
        </q-card-actions>
      </q-card>
    </div>

    <div v-else>
      <div v-if="isLoadingData" class="flex flex-center" style="height: 60vh">
        <q-spinner-dots color="primary" size="4em" />
      </div>

      <div v-else-if="stats" class="animate-fade">
        
        <div class="row items-center justify-between q-mb-lg">
          <div class="row items-center">
            <q-btn flat round icon="arrow_back" color="grey-7" @click="router.back()" class="q-mr-sm" />
            <q-avatar size="72px" font-size="36px" color="primary" text-color="white" class="q-mr-md shadow-3">
                {{ getUserInitials(userName) }}
            </q-avatar>
            <div>
                <h1 class="text-h4 text-weight-bold q-my-none line-height-tight">{{ userName }}</h1>
                <div class="text-subtitle1  flex items-center q-mt-xs">
                   <q-badge color="grey-3" text-color="grey-8" class="q-py-xs q-px-sm">
                      {{ userRoleLabel }}
                   </q-badge>
                   <span class="q-mx-sm text-grey-4">|</span>
                   <span class="text-caption">{{ userEmail }}</span>
                </div>
            </div>
          </div>

        </div>

        <div class="text-h6 q-mb-md text-weight-bold text-grey-8">Indicadores Operacionais</div>
        
        <div class="row q-col-gutter-md q-mb-xl">
          <div class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey text-uppercase">Distância Total</div>
                  <div class="text-h4 text-weight-bolder text-primary">
                    {{ formatNumber(stats.primary_metric_value) }} <span class="text-h6 text-grey-5">KM</span>
                  </div>
                </div>
                <q-avatar color="blue-1" text-color="blue-8" icon="add_road" size="lg" />
              </q-card-section>
              <q-separator />
              <q-card-section class="q-py-sm ">
                 <div class="text-caption ">Média de {{ formatNumber(stats.primary_metric_value / (stats.total_journeys || 1)) }} km por viagem</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey text-uppercase">Viagens Realizadas</div>
                  <div class="text-h4 text-weight-bolder text-grey-9">
                    {{ stats.total_journeys }}
                  </div>
                </div>
                <q-avatar color="grey-2" text-color="grey-8" icon="route" size="lg" />
              </q-card-section>
              <q-separator />
              <q-card-section class="q-py-sm ">
                 <div class="text-caption ">Registradas no sistema</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey text-uppercase">Abastecimentos</div>
                  <div class="text-h4 text-weight-bolder text-indigo-8">
                    {{ fuelLogCount }}
                  </div>
                </div>
                <q-avatar color="indigo-1" text-color="indigo-8" icon="local_gas_station" size="lg" />
              </q-card-section>
              <q-separator />
              <q-card-section class="q-py-sm ">
                 <div class="text-caption ">Eficiência média: {{ (stats.avg_km_per_liter || 0).toFixed(1) }} km/l</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey text-uppercase">Multas Registradas</div>
                  <div class="text-h4 text-weight-bolder" :class="fineCount > 0 ? 'text-negative' : 'text-positive'">
                    {{ fineCount }}
                  </div>
                </div>
                <q-avatar :color="fineCount > 0 ? 'red-1' : 'green-1'" :text-color="fineCount > 0 ? 'negative' : 'positive'" icon="gavel" size="lg" />
              </q-card-section>
              <q-separator />
              <q-card-section class="q-py-sm ">
                 <div class="text-caption " v-if="fineCount === 0">Nenhuma infração recente</div>
                 <div class="text-caption text-negative" v-else>Atenção requerida</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey text-uppercase">Chamados Abertos</div>
                  <div class="text-h4 text-weight-bolder text-orange-9">
                    {{ stats.maintenance_requests_count }}
                  </div>
                </div>
                <q-avatar color="orange-1" text-color="orange-9" icon="build_circle" size="lg" />
              </q-card-section>
              <q-separator />
              <q-card-section class="q-py-sm ">
                 <div class="text-caption ">Solicitações de oficina</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey text-uppercase">Total de Gastos</div>
                  <div class="text-h4 text-weight-bolder text-grey-9">
                    <span class="text-h6 text-grey-6">R$</span> {{ formatNumber(totalExpenses) }}
                  </div>
                </div>
                <q-avatar color="grey-3" text-color="grey-9" icon="attach_money" size="lg" />
              </q-card-section>
              <q-separator />
              <q-card-section class="q-py-sm ">
                 <div class="text-caption ">Custo/km: R$ {{ (stats.avg_cost_per_km || 0).toFixed(2) }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="row q-col-gutter-lg">
          <div class="col-12 col-lg-8">
             <q-card flat bordered class="full-height">
              <q-card-section class="row items-center justify-between">
                <div class="text-h6">Utilização por Veículo</div>
                <q-btn-toggle
                  v-model="chartMetric"
                  toggle-color="primary"
                  flat dense
                  :options="[
                    {label: 'KM', value: 'km'},
                    {label: 'Viagens', value: 'trips'}
                  ]"
                />
              </q-card-section>
              <q-card-section>
                <ApexChart type="bar" height="320" :options="performanceByVehicleChart.options" :series="performanceByVehicleChart.series" />
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-lg-4">
            <q-card flat bordered class="full-height">
              <q-card-section>
                <div class="text-h6">Eficiência de Combustível</div>
                <div class="text-caption text-grey">Comparativo com a média da frota</div>
              </q-card-section>
              <q-card-section>
                <ApexChart type="bar" height="320" :options="efficiencyChart.options" :series="efficiencyChart.series" />
              </q-card-section>
            </q-card>
          </div>
        </div>

      </div>

      <div v-else class="column flex-center text-center q-pa-xl " style="min-height: 50vh">
        <q-icon name="cloud_off" size="5em" color="grey-4" />
        <div class="text-h6 q-mt-md">Dados indisponíveis</div>
        <q-btn outline color="primary" label="Recarregar" @click="fetchData" class="q-mt-sm" />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import ApexChart from 'vue3-apexcharts';

// Stores
import { useUserStore } from 'stores/user-store';
import { useAuthStore } from 'stores/auth-store';
// Removidos stores não utilizados (fineStore, fuelLogStore, terminologyStore)

// Models
import type { UserStats } from 'src/models/user-models';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const $q = useQuasar();
const authStore = useAuthStore();

const isLoadingData = ref(true);
const chartMetric = ref('km');

// Contadores Adicionais
const fineCount = ref(0);
const fuelLogCount = ref(0);
const totalExpenses = ref(0);

const isLockedForDemo = computed(() => authStore.isDemo && authStore.isManager);

function showUpgradeDialog() {
  $q.dialog({
    title: 'Upgrade para TruCar PRO',
    message: 'Tenha acesso a relatórios financeiros detalhados por condutor.',
    ok: { label: 'Falar com Consultor', color: 'primary', unelevated: true },
    cancel: true
  });
}

const stats = computed(() => userStore.selectedUserStats as UserStats);

// User Info
const userName = computed(() => authStore.isDriver ? authStore.user?.full_name : userStore.selectedUser?.full_name);
const userEmail = computed(() => authStore.isDriver ? authStore.user?.email : userStore.selectedUser?.email);

const userRoleLabel = computed(() => {
    // CORREÇÃO: Casting para string para evitar erro de sobreposição de tipos
    const role = (authStore.isDriver ? authStore.user?.role : userStore.selectedUser?.role) as string;
    return role === 'driver' ? 'Motorista' : role === 'manager' ? 'Gestor' : 'Usuário';
});

function getUserInitials(name: string | undefined) {
    if (!name) return 'U';
    return name.slice(0, 2).toUpperCase();
}

function formatNumber(val: number | undefined) {
    if (val === undefined || val === null) return '0';
    return val.toLocaleString('pt-BR', { maximumFractionDigits: 1 });
}

// --- Configuração dos Gráficos ---
const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--q-primary').trim() || '#1976D2';

const efficiencyChart = computed(() => {
    const s = stats.value || {};
    return {
      series: [{ name: 'KM/L', data: [(s.avg_km_per_liter || 0), (s.fleet_avg_km_per_liter || 0)] }],
      options: {
        chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
        theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
        colors: [primaryColor, '#9e9e9e'],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '45%', distributed: true } },
        xaxis: { categories: ['Motorista', 'Média Frota'], labels: { style: { fontSize: '12px' } } },
        legend: { show: false },
        grid: { borderColor: $q.dark.isActive ? '#333' : '#e0e0e0' }
      }
    };
});

const performanceByVehicleChart = computed(() => {
    const s = stats.value || {};
    const data = [...(s.performance_by_vehicle || [])].sort((a, b) => a.value - b.value);
    
    return {
      series: [{ name: s.primary_metric_unit, data: data.map(i => i.value.toFixed(1)) }],
      options: {
        chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
        theme: { mode: $q.dark.isActive ? 'dark' : 'light' },
        colors: [primaryColor],
        plotOptions: { bar: { borderRadius: 4, horizontal: true, barHeight: '60%' } },
        dataLabels: { enabled: true, textAnchor: 'start', style: { colors: ['#fff'] }, offsetX: 0 },
        xaxis: { categories: data.map(i => i.vehicle_info), labels: { show: false } },
        yaxis: { labels: { show: false } }, 
        grid: { show: false }
      }
    };
});

async function fetchData() {
  isLoadingData.value = true;
  const userId = Number(route.params.id);
  
  if (userId) {
    try {
        // CORREÇÃO: Tipagem correta para Promise<void>
        const promises: Promise<void>[] = [userStore.fetchUserStats(userId)];
        if (authStore.isManager) promises.push(userStore.fetchUserById(userId));
        
        await Promise.all(promises);
        
        // CORREÇÃO: Supressão explícita do erro de 'any'
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const s = userStore.selectedUserStats as any;
        fineCount.value = s?.total_fines || 0; 
        fuelLogCount.value = s?.total_fuel_logs || 0;
        totalExpenses.value = s?.total_costs || 0;

    } catch (e) {
        console.error(e);
    }
  }
  isLoadingData.value = false;
}

onMounted(() => {
  // CORREÇÃO: 'void' para marcar a promise flutuante como intencional
  void fetchData();
});
</script>

<style scoped lang="scss">
.line-height-tight { line-height: 1.1; }
.animate-fade { animation: fadeIn 0.4s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>