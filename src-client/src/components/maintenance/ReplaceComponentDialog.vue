<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="(val) => emit('update:modelValue', val)"
    persistent
  >
    <q-card style="width: 500px; max-width: 90vw">
      <q-form @submit.prevent="handleSubmit">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Substituir Componente</div>
        </q-card-section>

        <q-card-section v-if="componentToReplace">
          <div class="text-subtitle1">Componente Antigo (Saindo)</div>
          <q-item dense class="q-pa-none">
            <q-item-section>
              <q-item-label>{{ componentToReplace.part?.name }}</q-item-label>
              <q-item-label caption>
                Cód. Item:
                {{
                  componentToReplace.inventory_transaction?.item
                    ?.item_identifier || 'N/A'
                }}
              </q-item-label>
            </q-item-section>
          </q-item>

          <q-select
            v-model="form.old_item_status"
            :options="oldItemStatusOptions"
            label="Destino do Item Antigo *"
            emit-value
            map-options
            outlined
            dense
            class="q-mt-md"
            :rules="[(val) => !!val || 'Selecione um destino']"
          />
          <q-input
            v-model="form.notes"
            label="Notas da Substituição (Opcional)"
            type="textarea"
            autogrow
            outlined
            dense
            class="q-mt-sm"
          />
        </q-card-section>

        <q-separator class="q-my-md" />

        <q-card-section>
          <div class="text-subtitle1">Item Novo (Entrando)</div>
          <q-select
            v-model="form.new_item_id"
            :options="availableItemOptions"
            label="Selecione o Item do Estoque *"
            emit-value
            map-options
            outlined
            dense
            use-input
            @filter="filterAvailableItems"
            :loading="partStore.isItemsLoading"
            :rules="[
              (val) => !!val || 'Selecione um item para instalar',
            ]"
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
import { ref, watch } from 'vue';
import { useQuasar } from 'quasar';
import { usePartStore } from 'stores/part-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type {
  MaintenanceRequest,
  ReplaceComponentPayload,
} from 'src/models/maintenance-models';
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

// --- FORMULÁRIO ATUALIZADO (REVERTIDO) ---
const form = ref<{
  new_item_id: number | null; // <-- Revertido para 'new_item_id'
  old_item_status: InventoryItemStatus;
  notes: string;
}>({
  new_item_id: null,
  old_item_status: InventoryItemStatus.FIM_DE_VIDA, // Padrão
  notes: '',
});

const oldItemStatusOptions = [
  { label: 'Fim de Vida (Descartado)', value: InventoryItemStatus.FIM_DE_VIDA },
  { label: 'Disponível (Voltar ao Estoque)', value: InventoryItemStatus.DISPONIVEL },
];

// --- LÓGICA DE FILTRO (REVERTIDA) ---
const availableItemOptions = ref<{ label: string; value: number }[]>([]);

async function loadAvailableItems(partId: number | undefined) {
  if (!partId) return;
  // Assumindo que partStore.fetchAvailableItems(partId) busca
  // itens disponíveis para aquele TIPO de peça.
  await partStore.fetchAvailableItems(partId);
  filterAvailableItems('');
}

function filterAvailableItems(val: string, update?: (callbackFn: () => void) => void) {
  const needle = val.toLowerCase();
  const options = partStore.availableItems
    .filter(item =>
        // Opcional: filtrar para garantir que o item está disponível
        item.status === InventoryItemStatus.DISPONIVEL && (
        !val || 
        String(item.item_identifier).includes(needle) ||
        item.part?.name.toLowerCase().includes(needle)
      )
    )
    .map((item) => ({
      label: `${item.part?.name || 'Peça'} (Cód. ${item.item_identifier})`,
      value: item.id,
    }));

  if (update) {
    update(() => {
      availableItemOptions.value = options;
    });
  } else {
    availableItemOptions.value = options;
  }
}
// --- FIM DA LÓGICA DE FILTRO ---

async function handleSubmit() {
  // --- VALIDAÇÃO ATUALIZADA ---
  if (
    !props.maintenanceRequest ||
    !props.componentToReplace?.id || // Valida o ID do componente (correto)
    !form.value.new_item_id // Valida o ID do item novo (revertido)
  ) {
    $q.notify({
      type: 'negative',
      message: 'Erro: Dados incompletos. Selecione um item novo.',
    });
    return;
  }
  // --- FIM DA VALIDAÇÃO ---

  isLoading.value = true;

  // --- PAYLOAD ATUALIZADO ---
  const payload: ReplaceComponentPayload = {
    notes: form.value.notes,
    old_item_status: form.value.old_item_status,
    component_to_remove_id: props.componentToReplace.id, // ID do Componente (correto)
    new_item_id: form.value.new_item_id, // ID do Item (revertido)
  };
  // --- FIM DO PAYLOAD ---

  const success = await maintenanceStore.replaceComponent(
    props.maintenanceRequest.id,
    payload
  );

  if (success) {
    emit('replacement-done');
    emit('update:modelValue', false);
  }
  isLoading.value = false;
}

watch(
  () => props.modelValue,
  (isOpening) => {
    if (isOpening && props.componentToReplace) {
      form.value = {
        new_item_id: null,
        old_item_status: InventoryItemStatus.FIM_DE_VIDA,
        notes: '',
      };
      // Carrega os itens disponíveis do mesmo TIPO da peça antiga
      // (Esta era a sua lógica original)
      void loadAvailableItems(props.componentToReplace.part?.id);
    }
  }
);
</script>