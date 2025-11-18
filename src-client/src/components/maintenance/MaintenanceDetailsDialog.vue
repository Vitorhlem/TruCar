<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="(val) => emit('update:modelValue', val)"
  >
    <q-card
      style="width: 800px; max-width: 90vw"
      class="rounded-borders"
      v-if="request"
    >
      <q-card-section class="bg-primary text-white">
        <div class="text-h6">
          Chamado #{{ request.id }}: {{ request.vehicle?.brand }}
          {{ request.vehicle?.model }}
        </div>
        <div class="text-subtitle2">
          Solicitado por {{ request.reporter?.full_name || 'N/A' }}
          <q-badge color="orange" text-color="black" class="q-ml-sm">
             {{ request.maintenance_type || 'CORRETIVA' }}
          </q-badge>
        </div>
      </q-card-section>

      <q-card-section v-if="authStore.isManager && !isClosed" class="">
        <div class="text-weight-medium q-mb-sm">Ações do Gestor</div>
        <div class="row q-gutter-sm">
          <q-btn
            @click="() => handleUpdateStatus(MaintenanceStatus.APROVADA)"
            color="primary"
            label="Aprovar"
            dense
            unelevated
            icon="thumb_up"
          />
          <q-btn
            @click="() => handleUpdateStatus(MaintenanceStatus.EM_ANDAMENTO)"
            color="info"
            label="Em Andamento"
            dense
            unelevated
            icon="engineering"
          />
          <q-btn
            @click="() => handleUpdateStatus(MaintenanceStatus.CONCLUIDA)"
            color="positive"
            label="Concluir"
            dense
            unelevated
            icon="check_circle"
          />
          <q-btn
            @click="() => handleUpdateStatus(MaintenanceStatus.REJEITADA)"
            color="negative"
            label="Rejeitar"
            dense
            unelevated
            icon="thumb_down"
          />
        </div>
      </q-card-section>

      <q-tabs
        v-model="tab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="details" label="Detalhes e Histórico" />
        <q-tab name="components" label="Componentes do Veículo" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        
        <q-tab-panel name="details">
          <q-scroll-area style="height: 400px">
            <q-card-section>
              <q-list bordered separator>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Veículo</q-item-label>
                    <q-item-label>
                      {{ request.vehicle?.brand }} {{ request.vehicle?.model }} 
                      ({{ request.vehicle?.license_plate || request.vehicle?.identifier }})
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Categoria</q-item-label>
                    <q-item-label>{{ request.category }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Problema Reportado</q-item-label>
                    <q-item-label class="text-body2" style="white-space: pre-wrap">
                      {{ request.problem_description }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>

            <q-card-section
              v-if="request.part_changes && request.part_changes.length > 0"
              class="q-pt-none"
            >
              <div class="text-subtitle1 q-mb-sm">Histórico de Substituições</div>
              <q-timeline color="primary" dense>
                <q-timeline-entry
                  v-for="log in request.part_changes"
                  :key="log.id"
                  :subtitle="new Date(log.timestamp).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })"
                  :title="`Troca realizada por ${log.user.full_name}`"
                  icon="build"
                >
                  <div :style="log.is_reverted ? 'text-decoration: line-through; opacity: 0.7;' : ''">
                    <div v-if="log.component_removed">
                      <q-badge color="negative" class="q-mr-xs">SAIU</q-badge>
                      <strong>{{ log.component_removed.part?.name || 'Peça Desconhecida' }}</strong>
                      (Cód. Item: {{ log.component_removed.inventory_transaction?.item?.item_identifier || 'N/A' }})
                    </div>
                    <div v-else>
                         <q-badge color="info" class="q-mr-xs">NOVO</q-badge>
                         Instalação direta (Nenhuma peça removida)
                    </div>

                    <div class="q-mt-xs">
                      <q-badge color="positive" class="q-mr-xs">ENTROU</q-badge>
                      <strong>{{ log.component_installed?.part?.name || 'Peça Desconhecida' }}</strong>
                      (Cód. Item: {{ log.component_installed?.inventory_transaction?.item?.item_identifier || 'N/A' }})
                    </div>
                    
                    <div v-if="log.notes" class="text-caption text-grey-7 q-mt-sm">
                      <strong>Nota:</strong> {{ log.notes }}
                    </div>
                  </div>

                  <div class="q-mt-sm" v-if="authStore.isManager && !isClosed">
                    <q-badge v-if="log.is_reverted" color="grey-7" label="Revertido" icon="undo" />
                    <q-btn
                      v-else
                      label="Reverter esta troca"
                      color="negative"
                      flat
                      dense
                      size="sm"
                      icon="undo"
                      @click="onRevert(log)"
                      :loading="maintenanceStore.isLoading"
                    />
                  </div>
                </q-timeline-entry>
              </q-timeline>
            </q-card-section>

            <q-card-section class="q-pt-none">
              <div class="text-subtitle1 q-mb-sm">Histórico / Chat</div>
              <q-chat-message
                v-for="comment in request.comments"
                :key="comment.id"
                :name="comment.user?.full_name || 'Usuário removido'"
                :sent="comment.user?.id === authStore.user?.id"
                text-color="white"
                :bg-color="comment.user?.id === authStore.user?.id ? 'primary' : 'grey-7'"
              >
                <div style="white-space: pre-wrap">{{ comment.comment_text }}</div>
              </q-chat-message>
            </q-card-section>
          </q-scroll-area>
        </q-tab-panel>

        <q-tab-panel name="components">
          <div class="row justify-end q-mb-md">
            <q-btn
              label="Instalar Novo Componente"
              icon="add_circle"
              color="positive"
              unelevated
              @click="isInstallDialogOpen = true"
              :disable="!authStore.isManager || isClosed"
            />
          </div>

          <q-table
            title="Componentes Atualmente Instalados"
            :rows="componentStore.components"
            :columns="componentColumns"
            row-key="id"
            :loading="componentStore.isLoading"
            no-data-label="Nenhum componente ativo encontrado neste veículo."
            flat
            bordered
            dense
            style="height: 400px"
            virtual-scroll
          >
            <template v-slot:body-cell-component_and_item="props">
              <q-td :props="props">
                <div class="text-weight-medium">
                  {{ props.row.part?.name || 'Peça N/A' }}
                </div>
                <div class="text-caption text-grey">
                  Cód. Item: {{ props.row.inventory_transaction?.item?.item_identifier || 'N/A' }}
                </div>
              </q-td>
            </template>

            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn
                  label="Substituir"
                  color="primary"
                  flat
                  dense
                  @click="openReplaceDialog(props.row)"
                  :disable="!authStore.isManager || isClosed"
                />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>

      <q-separator />

      <q-card-section v-if="tab === 'details' && !isClosed" class="">
        <q-input
          v-model="newCommentText"
          outlined
          bg-color=""
          placeholder="Digite sua mensagem..."
          dense
          autogrow
          @keydown.enter.prevent="postComment"
        >
          <template v-slot:after>
            <q-btn
              @click="postComment"
              round
              dense
              flat
              icon="send"
              color="primary"
              :disable="!newCommentText.trim()"
            />
          </template>
        </q-input>
      </q-card-section>

      <q-card-section v-if="isClosed" class="text-center text-grey-7 q-pa-lg">
        <q-icon name="lock" size="2em" />
        <div v-if="request.updated_at">
          Este chamado foi finalizado em
          {{ new Date(request.updated_at).toLocaleDateString('pt-BR') }} e não
          pode mais ser alterado.
        </div>
      </q-card-section>
    </q-card>

    <ReplaceComponentDialog
      v-model="isReplaceDialogOpen"
      :maintenance-request="request"
      :component-to-replace="selectedComponent"
      @replacement-done="handleReplacementDone"
    />
    
    <InstallComponentDialog
      v-model="isInstallDialogOpen"
      :maintenance-request="request"
      @installation-done="handleReplacementDone" 
    />

    <FinishMaintenanceDialog
      v-model="showFinishDialog"
      :request="request"
      @confirm="onFinishConfirmed"
    />

  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useQuasar, type QTableColumn } from 'quasar';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useAuthStore } from 'stores/auth-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store';
