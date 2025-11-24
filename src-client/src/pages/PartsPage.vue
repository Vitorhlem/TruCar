<template>
  <q-page class="q-pa-md q-pa-lg-xl">
    
    <div class="row items-center justify-between q-mb-lg q-col-gutter-y-md">
      <div class="col-12 col-md-auto">
        <h1 class="text-h4 text-weight-bolder q-my-none text-primary flex items-center gap-sm">
          <q-icon name="inventory_2" size="md" />
          Inventário
        </h1>
        <div class="text-subtitle2 text-grey-7 q-mt-xs" :class="{ 'text-grey-5': $q.dark.isActive }">
          Controle de peças, pneus, fluídos e consumíveis
        </div>
      </div>

      <div class="col-12 col-md-auto">
        <div class="d-inline-block relative-position">
          <q-btn 
            color="primary" 
            icon="add" 
            label="Adicionar Novo Item" 
            size="md"
            unelevated 
            class="shadow-2"
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
    </div>

    <div v-if="isDemo" class="q-mb-xl animate-fade">
      <q-card flat bordered class="demo-card-gradient">
        <q-card-section class="q-pa-md">
          <div class="row items-center justify-between">
            <div class="col-grow row items-center q-gutter-x-md">
              <q-circular-progress
                show-value
                font-size="14px"
                :value="usagePercentage"
                size="60px"
                :thickness="0.22"
                :color="usageColor"
                track-color="white"
                class="text-white q-my-xs"
              >
                {{ usagePercentage }}%
              </q-circular-progress>
              
              <div>
                <div class="text-subtitle2 text-uppercase text-white text-opacity-80">Capacidade do Inventário</div>
                <div class="text-h4 text-white text-weight-bold">
                  {{ demoUsageCount }} <span class="text-h6 text-white text-opacity-70">/ {{ demoUsageLimitLabel }} Itens</span>
                </div>
              </div>
            </div>
            
            <div class="col-auto">
               <q-btn flat dense color="white" icon="info" round>
                 <q-tooltip>Você cadastrou {{ usagePercentage }}% dos modelos de peças permitidos no plano Demo.</q-tooltip>
               </q-btn>
            </div>
          </div>
          <q-linear-progress :value="usagePercentage / 100" class="q-mt-md rounded-borders" color="white" track-color="white-30" />
        </q-card-section>
      </q-card>
    </div>

    <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-4">
            <q-card flat bordered class="full-height" :class="$q.dark.isActive ? '' : 'bg-white'">
                <q-card-section class="row items-center">
                    <div class="col">
                        <div class="text-caption text-grey text-uppercase">Valor Total Estimado</div>
                        <div class="text-h5 text-weight-bold text-primary">{{ formatCurrency(totalInventoryValue) }}</div>
                    </div>
                    <div class="col-auto">
                        <q-avatar color="primary" text-color="white" icon="attach_money" />
                    </div>
                </q-card-section>
            </q-card>
        </div>
        <div class="col-12 col-md-4">
            <q-card flat bordered class="full-height" :class="$q.dark.isActive ? '' : 'bg-white'">
                <q-card-section class="row items-center">
                    <div class="col">
                        <div class="text-caption text-grey text-uppercase">Itens em Alerta</div>
                        <div class="text-h5 text-weight-bold" :class="lowStockCount > 0 ? 'text-negative' : 'text-positive'">
                            {{ lowStockCount }} <span class="text-caption text-grey">abaixo do mínimo</span>
                        </div>
                    </div>
                    <div class="col-auto">
                        <q-avatar :color="lowStockCount > 0 ? 'red-1' : 'green-1'" :text-color="lowStockCount > 0 ? 'negative' : 'positive'" icon="notifications_active" />
                    </div>
                </q-card-section>
            </q-card>
        </div>
        <div class="col-12 col-md-4">
            <q-card flat bordered class="full-height" :class="$q.dark.isActive ? '' : 'bg-white'">
                <q-card-section class="row items-center">
                    <div class="col">
                        <div class="text-caption text-grey text-uppercase">Modelos Cadastrados</div>
                        <div class="text-h5 text-weight-bold">{{ partStore.parts.length }}</div>
                    </div>
                    <div class="col-auto">
                        <q-avatar color="grey-2" text-color="grey-8" icon="category" />
                    </div>
                </q-card-section>
            </q-card>
        </div>
    </div>

    <q-card flat bordered :class="$q.dark.isActive ? '' : 'bg-white'">
      <q-table
        :rows="partStore.parts"
        :columns="columns"
        row-key="id"
        :loading="partStore.isLoading"
        no-data-label="Nenhum item encontrado no inventário."
        flat
        :rows-per-page-options="[10, 20, 50]"
        :card-class="$q.dark.isActive ? ' text-white' : 'bg-white text-grey-9'"
        table-header-class="text-uppercase text-grey-7 bg-grey-2"
      >
        <template v-slot:top>
          <div class="row full-width items-center q-py-sm">
             <div class="col-12 col-md-6 text-h6">Listagem de Materiais</div>
             <div class="col-12 col-md-6 row justify-end">
                <q-input 
                    dense 
                    outlined
                    debounce="300" 
                    v-model="searchQuery" 
                    placeholder="Procurar por nome, marca ou código..." 
                    class="search-input"
                    :bg-color="$q.dark.isActive ? 'grey-8' : 'white'"
                >
                    <template v-slot:append> <q-icon name="search" /> </template>
                </q-input>
             </div>
          </div>
        </template>
        
        <template v-slot:header="props">
            <q-tr :props="props" :class="$q.dark.isActive ? '' : 'bg-grey-1'">
                <q-th v-for="col in props.cols" :key="col.name" :props="props" class="text-weight-bold text-primary">
                    {{ col.label }}
                </q-th>
            </q-tr>
        </template>

        <template v-slot:body-cell-photo_url="props">
          <q-td :props="props">
            <q-avatar 
              rounded 
              size="50px" 
              font-size="24px" 
              :color="$q.dark.isActive ? 'grey-8' : 'grey-3'" 
              :text-color="$q.dark.isActive ? 'grey-5' : 'grey-6'"
              class="shadow-1"
            >
              <img 
                v-if="props.value" 
                :src="getImageUrl(props.value) || ''" 
                alt="Foto"
                style="object-fit: cover;"
              >
              <q-icon v-else :name="getCategoryIcon(props.row.category)" />
            </q-avatar>
          </q-td>
        </template>

        <template v-slot:body-cell-name="props">
            <q-td :props="props">
                <div class="text-weight-medium">{{ props.row.name }}</div>
                <div class="text-caption text-grey">{{ props.row.brand }} {{ props.row.part_number ? `• #${props.row.part_number}` : '' }}</div>
            </q-td>
        </template>

        <template v-slot:body-cell-category="props">
            <q-td :props="props">
                <q-badge color="grey-3" text-color="grey-9" class="q-px-sm">
                    {{ props.row.category }}
                </q-badge>
            </q-td>
        </template>

        <template v-slot:body-cell-stock="props">
          <q-td :props="props">
            <div class="row justify-center">
                <q-badge 
                    :color="getStockColor(props.row.stock, props.row.minimum_stock)" 
                    class="q-pa-sm text-weight-bold shadow-1"
                    rounded
                >
                {{ props.row.stock }} <span class="q-ml-xs  opacity-100" style="font-size: 1em">/ {{ props.row.minimum_stock }}</span>
                </q-badge>
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-value="props">
          <q-td :props="props" class="text-weight-medium">
            {{ formatCurrency(props.value) }}
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn-dropdown unelevated color="primary" label="Ações" dense size="sm" dropdown-icon="more_vert" no-icon-animation>
              <q-list dense style="min-width: 150px">
                <q-item clickable v-close-popup @click="openStockDialog(props.row)">
                  <q-item-section avatar><q-icon name="sync_alt" color="primary" /></q-item-section>
                  <q-item-section>Movimentar</q-item-section> </q-item>
                <q-item clickable v-close-popup @click="openHistoryDialog(props.row)">
                  <q-item-section avatar><q-icon name="history" color="grey-7" /></q-item-section>
                  <q-item-section>Histórico</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="openDialog(props.row)">
                  <q-item-section avatar><q-icon name="edit" color="grey-7" /></q-item-section>
                  <q-item-section>Editar</q-item-section>
                </q-item>
                <q-item clickable v-close-popup @click="confirmDelete(props.row)">
                  <q-item-section avatar><q-icon name="delete" color="negative" /></q-item-section>
                  <q-item-section class="text-negative">Excluir</q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showComparisonDialog">
      <q-card style="width: 750px; max-width: 95vw;" :class="$q.dark.isActive ? '' : 'bg-white'">
        <q-card-section class="bg-primary text-white q-py-lg text-center relative-position overflow-hidden">
          <div class="absolute-full bg-white opacity-10" style="transform: skewY(-5deg) scale(1.5);"></div>
          <q-icon name="inventory" size="4em" class="q-mb-sm" />
          <div class="text-h4 text-weight-bold relative-position">Controle Total do Estoque</div>
          <div class="text-subtitle1 text-blue-2 relative-position">Gerencie seu almoxarifado sem limites com o PRO</div>
        </q-card-section>

        <q-card-section class="q-pa-none">
          <q-markup-table flat :dark="$q.dark.isActive" :class="$q.dark.isActive ? 'bg-transparent' : ''">
            <thead>
              <tr :class="$q.dark.isActive ? 'bg-grey-8' : 'bg-grey-1 text-grey-7'">
                <th class="text-left q-pa-md text-uppercase text-caption">Funcionalidade</th>
                <th class="text-center text-weight-bold q-pa-md bg-amber-1 text-amber-9 border-left">Plano Demo</th>
                <th class="text-center text-weight-bold q-pa-md text-primary bg-blue-1">Plano PRO</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="inventory_2" color="grey-6" size="xs" /> Cadastro de Itens</td>
                <td class="text-center bg-amber-1 text-amber-10">Até {{ demoUsageLimitLabel }}</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Ilimitado</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="qr_code" color="grey-6" size="xs" /> Rastreio por Serial</td>
                <td class="text-center bg-amber-1 text-amber-10">Limitado</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Completo</td>
              </tr>
              <tr>
                <td class="text-weight-medium q-pa-md"><q-icon name="history" color="grey-6" size="xs" /> Histórico de Movimentação</td>
                <td class="text-center bg-amber-1 text-amber-10">7 dias</td>
                <td class="text-center text-primary text-weight-bold bg-blue-1"><q-icon name="check_circle" /> Vitalício</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-lg" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-1'">
          <div class="column items-center full-width q-gutter-y-md">
            <div class="text-h6 text-weight-bold">Precisa gerenciar um almoxarifado maior?</div>
            <q-btn color="positive" label="Falar com Consultor" size="lg" unelevated icon="whatsapp" class="full-width shadow-2" />
            <q-btn flat color="grey-7" label="Continuar no Demo" v-close-popup />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isDialogOpen" persistent>
      <q-card style="width: 750px; max-width: 95vw;" :class="$q.dark.isActive ? '' : ''">
        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">{{ isEditing ? 'Editar Item (Template)' : 'Adicionar Novo Item' }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="resetForm" />
          </q-card-section>

          <q-card-section class="scroll" style="max-height: 70vh">
            <div class="row q-col-gutter-md">
                <div class="col-12 col-md-7 q-gutter-y-sm">
                    <q-input outlined dense v-model="formData.name" label="Nome do Item *" :rules="[val => !!val || 'Campo obrigatório']" />
                    
                    <div class="row q-col-gutter-sm">
                        <div class="col-6">
                            <q-select outlined dense v-model="formData.category" :options="categoryOptions" label="Categoria *" :rules="[val => !!val || 'Campo obrigatório']" />
                        </div>
                        <div class="col-6">
                            <q-input outlined dense v-model.number="formData.value" type="number" label="Custo Unit. (R$)" prefix="R$" step="0.01" />
                        </div>
                    </div>
                    
                    <q-input v-if="formData.category === 'Pneu'" outlined dense v-model="formData.serial_number" label="Nº de Série / Fogo *" :rules="[val => !!val || 'Obrigatório para pneus']" />
                    <q-input 
                        v-if="formData.category === 'Pneu'" 
                        outlined dense
                        v-model.number="formData.lifespan_km" 
                        type="number" 
                        :label="lifespanLabel" 
                        :hint="`Unidade de durabilidade esperada para gerar alertas`" 
                        clearable 
                    />
                    
                    <div class="row q-col-gutter-sm">
                        <div class="col-6">
                             <q-input outlined dense v-model="formData.part_number" label="Código / Part Number" />
                        </div>
                        <div class="col-6">
                             <q-input outlined dense v-model="formData.brand" label="Marca" />
                        </div>
                    </div>
                    
                    <q-input outlined dense v-model="formData.location" label="Localização (Ex: Prateleira A-03)" />
                </div>
                
                <div class="col-12 col-md-5 q-gutter-y-md">
                    <q-file 
                        v-model="photoFile" 
                        label="Foto do Item" 
                        outlined dense 
                        clearable 
                        accept=".jpg, .jpeg, .png, .webp, .avif"
                        @update:model-value="onFileSelected"
                    >
                        <template v-slot:prepend><q-icon name="photo_camera" /></template>
                        <template v-slot:append>
                             <q-avatar size="24px" square v-if="photoPreview || formData.photo_url">
                                <img :src="(photoPreview || getImageUrl(formData.photo_url)) || ''" style="object-fit: cover" />
                             </q-avatar>
                        </template>
                    </q-file>
                    
                    <div v-if="photoPreview || formData.photo_url" class="rounded-borders overflow-hidden bg-grey-2 flex flex-center relative-position" style="height: 140px; border: 1px dashed #ccc">
                        <q-img :src="(photoPreview || getImageUrl(formData.photo_url)) || ''" fit="contain" style="max-height: 100%; max-width: 100%" />
                    </div>
                    <div v-else class="rounded-borders bg-grey-1 flex flex-center text-grey-5" style="height: 140px; border: 1px dashed #ccc">
                        <div class="text-center">
                            <q-icon name="image" size="md" />
                            <div class="text-caption">Sem foto</div>
                        </div>
                    </div>

                    <q-file v-model="invoiceFile" label="Nota Fiscal (PDF)" outlined dense clearable accept=".pdf">
                        <template v-slot:prepend><q-icon name="attach_file" /></template>
                        <template v-slot:append>
                            <q-btn
                                v-if="!invoiceFile && formData.invoice_url"
                                flat dense round
                                icon="visibility"
                                color="primary"
                                @click.stop="openUrl(getImageUrl(formData.invoice_url))"
                            >
                                <q-tooltip>Ver Nota Fiscal Atual</q-tooltip>
                            </q-btn>
                        </template>
                    </q-file>
                    
                    <div v-if="!invoiceFile && formData.invoice_url" class="text-caption text-positive flex items-center q-ml-xs">
                        <q-icon name="check_circle" size="xs" class="q-mr-xs" />
                        Nota Fiscal já anexada
                    </div>
                </div>
            </div>
            
            <q-separator class="q-my-md" />
            
            <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-6">
                    <q-input 
                    outlined dense
                    v-model.number="formData.initial_quantity" 
                    type="number" 
                    label="Quantidade Inicial *" 
                    :disable="isEditing" 
                    :hint="isEditing ? 'Use as Ações para adicionar mais itens' : 'Nº de itens a criar'" 
                    :rules="[val => val >= 0 || 'Valor inválido']" 
                    bg-color=""
                    />
                </div>
                <div class="col-12 col-sm-6">
                    <q-input outlined dense v-model.number="formData.minimum_stock" type="number" label="Estoque Mínimo *" :rules="[val => val >= 0 || 'Valor inválido']" />
                </div>
                <div class="col-12">
                    <q-input outlined dense v-model="formData.notes" type="textarea" label="Notas (Opcional)" autogrow />
                </div>
            </div>
          </q-card-section>
          
          <q-card-actions align="right" class="q-pa-md bg-grey-1" :class="$q.dark.isActive ? 'bg-grey-8' : ''">
            <q-btn label="Cancelar" flat @click="resetForm" v-close-popup color="grey-7" />
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

