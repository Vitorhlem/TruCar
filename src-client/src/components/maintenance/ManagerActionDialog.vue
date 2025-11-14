<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)">
    <q-card style="width: 800px; max-width: 90vw;" class="rounded-borders" v-if="request">
      <q-card-section class="bg-primary text-white">
        <div class="text-h6">Chamado #{{ request.id }}: {{ request.vehicle?.brand }} {{ request.vehicle?.model }}</div>
        <div class="text-subtitle2">Solicitado por {{ request.reporter?.full_name || 'N/A' }}</div>
      </q-card-section>

      <q-card-section v-if="authStore.isManager && !isClosed" class="bg-black-9">
        <div class="text-weight-medium q-mb-sm">Ações do Gestor</div>
        <div class="row q-gutter-sm">
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.APROVADA)" color="primary" label="Aprovar" dense unelevated icon="thumb_up" />
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.EM_ANDAMENTO)" color="info" label="Em Andamento" dense unelevated icon="engineering" />
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.CONCLUIDA)" color="positive" label="Concluir" dense unelevated icon="check_circle" />
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.REJEITADA)" color="negative" label="Rejeitar" dense unelevated icon="thumb_down" />
        </div>
      </q-card-section>
      
      <q-scroll-area style="height: 400px;">
        <q-card-section>
          <q-list bordered separator>
            <q-item><q-item-section><q-item-label caption>Veículo</q-item-label><q-item-label>{{ request.vehicle?.brand }} {{ request.vehicle?.model }} ({{ request.vehicle?.license_plate || request.vehicle?.identifier }})</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>Categoria</q-item-label><q-item-label>{{ request.category }}</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>Problema Reportado</q-item-label><q-item-label class="text-body2" style="white-space: pre-wrap;">{{ request.problem_description }}</q-item-label></q-item-section></q-item>
          </q-list>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-subtitle1 q-mb-sm">Histórico / Chat</div>
          <q-chat-message
            v-for="comment in request.comments"
            :key="comment.id"
            :name="comment.user.full_name"
            :sent="comment.user.id === authStore.user?.id"
            text-color="white"
            :bg-color="comment.user.id === authStore.user?.id ? 'primary' : 'grey'"
          >
            <div>{{ comment.comment_text }}</div>
          </q-chat-message>
        </q-card-section>
      </q-scroll-area>
      
      <q-separator />

      <q-card-section v-if="!isClosed" class="bg-black-9">
        <q-input v-model="newCommentText" outlined bg-color="white" placeholder="Digite sua mensagem..." dense autogrow @keydown.enter.prevent="postComment">
          <template v-slot:after>
            <q-btn @click="postComment" round dense flat icon="send" color="primary" :disable="!newCommentText.trim()" />
          </template>
        </q-input>
      </q-card-section>

      <q-card-section v-else class="text-center text-grey-7 q-pa-lg">
        <q-icon name="lock" size="2em" />
        <div v-if="request.updated_at">Este chamado foi finalizado em {{ new Date(request.updated_at).toLocaleDateString('pt-BR') }} e não pode mais ser alterado.</div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useAuthStore } from 'stores/auth-store';
import { MaintenanceStatus, type MaintenanceRequest, type MaintenanceRequestUpdate, type MaintenanceCommentCreate } from 'src/models/maintenance-models';

const props = defineProps<{
  modelValue: boolean,
  request: MaintenanceRequest | null
}>();
const emit = defineEmits(['update:modelValue']);

const $q = useQuasar();
const maintenanceStore = useMaintenanceStore();
const authStore = useAuthStore();
const newCommentText = ref('');

const isClosed = computed(() => 
  props.request?.status === MaintenanceStatus.CONCLUIDA ||
  props.request?.status === MaintenanceStatus.REJEITADA
);

async function postComment() {
  if (!props.request || !newCommentText.value.trim()) return;
  const payload: MaintenanceCommentCreate = { comment_text: newCommentText.value };
  await maintenanceStore.addComment(props.request.id, payload);
  newCommentText.value = '';
}

function handleUpdateStatus(newStatus: MaintenanceStatus) {
  if (!props.request) return;

  const performUpdate = async (notes?: string) => {
    if (!props.request) return;
    const payload: MaintenanceRequestUpdate = { 
      status: newStatus,
      manager_notes: notes ?? props.request.manager_notes,
    };
    await maintenanceStore.updateRequest(props.request.id, payload);
    if (newStatus === MaintenanceStatus.CONCLUIDA || newStatus === MaintenanceStatus.REJEITADA) {
      emit('update:modelValue', false);
    }
  };

  if (newStatus === MaintenanceStatus.CONCLUIDA || newStatus === MaintenanceStatus.REJEITADA) {
    $q.dialog({
      title: 'Anotações Finais (Opcional)',
      message: 'Adicione uma nota de conclusão para este chamado.',
      prompt: { model: props.request.manager_notes || '', type: 'textarea' },
      cancel: true,
      persistent: false,
    }).onOk((data: string) => {
      void performUpdate(data);
    });
  } else {
    void performUpdate();
  }
}
</script>