import {
  MaintenanceStatus,
  type MaintenanceRequest,
  type MaintenanceRequestUpdate,
  type MaintenanceCommentCreate,
  type MaintenancePartChangePublic,
} from 'src/models/maintenance-models';
import type { VehicleComponent } from 'src/models/vehicle-component-models';

// Imports dos Diálogos
import ReplaceComponentDialog from './ReplaceComponentDialog.vue';
import InstallComponentDialog from './InstallComponentDialog.vue';
import FinishMaintenanceDialog from './FinishMaintenanceDialog.vue';

const props = defineProps<{
  modelValue: boolean;
  request: MaintenanceRequest | null;
}>();
const emit = defineEmits(['update:modelValue']);

const $q = useQuasar();
const maintenanceStore = useMaintenanceStore();
const authStore = useAuthStore();
const componentStore = useVehicleComponentStore();

const newCommentText = ref('');
const tab = ref('details');

// Estados dos Diálogos
const isReplaceDialogOpen = ref(false);
const isInstallDialogOpen = ref(false);
const showFinishDialog = ref(false);

const selectedComponent = ref<VehicleComponent | null>(null);

// Configuração da Tabela
const componentColumns: QTableColumn<VehicleComponent>[] = [
  {
    name: 'component_and_item',
    label: 'Componente / Cód. Item',
    field: () => '',
    align: 'left',
    sortable: true,
  },
  {
    name: 'installation_date',
    label: 'Instalado em',
    field: 'installation_date',
    format: (val) => new Date(val).toLocaleDateString('pt-BR'),
    align: 'left',
    sortable: true,
  },
  { name: 'actions', label: 'Ações', field: () => '', align: 'center' },
];

const isClosed = computed(
  () =>
    props.request?.status === MaintenanceStatus.CONCLUIDA ||
    props.request?.status === MaintenanceStatus.REJEITADA
);

