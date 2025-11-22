<template>
  <q-page padding>
    
    <div v-if="isDemo" class="q-mb-lg animate-fade">
      <div class="row">
        <div class="col-12">
          <q-card flat bordered class="">
            <q-card-section>
              <div class="row items-center justify-between no-wrap">
                <div class="col">
                  <div class="text-subtitle2 text-uppercase text-grey-8">Capacidade do Inventário</div>
                  <div class="text-h4 text-primary text-weight-bold q-mt-sm">
                    {{ demoUsageCount }} <span class="text-h6 text-grey-6">/ {{ demoUsageLimitLabel }} Itens</span>
                  </div>
                  <div class="text-caption text-grey-7 q-mt-sm">
                    <q-icon name="info" />
                    Você cadastrou {{ usagePercentage }}% dos modelos de peças permitidos no plano Demo.
                  </div>
                </div>
                <div class="col-auto q-ml-md">
                  <q-circular-progress
                    show-value
                    font-size="16px"
                    :value="usagePercentage"
                    size="70px"
                    :thickness="0.22"
                    :color="usageColor"
                    track-color="grey-3"
                  >
                    {{ usagePercentage }}%
                  </q-circular-progress>
                </div>
              </div>
              <q-linear-progress :value="usagePercentage / 100" class="q-mt-md" :color="usageColor" rounded />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between q-mb-md">
      <div>
        <h1 class="text-h4 text-weight-bold q-my-none">Inventário</h1>
        <div class="text-subtitle1 text-grey-7">Controle o seu estoque de peças, fluídos e consumíveis.</div>
      </div>
      
      <div class="d-inline-block relative-position">
        <q-btn 
          color="primary" 
          icon="add" 
          label="Adicionar Novo Item" 
          unelevated 
          @click="openDialog()"
          :disable="isLimitReached"
        />
        
        <q-tooltip 
          v-if="isLimitReached" 
          class="bg-negative text-body2 shadow-4" 
          anchor="bottom middle" 
          self="top middle"
          :offset="[10, 10]"
        >
          <div class="row items-center no-wrap">
              <q-icon name="lock" size="sm" class="q-mr-sm" />
              <div>
                  <div class="text-weight-bold">Capacidade Atingida</div>
                  <div class="text-caption">O plano Demo permite até {{ demoUsageLimitLabel }} cadastros.</div>
                  <div class="text-caption q-mt-xs text-yellow-2 cursor-pointer" @click="showComparisonDialog = true">Clique para saber mais</div>
              </div>
          </div>
        </q-tooltip>
      </div>
    </div>

    <q-card flat bordered>
      <q-table
        :rows="partStore.parts"
        :columns="columns"
        row-key="id"
        :loading="partStore.isLoading"
        no-data-label="Nenhum item encontrado no inventário."
        flat
        :rows-per-page-options="[10, 20, 50]"
      >
        <template v-slot:top>
          <q-input dense debounce="300" v-model="searchQuery" placeholder="Procurar por nome, marca ou código..." style="width: 300px;">
            <template v-slot:append> <q-icon name="search" /> </template>
          </q-input>
        </template>
        
        <template v-slot:body-cell-photo_url="props">
          <q-td :props="props">
            <q-avatar 
              rounded 
              size="60px" 
              font-size="32px" 
              color="grey-3" 
              text-color="grey-6"
              :icon="props.value ? undefined : getCategoryIcon(props.row.category)"
            >
              <img 
                v-if="props.value" 
                :src="getImageUrl(props.value)" 
                alt="Foto do item"
                style="object-fit: contain; width: 100%; height: 100%;"
              >
            </q-avatar>
          </q-td>
        </template>

        <template v-slot:body-cell-stock="props">
          <q-td :props="props">
            <q-chip :color="getStockColor(props.row.stock, props.row.minimum_stock)" text-color="white" class="text-weight-bold" square>
              {{ props.row.stock }} / {{ props.row.minimum_stock }}
            </q-chip>
          </q-td>
        </template>

        <template v-slot:body-cell-value="props">
          <q-td :props="props">
            {{ props.value ? props.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'N/A' }}
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn-dropdown unelevated color="primary" label="Ações" dense>
              <q-list dense>
                <q-item clickable v-close-popup @click="openStockDialog(props.row)">
                  <q-item-section avatar><q-icon name="sync_alt" /></q-item-section>
                  <q-item-section>Gerenciar Itens</q-item-section> </q-item>
                <q-item clickable v-close-popup @click="openHistoryDialog(props.row)">
                  <q-item-section avatar><q-icon name="history" /></q-item-section>
                  <q-item-section>Ver Histórico</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="openDialog(props.row)">
                  <q-item-section avatar><q-icon name="edit" /></q-item-section>
                  <q-item-section>Editar Item</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="confirmDelete(props.row)">
                  <q-item-section avatar><q-icon name="delete" color="negative" /></q-item-section>
                  <q-item-section><q-item-label class="text-negative">Excluir Item</q-item-label></q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 700px; max-width: 95vw;">
        <q-card-section class="bg-primary text-white q-py-lg">
          <div class="text-h5 text-weight-bold text-center">Controle Total do Estoque</div>
          <div class="text-subtitle1 text-center text-blue-2">Veja as vantagens do upgrade</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat separator="horizontal">
            <thead>
              <tr class="bg-grey-1 text-uppercase text-grey-7">
                <th class="text-left q-pa-md">Funcionalidade</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="inventory_2" color="grey-6" size="xs" /> Cadastro de Itens</td>
                <td class="text-center bg-amber-1 text-amber-10">Até {{ demoUsageLimitLabel }}</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="qr_code" color="grey-6" size="xs" /> Rastreio por Serial</td>
                <td class="text-center bg-amber-1 text-amber-10">Limitado</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Completo</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="history" color="grey-6" size="xs" /> Histórico de Movimentação</td>
                <td class="text-center bg-amber-1 text-amber-10">7 dias</td>
                <td class="text-center text-primary text-weight-bold"><q-icon name="check_circle" /> Vitalício</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg bg-grey-1">
          <div class="text-center full-width">
            <div class="text-grey-7 q-mb-md">Precisa gerenciar um almoxarifado maior?</div>
            <q-btn color="primary" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width" />
            <q-btn flat color="grey-7" label="Continuar no Demo" class="q-mt-sm" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isDialogOpen" >
      <q-card style="width: 700px; max-width: 90vw;">
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">{{ isEditing ? 'Editar Item (Template)' : 'Adicionar Novo Item' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="resetForm" />
          </q-card-section>

          <q-card-section class="row q-col-gutter-md">
            <div class="col-12 col-md-7 q-gutter-y-md">
              <q-input outlined v-model="formData.name" label="Nome do Item *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-select outlined v-model="formData.category" :options="categoryOptions" label="Categoria *" :rules="[val => !!val || 'Campo obrigatório']" />
              <q-input v-if="formData.category === 'Pneu'" outlined v-model="formData.serial_number" label="Nº de Série / Fogo *" :rules="[val => !!val || 'Obrigatório para pneus']" />
              <q-input 
                v-if="formData.category === 'Pneu'" 
                outlined 
                v-model.number="formData.lifespan_km" 
                type="number" 
                :label="lifespanLabel" 
                :hint="`Unidade de durabilidade esperada para gerar alertas`" 
                clearable 
              />
              <q-input outlined v-model.number="formData.value" type="number" label="Custo do Item (R$)" prefix="R$" step="0.01" />
              <q-input outlined v-model="formData.part_number" label="Código / Part Number" />
              <q-input outlined v-model="formData.brand" label="Marca" />
              <q-input outlined v-model="formData.location" label="Localização (Ex: Prateleira A-03)" />
            </div>
            
            <div class="col-12 col-md-5 q-gutter-y-md">
              <q-file v-model="photoFile" label="Foto do Item" outlined clearable accept=".jpg, .jpeg, .png, .webp, .avif">
                <template v-slot:prepend><q-icon name="photo_camera" /></template>
              </q-file>
              <q-file v-model="invoiceFile" label="Nota Fiscal (PDF)" outlined clearable accept=".pdf">
                <template v-slot:prepend><q-icon name="attach_file" /></template>
              </q-file>
              <q-img v-if="!photoFile && formData.photo_url" :src="getImageUrl(formData.photo_url)" class="q-mt-md rounded-borders" style="height: 120px; max-width: 100%" fit="contain" />
            </div>

            <div class="col-12 col-sm-6">
              <q-input 
                outlined 
                v-model.number="formData.initial_quantity" 
                type="number" 
                label="Quantidade Inicial *" 
                :disable="isEditing" 
                :hint="isEditing ? 'Use as Ações para adicionar mais itens' : 'Nº de itens a criar'" 
                :rules="[val => val >= 0 || 'Valor inválido']" 
              />
            </div>
            <div class="col-12 col-sm-6">
              <q-input outlined v-model.number="formData.minimum_stock" type="number" label="Estoque Mínimo *" :rules="[val => val >= 0 || 'Valor inválido']" />
            </div>
            <div class="col-12">
                <q-input outlined v-model="formData.notes" type="textarea" label="Notas (Opcional)" autogrow />
            </div>
          </q-card-section>
          
          <q-card-actions align="right" class="q-pa-md">
            <q-btn label="Cancelar" flat @click="resetForm" v-close-popup />
            <q-btn :label="isEditing ? 'Salvar Alterações' : 'Adicionar Item'" type="submit" color="primary" unelevated :loading="partStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <ManageStockDialog v-model="isStockDialogOpen" :part="selectedPart" />
    <PartHistoryDialog v-model="isHistoryDialogOpen" :part="selectedPart" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useQuasar, type QTableProps } from 'quasar';
