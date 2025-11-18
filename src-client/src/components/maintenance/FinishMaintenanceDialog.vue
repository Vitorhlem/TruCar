<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)" persistent>
    <q-card style="min-width: 450px">
      <q-card-section class="bg-positive text-white">
        <div class="text-h6">Concluir Manutenção</div>
      </q-card-section>

      <q-card-section>
        <div class="text-body2 q-mb-md">
          O chamado será fechado. Para remover o alerta do painel, defina a <strong>próxima</strong> manutenção preventiva.
        </div>
        
        <q-form @submit="onSubmit">
          <q-input 
            v-model="form.manager_notes" 
            label="Notas do Gestor / Solução Aplicada" 
            outlined 
            type="textarea" 
            autogrow 
            class="q-mb-md"
          />

          <q-separator class="q-mb-md" />
          <div class="text-subtitle2 q-mb-sm text-primary">Agendamento da Próxima:</div>

          <div class="row q-col-gutter-md">
            <div class="col-6">
              <q-input 
                v-model="form.next_maintenance_date" 
                label="Data *" 
                type="date" 
                outlined 
                dense 
                stack-label 
                :rules="[val => !!val || 'Obrigatório']"
              />
            </div>
            <div class="col-6">
              <q-input 
                v-model.number="form.next_maintenance_km" 
                label="KM ou Horas *" 
                type="number" 
                outlined 
                dense 
                :rules="[val => !!val || 'Obrigatório']"
              />
            </div>
          </div>
          
          <div class="text-caption text-grey-7 q-mt-xs" v-if="currentUsage">
             Leitura Atual do Veículo: {{ currentUsage }}
          </div>

          <q-card-actions align="right" class="q-mt-md">
            <q-btn flat label="Cancelar" v-close-popup color="grey-8" />
            <q-btn unelevated label="Concluir e Agendar" type="submit" color="positive" />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
// CORREÇÃO: Uso de 'import type' para interfaces
import type { MaintenanceRequest, MaintenanceRequestUpdate } from 'src/models/maintenance-models';
import { MaintenanceStatus } from 'src/models/maintenance-models';

const props = defineProps<{
  modelValue: boolean;
  request: MaintenanceRequest | null;
}>();

const emit = defineEmits(['update:modelValue', 'confirm']);

const form = ref<MaintenanceRequestUpdate>({
  status: MaintenanceStatus.CONCLUIDA,
  manager_notes: '',
  next_maintenance_date: '',
  next_maintenance_km: null
});

// Calcula sugestão baseada no veículo atual (Ex: +10.000km ou +6 meses)
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.request?.vehicle) {
    const v = props.request.vehicle;
    
    // Tenta sugerir +90 dias
    const today = new Date();
    today.setDate(today.getDate() + 90); 
    
    // CORREÇÃO: Garante string ou null para satisfazer a tipagem estrita
    const dateStr = today.toISOString().split('T')[0];
    form.value.next_maintenance_date = dateStr || null;
    
    // Tenta sugerir KM (Se for KM: +10000, Se for Horas: +250)
    const current = v.current_km || v.current_engine_hours || 0;
    form.value.next_maintenance_km = current + 5000; // Valor padrão de exemplo
    
    form.value.manager_notes = props.request.manager_notes || '';
  }
});

const currentUsage = computed(() => {
    if (!props.request?.vehicle) return '';
    const v = props.request.vehicle;
    return v.current_km ? `${v.current_km} Km` : (v.current_engine_hours ? `${v.current_engine_hours} Horas` : '0');
});

function onSubmit() {
  emit('confirm', { ...form.value });
  emit('update:modelValue', false);
}
</script>