// --- CONFIGURAÇÃO DE URL DE IMAGENS ---
const API_BASE_URL = 'http://localhost:8000'; 

function getImageUrl(url: string | null | undefined) {
  if (!url) return undefined;
  if (url.startsWith('http')) return url;
  return `${API_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`;
}

// --- NOVA FUNÇÃO PARA ABRIR NOTA FISCAL ---
function openUrl(url: string | undefined) {
    if (url) {
        window.open(url, '_blank');
    }
}
// -------------------------------------------

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
const photoPreview = ref<string | null>(null);
const invoiceFile = ref<File | null>(null);

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

// --- LÓGICA DEMO E LIMITES ---
const showComparisonDialog = ref(false);

const demoUsageCount = computed(() => demoStore.stats?.part_count ?? 0);
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
  if (usagePercentage.value >= 100) return 'red-4';
  if (usagePercentage.value >= 80) return 'orange-4';
  return 'white';
});

// --- KPIs ---
const totalInventoryValue = computed(() => {
    return partStore.parts.reduce((acc, part) => acc + (part.stock * (part.value || 0)), 0);
});

const lowStockCount = computed(() => {
    return partStore.parts.filter(p => p.stock <= p.minimum_stock).length;
});

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
  { name: 'photo_url', label: 'Item', field: 'photo_url', align: 'left', style: 'width: 80px' },
  { name: 'name', label: 'Descrição', field: 'name', align: 'left', sortable: true },
  { name: 'category', label: 'Categoria', field: 'category', align: 'left', sortable: true },
  { name: 'value', label: 'Custo Unit.', field: 'value', align: 'right', sortable: true },
  { name: 'stock', label: 'Estoque', field: 'stock', align: 'center', sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'right' },
];

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

