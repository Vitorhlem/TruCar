<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="(val) => emit('update:modelValue', val)"
    persistent
  >
    <q-card style="width: 500px; max-width: 90vw">
      <q-form @submit.prevent="handleSubmit">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Instalar Novo Componente</div>
          <div class="text-caption">Adiciona um item do estoque ao veículo sem remover nada.</div>
        </q-card-section>

        <q-card-section>
          <q-select
            v-model="selectedPartId"
            :options="partOptions"
            label="1. Pesquisar Peça (Template) *"
            outlined
            dense
            use-input
            input-debounce="300"
            @filter="filterParts"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            :loading="isPartsLoading"
            class="q-mb-md"
          >
             <template v-slot:no-option>
              <q-item>
                <q-item-section class="text-grey">Nenhuma peça encontrada</q-item-section>
              </q-item>
            </template>
          </q-select>

          <q-select
            v-if="selectedPartId"
            v-model="form.new_item_id"
            :options="availableItemOptions"
            label="2. Selecionar Item do Estoque *"
            emit-value
            map-options
            outlined
            dense
            use-input
            @filter="filterAvailableItems"
            :loading="partStore.isItemsLoading"
            :rules="[(val) => !!val || 'Selecione um item para instalar']"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>ID Único: {{ scope.opt.value }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
            <template v-slot:no-option>
              <q-item>
                <q-item-section class="text-grey">
                  Nenhum item 'Disponível' no estoque desta peça.
                </q-item-section>
              </q-item>
            </template>
          </q-select>

           <q-input
            v-model="form.notes"
            label="Notas da Instalação (Opcional)"
            type="textarea"
            autogrow
            outlined
            dense
            class="q-mt-md"
          />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            type="submit"
            unelevated
            color="primary"
            label="Confirmar Instalação"
            :loading="isLoading"
            :disable="!form.new_item_id"
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
import type { MaintenanceRequest, InstallComponentPayload } from 'src/models/maintenance-models';
import { InventoryItemStatus } from 'src/models/inventory-item-models';

const props = defineProps<{
  modelValue: boolean;
  maintenanceRequest: MaintenanceRequest | null;
}>();

const emit = defineEmits(['update:modelValue', 'installation-done']);

const $q = useQuasar();
const partStore = usePartStore();
const maintenanceStore = useMaintenanceStore();
const isLoading = ref(false);
const isPartsLoading = ref(false);

const selectedPartId = ref<number | null>(null);
const partOptions = ref<{id: number, name: string}[]>([]);

const form = ref<{
  new_item_id: number | null;
  notes: string;
}>({
  new_item_id: null,
  notes: '',
});

// Filtro de Peças (Templates) - CORRIGIDO
function filterParts(val: string, update: (fn: () => void) => void) {
  if (partStore.parts.length === 0) {
    isPartsLoading.value = true;
    // Chamada correta da action: fetchParts()
    partStore.fetchParts()
      .then(() => {
        update(() => {
          const needle = val.toLowerCase();
          partOptions.value = partStore.parts
            .filter(p => p.name.toLowerCase().includes(needle))
            .map(p => ({ id: p.id, name: p.name }));
        });
      })
      .finally(() => {
        isPartsLoading.value = false;
      });
    return;
  }

  update(() => {
    const needle = val.toLowerCase();
    partOptions.value = partStore.parts
      .filter(p => p.name.toLowerCase().includes(needle))
      .map(p => ({ id: p.id, name: p.name }));
  });
}

// Itens Disponíveis para a Peça selecionada
const availableItemOptions = ref<{ label: string; value: number }[]>([]);

watch(selectedPartId, async (newPartId) => {
    form.value.new_item_id = null; // Reseta seleção anterior
    if (newPartId) {
        await partStore.fetchAvailableItems(newPartId);
        filterAvailableItems('');
    } else {
        availableItemOptions.value = [];
    }
});

function filterAvailableItems(val: string, update?: (callbackFn: () => void) => void) {
  const needle = val.toLowerCase();
  const options = partStore.availableItems
    .filter(item =>
        item.status === InventoryItemStatus.DISPONIVEL && (
        !val || String(item.item_identifier).includes(needle)
      )
    )
    .map((item) => ({
      label: `Item Cód. ${item.item_identifier}`,
      value: item.id,
    }));

  if (update) {
    update(() => availableItemOptions.value = options);
  } else {
    availableItemOptions.value = options;
  }
}

async function handleSubmit() {
  if (!props.maintenanceRequest || !form.value.new_item_id) {
    $q.notify({
      type: 'warning',
      message: 'Selecione um item para continuar.'
    });
    return;
  }

  isLoading.value = true;

  const payload: InstallComponentPayload = {
    new_item_id: form.value.new_item_id,
    notes: form.value.notes,
  };

  const success = await maintenanceStore.installComponent(
    props.maintenanceRequest.id,
    payload
  );

  if (success) {
    emit('installation-done');
    emit('update:modelValue', false);
  }
  isLoading.value = false;
}

watch(() => props.modelValue, (isOpen) => {
    if (isOpen) {
        selectedPartId.value = null;
        form.value = { new_item_id: null, notes: '' };
        partOptions.value = [];
    }
});
</script>