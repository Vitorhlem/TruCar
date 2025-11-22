<template>
  <q-card style="width: 900px; max-width: 95vw; display: flex; flex-direction: column; max-height: 85vh;">
    <q-toolbar class="">
      <q-toolbar-title>Nova Ordem de Frete</q-toolbar-title>
      <q-btn flat round dense icon="close" @click="$emit('close')" />
    </q-toolbar>

    <q-form @submit.prevent="handleSubmit" class="col column no-wrap">
      
      <q-card-section class="col scroll q-pa-md q-gutter-y-lg">
        
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

        <div>
          <div class="text-h6 q-mb-md">Rota e Paradas</div>
          <div v-for="(stop, index) in stopPoints" :key="index" class="q-pa-md border-rounded q-mb-md">
            
            <div class="flex items-center justify-between q-mb-sm">
              <div class="text-subtitle1 text-weight-bold text-grey-8">
                <q-icon name="place" color="primary" class="q-mr-xs"/> Parada {{ index + 1 }}
              </div>
              <q-btn v-if="stopPoints.length > 1" flat round dense color="negative" icon="delete" @click="removeStopPoint(index)">
                 <q-tooltip>Remover parada</q-tooltip>
              </q-btn>
            </div>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-3">
                <q-select 
                  outlined dense bg-color=""
                  v-model="stop.type" 
                  :options="['Coleta', 'Entrega']" 
                  label="Tipo *" 
                  :rules="[val => !!val || 'Obrigatório']" 
                />
              </div>
              <div class="col-12 col-sm-4">
                <q-input 
                  outlined dense bg-color=""
                  v-model="stop.scheduled_time" 
                  type="datetime-local" 
                  stack-label 
                  label="Data/Hora *" 
                  :rules="[val => !!val || 'Obrigatório']" 
                />
              </div>
              
              <div class="col-12 col-sm-5">
                 <q-input 
                   outlined dense bg-color=""
                   v-model="stop.cep" 
                   label="CEP" 
                   mask="#####-###"
                   unmasked-value
                   :loading="isCepLoading"
                   @blur="handleStopCepBlur(index)"
                 >
                    <template v-slot:append><q-icon name="search" /></template>
                 </q-input>
              </div>

              <div class="col-12">
                 <q-input 
                   outlined dense bg-color=""
                   v-model="stop.address" 
                   label="Endereço Completo *" 
                   :rules="[val => !!val || 'Obrigatório']" 
                 />
              </div>

              <div class="col-12">
                <q-input outlined dense bg-color="" v-model="stop.cargo_description" label="Descrição da Carga (nesta parada)" />
              </div>
            </div>
          </div>
          
          <q-btn outline color="primary" icon="add_location_alt" label="Adicionar Parada" @click="addStopPoint" class="full-width" />
        </div>

      </q-card-section>
      
      <q-separator />

      <q-card-actions align="right" class="col-auto bg- q-pa-md">
        <q-btn flat label="Cancelar" color="grey-8" @click="$emit('close')" />
        <q-btn type="submit" unelevated color="primary" label="Criar Ordem de Frete" :loading="isSubmitting" class="q-px-lg" />
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
  // Reorganiza a sequência
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

<style scoped>
.border-rounded {
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
</style>