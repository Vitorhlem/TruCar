<template>
  <q-card>
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>Nova Ordem de Frete</q-toolbar-title>
      <q-btn flat round dense icon="close" @click="$emit('close')" />
    </q-toolbar>

    <q-form @submit.prevent="handleSubmit">
      <q-card-section class="q-gutter-y-lg">
        <!-- SEÇÃO 1: DADOS GERAIS -->
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-select
              outlined
              v-model="formData.client_id"
              :options="clientOptions"
              label="Cliente *"
              emit-value map-options
              :rules="[val => !!val || 'Selecione um cliente']"
            />
          </div>
          <div class="col-12 col-sm-6">
            <q-input outlined v-model="formData.description" label="Descrição do Frete" />
          </div>
        </div>

        <q-separator />

        <!-- SEÇÃO 2: PONTOS DE PARADA (DINÂMICO) -->
        <div class="text-h6">Rota e Paradas</div>
        <div v-for="(stop, index) in stopPoints" :key="index" class="q-pa-md q-gutter-y-md" bordered>
          <div class="flex items-center justify-between">
            <div class="text-subtitle1 text-weight-medium">Parada {{ index + 1 }}</div>
            <q-btn v-if="stopPoints.length > 1" flat round dense color="negative" icon="delete" @click="removeStopPoint(index)" />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-select outlined v-model="stop.type" :options="['Coleta', 'Entrega']" label="Tipo *" :rules="[val => !!val || 'Campo obrigatório']" />
            </div>
            <div class="col-12 col-sm-6">
              <q-input outlined v-model="stop.scheduled_time" type="datetime-local" stack-label label="Data/Hora Agendada *" :rules="[val => !!val || 'Campo obrigatório']" />
            </div>
            
            <!-- CAMPOS DE CEP E ENDEREÇO -->
            <div class="col-12 col-sm-6">
                <q-input 
                  outlined 
                  v-model="stop.cep" 
                  label="CEP da Parada" 
                  mask="#####-###"
                  unmasked-value
                  :loading="isCepLoading"
                  @blur="handleStopCepBlur(index)"
                />
            </div>
             <div class="col-12 col-sm-6">
                <q-input outlined v-model="stop.address" label="Endereço da Parada *" :rules="[val => !!val || 'Campo obrigatório']" />
            </div>
            <!-- FIM DOS CAMPOS -->

            <div class="col-12">
              <q-input outlined v-model="stop.cargo_description" label="Descrição da Carga (nesta parada)" />
            </div>
          </div>
          <q-separator v-if="index < stopPoints.length - 1" class="q-mt-md" />
        </div>
        <q-btn outline color="primary" icon="add_location" label="Adicionar Parada" @click="addStopPoint" class="full-width" />
      </q-card-section>
      
      <q-card-actions align="right" class="q-pa-md">
        <q-btn flat label="Cancelar" @click="$emit('close')" />
        <q-btn type="submit" unelevated color="primary" label="Criar Ordem de Frete" :loading="isSubmitting" />
      </q-card-actions>
    </q-form>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useClientStore } from 'stores/client-store';
import { useFreightOrderStore } from 'stores/freight-order-store';
import type { FreightOrderCreate, StopPointCreate } from 'src/models/freight-order-models';
import { useCepApi } from 'src/composables/useCepApi';

const emit = defineEmits(['close']);

const clientStore = useClientStore();
const freightOrderStore = useFreightOrderStore();
const { isCepLoading, fetchAddressByCep } = useCepApi();

const isSubmitting = ref(false);
const formData = ref<Partial<FreightOrderCreate>>({});
const stopPoints = ref<Partial<StopPointCreate & { cep: string }>[]>([
  { type: 'Coleta', sequence_order: 1, cep: '' },
  { type: 'Entrega', sequence_order: 2, cep: '' },
]);

const clientOptions = computed(() =>
  clientStore.clients.map(c => ({ label: c.name, value: c.id }))
);

function addStopPoint() {
  stopPoints.value.push({
    sequence_order: stopPoints.value.length + 1,
    cep: ''
  });
}

function removeStopPoint(index: number) {
  stopPoints.value.splice(index, 1);
  stopPoints.value.forEach((stop, i) => {
    stop.sequence_order = i + 1;
  });
}

async function handleStopCepBlur(index: number) {
  const stop = stopPoints.value[index];
  if (stop && stop.cep) {
    const address = await fetchAddressByCep(stop.cep);
    if (address) {
      stop.address = `${address.street}, ${address.neighborhood}, ${address.city} - ${address.state}`;
    }
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    const payload: FreightOrderCreate = {
      client_id: formData.value.client_id as number,
      description: formData.value.description || null,
      stop_points: stopPoints.value.map(s => ({
        sequence_order: s.sequence_order,
        type: s.type,
        address: s.address,
        cargo_description: s.cargo_description,
        scheduled_time: s.scheduled_time,
      })) as StopPointCreate[],
    };
    
    await freightOrderStore.addFreightOrder(payload);
    emit('close');
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  void clientStore.fetchAllClients();
});
</script>
