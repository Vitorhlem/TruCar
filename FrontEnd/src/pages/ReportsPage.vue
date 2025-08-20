<template>
  <q-page padding>
    <h1 class="text-h5 text-weight-bold q-my-md">Gerador de Relatórios</h1>
    
    <q-card flat bordered class="floating-card">
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
        <!-- Adicione outros seletores de alvo aqui para outros relatórios -->

        <q-input outlined v-model="dateRangeText" label="Selecione o Período" readonly>
          <template v-slot:append>
            <q-icon name="event" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-date v-model="dateRange" range />
              </q-popup-proxy>
            </q-icon>
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
import type { User } from 'src/models/auth-models';

const userStore = useUserStore();
const $q = useQuasar();

const reportType = ref<string | null>(null);
const targetId = ref<number | null>(null);
const dateRange = ref<{ from: string, to: string } | null>(null);
const isLoading = ref(false);

const reportOptions = [
  { label: 'Relatório de Atividade por Motorista', value: 'activity_by_driver' },
  // (Outros tipos de relatório viriam aqui)
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