import { usePartStore, type PartCreatePayload } from 'stores/part-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useDemoStore } from 'stores/demo-store';
import { useAuthStore } from 'stores/auth-store';
import type { Part, PartCategory } from 'src/models/part-models';
import ManageStockDialog from 'components/ManageStockDialog.vue';
import PartHistoryDialog from 'components/PartHistoryDialog.vue';
import api from 'src/services/api';

const $q = useQuasar();
const partStore = usePartStore();
const terminologyStore = useTerminologyStore();
const authStore = useAuthStore();
const demoStore = useDemoStore();

const isDialogOpen = ref(false);
const isStockDialogOpen = ref(false);
const isHistoryDialogOpen = ref(false);
const selectedPart = ref<Part | null>(null);

const editingPart = ref<Part | null>(null);
const isEditing = computed(() => !!editingPart.value);
const searchQuery = ref('');
const photoFile = ref<File | null>(null);
const invoiceFile = ref<File | null>(null);

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

// --- LÓGICA DEMO E LIMITES (ATUALIZADA PARA 15) ---
const showComparisonDialog = ref(false);

const demoUsageCount = computed(() => demoStore.stats?.part_count ?? 0);
// Prioriza o limite vindo do backend (Store), senão usa o fallback de 15 (conforme config.py)
const demoUsageLimit = computed(() => demoStore.stats?.part_limit ?? authStore.user?.organization?.part_limit ?? 15);
const demoUsageLimitLabel = computed(() => {
    const limit = demoUsageLimit.value;
    return (limit === undefined || limit === null || limit < 0) ? 'Ilimitado' : limit.toString();
});

