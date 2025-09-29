<template>
  <q-page padding>
    <h1 class="text-h5 text-weight-bold q-my-md">Gerador de Relatórios</h1>

    <div v-if="isDemo" class="column flex-center text-center q-pa-md" style="min-height: 60vh;">
      <div>
        <q-icon name="workspace_premium" color="amber" size="100px" />
        <div class="text-h5 q-mt-sm">Esta é uma funcionalidade do plano completo</div>
        <div class="text-body1 text-grey-8 q-mt-sm">
          Faça o upgrade da sua conta para aceder a relatórios detalhados,<br />
          filtros por data, exportação para PDF e muito mais.
        </div>
        <q-btn
          @click="showUpgradeDialog"
          color="primary"
          label="Saber Mais sobre o Plano Completo"
          unelevated
          class="q-mt-lg"
        />
      </div>
    </div>

    <q-card v-else flat bordered class="floating-card">
      <q-card-section class="q-gutter-md">
        <q-select
          outlined
          v-model="reportType"
          :options="reportOptions"
          label="Tipo de Relatório"
          emit-value map-options
        />
        <q-select
          v-if="reportType === 'activity_by_driver'"
          outlined
          v-model="targetId"
          :options="userOptions"
          label="Selecione o Motorista"
          emit-value map-options
        />

        <q-input outlined v-model="dateRangeText" label="Selecione o Período" readonly>
          <template v-slot:append>
            <q-icon name="event" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-date v-model="dateRange" range />
              </q-popup-proxy> </q-icon>
          </template>
        </q-input>
      </q-card-section>
      <q-separator />
      <q-card-actions align="right">
        <q-btn
          @click="generateReport"
          color="primary"
          label="Gerar Relatório em PDF"
          icon="picture_as_pdf"
          unelevated
          :loading="isLoading"
          :disable="!isFormValid"
        />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from 'stores/user-store';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth-store';
import type { User } from 'src/models/auth-models';

const userStore = useUserStore();
const $q = useQuasar();
const authStore = useAuthStore();

const reportType = ref<string | null>(null);
const targetId = ref<number | null>(null);
const dateRange = ref<{ from: string, to: string } | null>(null);
const isLoading = ref(false);

const reportOptions = [
  { label: 'Relatório de Atividade por Motorista', value: 'activity_by_driver' },
];

const userOptions = computed(() => userStore.users
  .filter(u => u.role === 'driver')
  .map((u: User) => ({ label: u.full_name, value: u.id }))
);

const dateRangeText = computed(() => {
  if (dateRange.value) {
    return `${dateRange.value.from} - ${dateRange.value.to}`;
  }
  return '';
});

const isFormValid = computed(() => reportType.value && targetId.value && dateRange.value);

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para liberar recursos avançados como relatórios detalhados e cadastro ilimitado de veículos e motoristas, entre em contato com nossa equipe comercial.',
    ok: {
      label: 'Entendido',
      color: 'primary',
      unelevated: true
    },
    persistent: false
  });
}

async function generateReport() {
  if (!isFormValid.value) return;
  isLoading.value = true;
  try {
    const payload = {
      report_type: reportType.value,
      target_id: targetId.value,
      date_from: dateRange.value?.from.replace(/\//g, '-'),
      date_to: dateRange.value?.to.replace(/\//g, '-')
    };
    const response = await api.post('/report-generator/generate', payload, { responseType: 'blob' });
    
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = `relatorio_${reportType.value}_${targetId.value}.pdf`;
    link.click();
    window.URL.revokeObjectURL(link.href);

  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao gerar o relatório.' });
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  if (userStore.users.length === 0) {
    void userStore.fetchAllUsers();
  }
});
</script>