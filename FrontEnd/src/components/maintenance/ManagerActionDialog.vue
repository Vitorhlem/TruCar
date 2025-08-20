<template>
  <q-dialog :model-value="modelValue" @update:model-value="val => emit('update:modelValue', val)">
    <q-card style="width: 800px; max-width: 90vw;" class="rounded-borders" v-if="request">
      <q-card-section class="bg-primary text-white">
        <div class="text-h6">Chamado #{{ request.id }}: {{ request.vehicle.brand }} {{ request.vehicle.model }}</div>
        <div class="text-subtitle2">Solicitado por {{ request.reporter.full_name }}</div>
      </q-card-section>

      <q-card-section v-if="authStore.isManager && !isClosed" class="bg-grey-2">
        <div class="text-weight-medium q-mb-sm">Ações do Gestor</div>
        <div class="row q-gutter-sm">
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.APPROVED)" color="primary" label="Aprovar" dense unelevated icon="thumb_up" />
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.IN_PROGRESS)" color="info" label="Em Andamento" dense unelevated icon="engineering" />
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.COMPLETED)" color="positive" label="Concluída" dense unelevated icon="check_circle" />
          <q-btn @click="() => handleUpdateStatus(MaintenanceStatus.REJECTED)" color="negative" label="Rejeitar" dense unelevated icon="thumb_down" />
        </div>
      </q-card-section>
      
      <q-scroll-area style="height: 400px;">
        <q-card-section>
          <q-list bordered separator>
            <q-item><q-item-section><q-item-label caption>Categoria</q-item-label><q-item-label>{{ request.category }}</q-item-label></q-item-section></q-item>
            <q-item><q-item-section><q-item-label caption>Problema Reportado</q-item-label><q-item-label class="text-body2" style="white-space: pre-wrap;">{{ request.problem_description }}</q-item-label></q-item-section></q-item>
          </q-list>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-subtitle1 q-mb-sm">Histórico / Chat</div>
          <q-chat-message
            v-for="comment in maintenanceStore.comments"
            :key="comment.id"
            :name="comment.user.full_name"
            :sent="comment.user.id === authStore.user?.id"
            text-color="white"
            :bg-color="comment.user.id === authStore.user?.id ? 'primary' : 'grey-7'"
            bubble
          >
            <template v-slot:default>
              <div>{{ comment.comment_text }}</div>
              <div v-if="comment.file_url" class="q-mt-sm">
                <q-btn type="a" :href="`${apiBaseUrl}${comment.file_url}`" target="_blank" flat dense rounded icon="attach_file" label="Ver Anexo" color="white" size="sm" />
              </div>
            </template>
          </q-chat-message>
        </q-card-section>
      </q-scroll-area>
      
      <q-separator />

      <q-card-section v-if="!isClosed" class="bg-grey-2">
        <q-input
          v-model="newComment"
          outlined
          bg-color="white"
          placeholder="Digite sua mensagem..."
          dense
          autogrow
          @keydown.enter.prevent="postComment"
        >
          <template v-slot:after>
            <q-btn @click="postComment" round dense flat icon="send" color="primary" :disable="!newComment.trim()" />
          </template>
        </q-input>
        <q-uploader
          v-if="authStore.isManager"
          label="Anexar arquivos (opcional)"
          @added="onFileAdded"
          ref="uploaderRef"
          max-files="1"
          class="q-mt-sm full-width"
          flat bordered dense
          color="grey-7"
        />
      </q-card-section>
      <q-card-section v-else class="text-center text-grey-7 q-pa-lg">
        <q-icon name="lock" size="2em" />
        <div>Este chamado foi finalizado em {{ new Date(request.updated_at!).toLocaleDateString('pt-BR') }} e não pode mais ser alterado.</div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useQuasar, type QRejectedEntry, type QUploader } from 'quasar';
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
const newComment = ref('');
const uploadedFileUrl = ref<string | null>(null);
const uploaderRef = ref<QUploader | null>(null);
const apiBaseUrl = 'http://localhost:8000';

// A variável 'isClosed' agora será usada pelo template
const isClosed = computed(() => 
  props.request?.status === MaintenanceStatus.COMPLETED ||
  props.request?.status === MaintenanceStatus.REJECTED
);

watch(() => props.request, (newVal) => {
  if (newVal) {
    void maintenanceStore.fetchComments(newVal.id);
    newComment.value = '';
    uploadedFileUrl.value = null;
    uploaderRef.value?.reset();
  }
});

async function onFileAdded(files: readonly (File | QRejectedEntry)[]) {
  const file = files[0];
  if (file instanceof File) {
    const uploader = uploaderRef.value;
    if (uploader) uploader.upload();
    const url = await maintenanceStore.uploadAttachment(file);
    if (url) {
      uploadedFileUrl.value = url;
      $q.notify({ type: 'positive', message: 'Anexo pronto. Envie com um comentário.' });
    } else {
      uploader?.removeFile(file);
    }
  }
}

async function postComment() {
  if (!props.request || !newComment.value.trim()) return;
  const payload: MaintenanceCommentCreate = {
    comment_text: newComment.value,
    file_url: uploadedFileUrl.value
  };
  try {
    await maintenanceStore.addComment(props.request.id, payload);
    newComment.value = '';
    uploadedFileUrl.value = null;
    uploaderRef.value?.reset();
  } catch { /* A store já notifica o erro */ }
}

async function handleUpdateStatus(newStatus: MaintenanceStatus) {
  if (!props.request) return;
  const payload: MaintenanceRequestUpdate = { status: newStatus };
  try {
    await maintenanceStore.updateRequest(props.request.id, payload);
    $q.notify({ type: 'positive', message: `Status alterado para ${newStatus}` });
    if (newStatus === MaintenanceStatus.COMPLETED || newStatus === MaintenanceStatus.REJECTED) {
      emit('update:modelValue', false);
    }
  } catch { /* A store já notifica o erro */ }
}
</script>