const isLimitReached = computed(() => {
  if (!isDemo.value) return false;
  const limit = demoUsageLimit.value;
  if (limit === undefined || limit === null || limit < 0) return false;
  return demoUsageCount.value >= limit;
});

const usagePercentage = computed(() => {
  if (!isDemo.value || demoUsageLimit.value <= 0) return 0;
  const pct = Math.round((demoUsageCount.value / demoUsageLimit.value) * 100);
  return Math.min(pct, 100);
});

const usageColor = computed(() => {
  if (usagePercentage.value >= 100) return 'negative';
  if (usagePercentage.value >= 80) return 'warning';
  return 'primary';
});
// --- FIM LÓGICA DEMO ---

const categoryOptions: PartCategory[] = ["Peça", "Pneu", "Fluído", "Consumível", "Outro"];

const lifespanLabel = computed(() => {
  const unit = terminologyStore.distanceUnit.toUpperCase();
  return `Vida Útil em ${unit} (Opcional)`;
});

const initialFormData: PartCreatePayload = {
  name: '',
  category: 'Peça' as PartCategory,
  part_number: '',
  brand: '',
  initial_quantity: 0,
  minimum_stock: 0,
  location: '',
  notes: '',
  photo_url: null,
  value: null,
  invoice_url: null,
  serial_number: null,
  lifespan_km: null,
};
const formData = ref({ ...initialFormData });