// === AÇÕES BÁSICAS ===

async function postComment() {
  if (!props.request || !newCommentText.value.trim()) return;
  const payload: MaintenanceCommentCreate = {
    comment_text: newCommentText.value,
  };
  await maintenanceStore.addComment(props.request.id, payload);
  newCommentText.value = '';
}

function openReplaceDialog(component: VehicleComponent) {
  selectedComponent.value = component;
  isReplaceDialogOpen.value = true;
}

function handleReplacementDone() {
  // Recarrega a lista de componentes do veículo para refletir a troca/instalação
  if (props.request?.vehicle?.id) {
    void componentStore.fetchComponents(props.request.vehicle.id);
  }
}

// === LÓGICA DE REVERSÃO (Segura) ===

function onRevert(log: MaintenancePartChangePublic) {
  if (!props.request) return;

  // Verificação de segurança: componente instalado deve existir
  if (!log.component_installed) {
      console.error("Componente instalado não encontrado no log.");
      return;
  }

  const partName = log.component_installed.part?.name || 'N/A';
  const itemIdentifier = log.component_installed.inventory_transaction?.item?.item_identifier || 'N/A';

  $q.dialog({
    title: 'Reverter Troca',
    message: `Tem certeza que deseja reverter esta troca? <br><br> A peça <strong>'${partName}' (Cód. Item: ${itemIdentifier})</strong> será desinstalada e retornará ao estoque como 'Disponível'.`,
    html: true,
    cancel: 'Cancelar',
    ok: 'Confirmar Reversão',
    persistent: false,
    color: 'negative',
  }).onOk(() => {
    const performRevert = async () => {
      try {
        if (!props.request) return; 
        const success = await maintenanceStore.revertPartChange(
          props.request.id,
          log.id
        );
        if (success) {
          handleReplacementDone();
        }
      } catch (error) {
        console.error('Falha ao reverter a troca:', error);
        $q.notify({
          type: 'negative',
          message: 'Ocorreu um erro ao reverter a troca.',
        });
      }
    };
    void performRevert();
  });
}

// === MUDANÇA DE STATUS DO CHAMADO ===

function handleUpdateStatus(newStatus: MaintenanceStatus) {
  if (!props.request) return;

  // Cenário 1: Concluir (Logica Condicional)
  if (newStatus === MaintenanceStatus.CONCLUIDA) {
    
    // VERIFICA SE O CHAMADO É PREVENTIVO (Vindo do Agendamento)
    // CORREÇÃO: Removido o @ts-expect-error pois a propriedade agora existe no modelo
    if (props.request.maintenance_type === 'PREVENTIVA') {
        // Se for Preventiva, abre o modal para definir a PRÓXIMA data
        showFinishDialog.value = true;
    } else {
        // Se for Corretiva (quebra), finaliza direto sem perguntar data futura
        void performDirectUpdate({ status: newStatus });
    }

  } 
  // Cenário 2: Rejeitar (Pede motivo)
  else if (newStatus === MaintenanceStatus.REJEITADA) {
    $q.dialog({
      title: 'Motivo da Rejeição',
      message: 'Por que este chamado está sendo rejeitado?',
      prompt: { model: '', type: 'textarea' },
      cancel: true,
      persistent: false,
    }).onOk((data: string) => {
       // CORREÇÃO: Uso do void para promessa não aguardada
       void performDirectUpdate({ status: newStatus, manager_notes: data });
    });
  } 
  // Cenário 3: Aprovar / Em Andamento (Direto)
  else {
    // CORREÇÃO: Uso do void para promessa não aguardada
    void performDirectUpdate({ status: newStatus, manager_notes: props.request.manager_notes });
  }
}

// Atualização simples (sem diálogo extra)
const performDirectUpdate = async (payload: MaintenanceRequestUpdate) => {
    if (!props.request) return;
    await maintenanceStore.updateRequest(props.request.id, payload);
    
    if (payload.status === MaintenanceStatus.CONCLUIDA || payload.status === MaintenanceStatus.REJEITADA) {
      emit('update:modelValue', false);
    }
};

// Chamado quando o FinishMaintenanceDialog confirma (Apenas para Preventivas)
async function onFinishConfirmed(payload: MaintenanceRequestUpdate) {
    if (!props.request) return;
    await maintenanceStore.updateRequest(props.request.id, payload);
    emit('update:modelValue', false);
}

// === WATCHERS ===

watch(
  () => tab.value,
  (newTab) => {
    if (newTab === 'components' && props.request?.vehicle?.id) {
      const storeVehicleId = componentStore.currentVehicleId;
      if (storeVehicleId !== props.request.vehicle.id) {
        void componentStore.fetchComponents(props.request.vehicle.id);
      }
    }
  }
);

watch(
  () => props.request?.id,
  (newId, oldId) => {
    if (newId !== oldId) {
      tab.value = 'details';
      if (props.request?.vehicle.id) {
        void componentStore.fetchComponents(props.request.vehicle.id);
      }
    }
  },
  { immediate: true }
);
</script>