function formatCurrency(val: number | null | undefined): string {
    return (val || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function onFileSelected(val: File | null) {
  if (val) {
    photoPreview.value = URL.createObjectURL(val);
  } else {
    photoPreview.value = null;
  }
}

function resetForm() {
  editingPart.value = null;
  formData.value = { ...initialFormData };
  photoFile.value = null;
  photoPreview.value = null;
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
    photoFile.value = null;
    photoPreview.value = null;
    invoiceFile.value = null; // Limpa o input de arquivo novo
  } else {
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
    if (authStore.isDemo && !isEditing.value) {
        void demoStore.fetchDemoStats(true);
    }
  }
}

function confirmDelete(part: Part) {
  if (part.stock > 0) {
     $q.dialog({
      title: 'Ação Bloqueada',
      message: `O item "${part.name}" ainda possui ${part.stock} unidades em estoque. Zere o estoque primeiro.`,
      persistent: true,
      ok: { label: 'Entendi', color: 'primary' }
    });
    return;
  }

  $q.dialog({
    title: 'Confirmar Exclusão',
    message: `Tem certeza que deseja remover o modelo "${part.name}"?`,
    cancel: true,
    persistent: false,
    ok: { label: 'Excluir', color: 'negative', unelevated: true },
  }).onOk(() => {
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

<style scoped lang="scss">
.demo-card-gradient {
  background: linear-gradient(135deg, var(--q-primary) 0%, darken($primary, 20%) 100%);
  border: none;
  border-radius: 12px;
}

.white-30 {
  color: rgba(255,255,255,0.3) !important;
}

.opacity-10 {
  opacity: 0.1;
}

.search-input {
  width: 300px;
  @media (max-width: 599px) {
    width: 100%;
  }
}

.opacity-80 {
    opacity: 0.8;
}
</style>