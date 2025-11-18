<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)">
    <q-card style="min-width: 500px">
      <q-card-section>
        <div class="text-h6">Novo Chamado de Manutenção</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="onSubmit">
          <q-select
            v-model="form.vehicle_id"
            :options="vehicleOptions"
            label="Veículo *"
            option-value="id"
            option-label="identifier"
            emit-value
            map-options
            outlined
            dense
            :rules="[val => !!val || 'Campo obrigatório']"
            class="q-mb-md"
          />
          
          <q-select
            v-model="form.category"
            :options="categoryOptions"
            label="Categoria *"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="form.problem_description"
            label="Descrição do Problema *"
            type="textarea"
            outlined
            dense
            class="q-mb-md"
          />

          <div class="row justify-end q-gutter-sm">
            <q-btn label="Cancelar" color="negative" flat v-close-popup />
            <q-btn label="Criar Chamado" type="submit" color="primary" unelevated :loading="loading" />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useVehicleStore } from 'stores/vehicle-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { MaintenanceCategory } from 'src/models/maintenance-models';

const props = defineProps<{
  modelValue: boolean;
  preSelectedVehicleId?: number | null;
  maintenanceType?: 'PREVENTIVA' | 'CORRETIVA'; // <--- NOVA PROP
}>();

const emit = defineEmits(['update:modelValue', 'request-created']);

const vehicleStore = useVehicleStore();
const maintenanceStore = useMaintenanceStore();

const loading = ref(false);

// --- CORREÇÃO: Tipagem correta ---
interface VehicleOption {
  id: number;
  identifier: string;
}
const vehicleOptions = ref<VehicleOption[]>([]);
// --------------------------------

const categoryOptions = Object.values(MaintenanceCategory);

const form = ref({
  vehicle_id: null as number | null,
  problem_description: '',
  category: MaintenanceCategory.MECHANICAL,
  maintenance_type: 'CORRETIVA' as 'PREVENTIVA' | 'CORRETIVA' // <--- NOVO CAMPO NO FORM
});

onMounted(async () => {
  await vehicleStore.fetchAllVehicles({ rowsPerPage: 100 });
  vehicleOptions.value = vehicleStore.vehicles.map(v => ({
    id: v.id,
    identifier: `${v.brand} ${v.model} (${v.license_plate || v.identifier})`
  }));
});

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.preSelectedVehicleId) {
      form.value.vehicle_id = props.preSelectedVehicleId;
    } else {
      form.value.vehicle_id = null;
    }
    form.value.maintenance_type = props.maintenanceType || 'CORRETIVA';
    if (form.value.maintenance_type === 'PREVENTIVA') {
       form.value.problem_description = 'Manutenção Preventiva Agendada';
    } else {
       form.value.problem_description = '';
    }
    form.value.category = MaintenanceCategory.MECHANICAL;
  }
});

async function onSubmit() {
  if (!form.value.vehicle_id) return;
  
  loading.value = true;
  const success = await maintenanceStore.createRequest({
    vehicle_id: form.value.vehicle_id,
    problem_description: form.value.problem_description,
    category: form.value.category,
    maintenance_type: form.value.maintenance_type // <--- ENVIA O TIPO
  });
  loading.value = false;

  if (success) {
    emit('update:modelValue', false);
    emit('request-created');
  }
}
</script>