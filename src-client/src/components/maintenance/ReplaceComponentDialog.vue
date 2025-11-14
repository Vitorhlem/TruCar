<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)" persistent>
    <q-card style="width: 500px; max-width: 90vw;">
      <q-form @submit.prevent="handleSubmit">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Substituir Componente</div>
        </q-card-section>

        <q-card-section v-if="componentToReplace">
          <div class="text-subtitle1">Item Antigo (Saindo)</div>
          <q-item dense class="q-pa-none">
            <q-item-section>
              <q-item-label>{{ componentToReplace.part?.name }}</q-item-label>
              <q-item-label caption>
                Cód. Item: {{ componentToReplace.inventory_transaction?.item?.item_identifier || 'N/A' }}
              </q-item-label>
            </q-item-section>
          </q-item>
          
          <q-select
            v-model="form.old_item_status"
            :options="oldItemStatusOptions"
            label="Destino do Item Antigo *"
            emit-value map-options outlined dense class="q-mt-md"
            :rules="[val => !!val || 'Selecione um destino']"
          />
          <q-input
            v-model="form.notes"
            label="Notas da Remoção (Opcional)"
            type="textarea" autogrow outlined dense class="q-mt-sm"
          />
        </q-card-section>
        
        <q-separator class="q-my-md" />

        <q-card-section>
          <div class="text-subtitle1">Item Novo (Entrando)</div>
          <q-select
            v-model="form.new_item_id"
            :options="availableItemOptions"
            label="Selecione o Item do Estoque *"
            emit-value map-options outlined dense
            use-input
            @filter="filterAvailableItems"
            :loading="partStore.isItemsLoading"
            :rules="[val => !!val || 'Selecione um item para instalar']"
          >
            <template v-slot:no-option>
              <q-item>
                <q-item-section class="text-grey">
                  Nenhum item 'Disponível' encontrado para esta peça.
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn 
            type="submit" 
            unelevated 
            color="primary" 
            label="Confirmar Substituição"
            :loading="isLoading" 
          />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
// --- CORREÇÃO ESLINT (remover 'computed') ---
import { ref, watch } from 'vue';
// --- FIM DA CORREÇÃO ---
import { useQuasar } from 'quasar';
import { usePartStore } from 'stores/part-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type { MaintenanceRequest, ReplaceComponentPayload } from 'src/models/maintenance-models';
import { InventoryItemStatus } from 'src/models/inventory-item-models';

const props = defineProps<{
  modelValue: boolean;
  maintenanceRequest: MaintenanceRequest | null;
  componentToReplace: VehicleComponent | null;
}>();

const emit = defineEmits(['update:modelValue', 'replacement-done']);

const $q = useQuasar();
const partStore = usePartStore();
const maintenanceStore = useMaintenanceStore();
const isLoading = ref(false);

// --- CORREÇÃO DE TIPO (number | null) ---
const form = ref<{
  new_item_id: number | null;
  old_item_status: InventoryItemStatus;
  notes: string;
}>({
// --- FIM DA CORREÇÃO ---
  new_item_id: null,
  old_item_status: InventoryItemStatus.FIM_DE_VIDA, // Padrão
  notes: '',
});

const oldItemStatusOptions = [
  { label: 'Fim de Vida (Descartado)', value: InventoryItemStatus.FIM_DE_VIDA },
];

const availableItemOptions = ref<{ label: string; value: number }[]>([]);

async function loadAvailableItems(partId: number | undefined) {
  if (!partId) return;
  await partStore.fetchAvailableItems(partId);
  filterAvailableItems('');
}

function filterAvailableItems(val: string, update?: (callbackFn: () => void) => void) {
  const needle = val.toLowerCase();
  const options = partStore.availableItems
    // --- CORREÇÃO (checar item.part) ---
    .filter(item => 
      item.part && ( // Garante que 'part' não é nulo
        !val || 
        String(item.item_identifier).includes(needle) ||
        item.part.name.toLowerCase().includes(needle)
      )
    )
    .map(item => ({
      label: `${item.part?.name || 'Peça'} (Cód. ${item.item_identifier})`, // Usa optional chaining
    // --- FIM DA CORREÇÃO ---
      value: item.id,
    }));
  
  if (update) {
    update(() => { availableItemOptions.value = options; });
  } else {
    availableItemOptions.value = options;
  }
}

async function handleSubmit() {
  if (!props.maintenanceRequest || !props.componentToReplace?.inventory_transaction?.item?.id || !form.value.new_item_id) {
    $q.notify({ type: 'negative', message: 'Erro: Dados incompletos. Selecione um item novo.' });
    return;
  }

  isLoading.value = true;
  
  const payload: ReplaceComponentPayload = {
    notes: form.value.notes,
    old_item_status: form.value.old_item_status,
    old_item_id: props.componentToReplace.inventory_transaction.item.id,
    // --- CORREÇÃO ESLINT (remover 'as number') ---
    new_item_id: form.value.new_item_id,
    // --- FIM DA CORREÇÃO ---
  };

  const success = await maintenanceStore.replaceComponent(props.maintenanceRequest.id, payload);
  
  if (success) {
    $q.notify({ type: 'positive', message: 'Componente substituído com sucesso!' });
    emit('replacement-done'); 
    emit('update:modelValue', false);
  }
  isLoading.value = false;
}

watch(() => props.modelValue, (isOpening) => {
  if (isOpening && props.componentToReplace) {
    // --- CORREÇÃO DE TIPO (number | null) ---
    form.value = {
      new_item_id: null,
      old_item_status: InventoryItemStatus.FIM_DE_VIDA,
      notes: '',
    };
    // --- FIM DA CORREÇÃO ---
    void loadAvailableItems(props.componentToReplace.part?.id);
  }
});
</script>