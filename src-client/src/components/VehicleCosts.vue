<template>
  <div>
    <div class="flex items-center justify-between q-mb-md">
      <div class="text-h6">Histórico de Custos</div>
      <q-btn
        @click="openAddDialog"
        color="primary"
        icon="add"
        label="Adicionar Custo"
        unelevated
      />
    </div>

    <q-table
      :rows="costsStore.costs"
      :columns="columns"
      row-key="id"
      :loading="costsStore.isLoading"
      flat
      bordered
    >
      <template v-slot:body-cell-amount="props">
        <q-td :props="props">
          {{ props.row.amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
        </q-td>
      </template>
      <template v-slot:no-data>
        <div class="full-width row flex-center text-primary q-gutter-sm q-pa-md">
          <q-icon name="money_off" size="2em" />
          <span>Nenhum custo registado para este veículo.</span>
        </div>
      </template>
    </q-table>

    <q-dialog v-model="isDialogOpen">
      <q-card style="width: 400px">
        <q-card-section>
          <div class="text-h6">Novo Custo</div>
        </q-card-section>

        <q-form @submit.prevent="onFormSubmit">
          <q-card-section class="q-gutter-y-md">
            <q-select
              outlined
              v-model="formData.cost_type"
              :options="costTypeOptions"
              label="Tipo de Custo *"
              :rules="[val => !!val || 'Campo obrigatório']"
            />
            <q-input
              outlined
              v-model.number="formData.amount"
              type="number"
              label="Valor (R$) *"
              prefix="R$"
              step="0.01"
              :rules="[val => val > 0 || 'O valor deve ser positivo']"
            />
            <q-input outlined v-model="formData.date" mask="##/##/####" label="Data *">
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover><q-date v-model="formData.date" mask="DD/MM/YYYY" /></q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input
              outlined
              v-model="formData.notes"
              type="textarea"
              label="Observações (Opcional)"
              autogrow
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup />
            <q-btn type="submit" unelevated color="primary" label="Salvar" :loading="isSubmitting" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useVehicleCostStore } from 'stores/costs-store';
import type { QTableProps } from 'quasar';
import { format, parse } from 'date-fns';

// 1. Definição das Props
const props = defineProps<{
  vehicleId: number;
}>();

// 2. Setup das Stores e Refs
const costsStore = useVehicleCostStore();
const isDialogOpen = ref(false);
const isSubmitting = ref(false);
const costTypeOptions = ['Manutenção', 'Combustível', 'Impostos', 'Seguro', 'Limpeza', 'Outros'];
const formData = ref({
  cost_type: '',
  amount: 0,
  date: format(new Date(), 'dd/MM/yyyy'),
  notes: '',
});

// 3. Definição das Colunas da Tabela
const columns: QTableProps['columns'] = [
  { name: 'cost_type', label: 'Tipo de Custo', field: 'cost_type', align: 'left', sortable: true },
  { name: 'amount', label: 'Valor', field: 'amount', align: 'right', sortable: true },
  { name: 'date', label: 'Data', field: 'date', align: 'center', sortable: true, format: (val) => format(new Date(val), 'dd/MM/yyyy') },
  { name: 'notes', label: 'Observações', field: 'notes', align: 'left' },
];

// 4. Lógica do Componente
function resetForm() {
  formData.value = {
    cost_type: '',
    amount: 0,
    date: format(new Date(), 'dd/MM/yyyy'),
    notes: '',
  };
}

function openAddDialog() {
  resetForm();
  isDialogOpen.value = true;
}

async function onFormSubmit() {
  isSubmitting.value = true;
  try {
    // Converte a data do formato DD/MM/YYYY para YYYY-MM-DD para o backend
    const parsedDate = parse(formData.value.date, 'dd/MM/yyyy', new Date());
    const payload = {
      ...formData.value,
      date: format(parsedDate, 'yyyy-MM-dd'),
    };
    await costsStore.addCost(props.vehicleId, payload);
    isDialogOpen.value = false;
  } finally {
    isSubmitting.value = false;
  }
}

// 5. Lifecycle Hook para buscar os dados
onMounted(() => {
  void costsStore.fetchCostsByVehicle(props.vehicleId);
});
</script>