const columns: QTableProps['columns'] = [
  { name: 'photo_url', label: 'Foto', field: 'photo_url', align: 'center' },
  { name: 'name', label: 'Item (Template)', field: 'name', align: 'left', sortable: true },
  { name: 'category', label: 'Categoria', field: 'category', align: 'left', sortable: true },
  { name: 'value', label: 'Custo Unitário', field: 'value', align: 'right', sortable: true },
  { name: 'stock', label: 'Estoque (Disp.)', field: 'stock', align: 'center', sortable: true },
  { name: 'location', label: 'Localização', field: 'location', align: 'left' },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'center' },
];

function getImageUrl(path: string | null): string {
  if (!path) return '';
  const baseUrl = api.defaults.baseURL || '';
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  return `${cleanBaseUrl}${cleanPath}`;
}

watch(searchQuery, () => {
  void partStore.fetchParts(searchQuery.value);
});

function getStockColor(current: number, min: number): string {
  if (current <= 0) return 'negative';
  if (current <= min) return 'warning';
  return 'positive';
}

function getCategoryIcon(category: PartCategory): string {
  const iconMap: Record<PartCategory, string> = {
    'Peça': 'settings', 'Fluído': 'opacity', 'Consumível': 'inbox', 'Outro': 'category', 'Pneu': 'album',
  };
  return iconMap[category] || 'inventory_2';
}

function resetForm() {
  editingPart.value = null;
  formData.value = { ...initialFormData };
  photoFile.value = null;
  invoiceFile.value = null;
}

function openDialog(part: Part | null = null) {
  if (part) {
    editingPart.value = { ...part };
    formData.value = {
      ...initialFormData,
      ...part,
      initial_quantity: 0, 
    };
  } else {
    // Bloqueio ao tentar abrir o diálogo de criação se o limite foi atingido
    if (isLimitReached.value) {
        showComparisonDialog.value = true;
        return;
    }
    resetForm();
  }
  isDialogOpen.value = true;
}

function openStockDialog(part: Part) {
  selectedPart.value = part;
  isStockDialogOpen.value = true;
}

function openHistoryDialog(part: Part) {
  selectedPart.value = part;
  void partStore.fetchHistory(part.id);
  isHistoryDialogOpen.value = true;
}

async function handleSubmit() {
  const payload: PartCreatePayload = { ...formData.value };
  if (photoFile.value) {
    payload.photo_file = photoFile.value;
  }
  if (invoiceFile.value) {
    payload.invoice_file = invoiceFile.value;
  }
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  delete (payload as any).stock; 
  
  const success = isEditing.value && editingPart.value
    ? await partStore.updatePart(editingPart.value.id, payload)
    : await partStore.createPart(payload);
  
  if (success) {
    isDialogOpen.value = false;
    resetForm();
    // Atualiza stats após criação bem sucedida
    if (authStore.isDemo && !isEditing.value) {
        void demoStore.fetchDemoStats(true);
    }
  }
}

function confirmDelete(part: Part) {
  if (part.stock > 0) {
     $q.dialog({
      title: 'Ação Bloqueada',
      message: `O item "${part.name}" ainda possui ${part.stock} unidades em estoque. Para excluí-lo, você deve primeiro remover ou dar baixa em todos os itens físicos associados através da opção "Gerenciar Itens".`,
      persistent: true,
      ok: { label: 'Entendi', color: 'primary' }
    });
    return;
  }

  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja remover o modelo "${part.name}"? Esta ação é irreversível.`,
    cancel: true,
    persistent: false,
    ok: { label: 'Tentar Excluir', color: 'negative', unelevated: true },
  }).onOk(() => {
    // CORREÇÃO: Usar partStore e part.id
    void (async () => {
      await partStore.deletePart(part.id);
      if (authStore.isDemo) { 
          await demoStore.fetchDemoStats(true); 
      }
    })();
  });
}

onMounted(() => {
  void partStore.fetchParts();
  if (authStore.isDemo) {
    void demoStore.fetchDemoStats();
  }
});
</script>