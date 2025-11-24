<template>
  <q-page padding class="q-gutter-y-md">
    <div v-if="!vehicleStore.isLoading && vehicleStore.selectedVehicle">
      <q-card flat bordered class="bg-primary text-white">
        <q-card-section class="row items-center q-gutter-x-md">
          <q-avatar
            size="70px"
            font-size="40px"
            color="white"
            text-color="primary"
            icon="directions_car"
          />
          <div>
            <div class="text-caption opacity-80">Veículo Selecionado</div>
            <div class="text-h4 text-weight-bold">
              {{ vehicleStore.selectedVehicle.brand }} {{ vehicleStore.selectedVehicle.model }}
            </div>
            <div class="text-subtitle1 opacity-90 row items-center q-gutter-x-sm">
              <q-badge color="white" text-color="primary" :label="(vehicleStore.selectedVehicle.license_plate || vehicleStore.selectedVehicle.identifier) || ''" />
              <q-separator vertical dark />
              <span>
                {{ isAgro ? 'Horímetro' : 'Odômetro' }}: 
                <strong>{{ (isAgro ? vehicleStore.selectedVehicle.current_engine_hours : vehicleStore.selectedVehicle.current_km)?.toLocaleString('pt-BR') || 0 }} {{ isAgro ? 'h' : 'km' }}</strong>
              </span>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
    <div v-else class="row items-center q-gutter-x-md">
      <q-skeleton type="circle" size="70px" />
      <div class="col">
        <q-skeleton type="text" width="40%" class="text-h4" />
        <q-skeleton type="text" width="20%" class="text-subtitle1" />
      </div>
    </div>

    <q-card flat bordered>
      <q-tabs
        v-model="tab"
        dense
        class="text-grey-7"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="tires" icon="radio_button_checked" label="Gestão de Pneus" />
        <q-tab name="history" icon="history" :label="`Movimentações (${filteredHistory.length})`" />
        <q-tab name="components" icon="extension" :label="`Componentes (${filteredComponents.length})`" />
        <q-tab name="costs" icon="attach_money" :label="`Custos (${filteredCosts.length})`" />
        <q-tab name="maintenance" icon="build" :label="`Manutenções (${filteredMaintenances.length})`" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated transition-prev="fade" transition-next="fade">
        
        <q-tab-panel name="tires" class="q-pa-md">
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-12 col-sm-6 col-md-3">
              <q-card flat bordered class="full-height">
                <q-card-section class="row items-center justify-between no-wrap">
                  <div>
                    <div class="text-caption text-grey">CPK (Custo por KM)</div>
                    <div class="text-h6 text-weight-bold text-primary">
                      {{ kpiTireCostPerKm }}
                      <small v-if="kpiTireCostPerKm !== 'N/A'" class="text-caption text-grey">R$/km</small>
                    </div>
                  </div>
                  <q-icon name="trending_up" size="lg" color="primary" class="q-ml-sm opacity-50" />
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-card flat bordered class="full-height">
                <q-card-section class="row items-center justify-between no-wrap">
                  <div>
                    <div class="text-caption text-grey">Vida Útil Média</div>
                    <div class="text-h6 text-weight-bold text-secondary">
                      {{ kpiAvgTireLifespan }}
                      <small v-if="kpiAvgTireLifespan !== 'N/A'" class="text-caption text-grey">km</small>
                    </div>
                  </div>
                  <q-icon name="speed" size="lg" color="secondary" class="q-ml-sm opacity-50" />
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-card flat bordered class="full-height">
                <q-card-section class="row items-center justify-between no-wrap">
                  <div>
                    <div class="text-caption text-grey">Pneus em Alerta</div>
                    <div class="text-h6 text-weight-bold" :class="kpiTiresInAlert > 0 ? 'text-negative' : 'text-positive'">
                      {{ kpiTiresInAlert }}
                      <small class="text-caption text-grey">unid.</small>
                    </div>
                  </div>
                  <q-icon 
                    :name="kpiTiresInAlert > 0 ? 'warning' : 'check_circle'" 
                    size="lg" 
                    :color="kpiTiresInAlert > 0 ? 'negative' : 'positive'" 
                    class="q-ml-sm opacity-50" 
                  />
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-card flat bordered class="full-height">
                <q-card-section class="row items-center justify-between no-wrap">
                  <div>
                    <div class="text-caption text-grey">Custo Total (Histórico)</div>
                    <div class="text-h6 text-weight-bold ">
                      {{ kpiTotalTireCost }}
                    </div>
                  </div>
                  <q-icon name="monetization_on" size="lg" color="grey-7" class="q-ml-sm opacity-50" />
                </q-card-section>
              </q-card>
            </div>
          </div>

          <q-separator class="q-mb-md" />

          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-regular row items-center">
              <q-icon name="settings_overscan" class="q-mr-sm" color="primary" />
              Layout dos Pneus
            </div>
            <q-btn
              v-if="tireStore.tireLayout?.axle_configuration"
              label="Alterar Configuração"
              color="secondary"
              outline
              icon="settings"
              @click="isAxleConfigDialogOpen = true"
            />
          </div>

          <div class="q-mb-xl">
             <InteractiveTireLayout
              v-if="tireStore.tireLayout?.axle_configuration"
              :axle-config="tireStore.tireLayout.axle_configuration"
              :tires="tiresWithStatus"
              :is-agro="isAgro"
              @install="openInstallDialog"
              @remove="openRemoveDialog"
            />
            
            <div v-else-if="!tireStore.isLoading && !vehicleStore.isLoading && !tireStore.tireLayout?.axle_configuration" 
                 class="rounded-borders q-pa-xl text-center"
                 :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-2'"
            >
                <q-icon name="no_crash" size="4rem" color="grey-5" />
                <div class="text-h6 q-mt-md text-grey-7">Nenhuma configuração definida</div>
                <p class="text-grey-6 q-mb-md">Defina o layout de eixos para começar a gerenciar os pneus.</p>
                <q-btn
                  label="Definir Eixos Agora"
                  color="primary"
                  unelevated
                  icon="add"
                  @click="isAxleConfigDialogOpen = true"
                />
            </div>
          </div>

          <div class="text-h6 text-weight-regular q-mb-md row items-center">
              <q-icon name="analytics" class="q-mr-sm" color="primary" />
              Análise de Desempenho
            </div>
          <div class="row q-col-gutter-lg">
            <div class="col-12 col-lg-8">
              <q-table
                title="Histórico de Remoções (Descarte/Troca)"
                :rows="removedTiresHistory"
                :columns="historyTireColumns"
                row-key="id"
                flat bordered
                dense
                :class="$q.dark.isActive ? 'bg-dark' : 'bg-white'"
                no-data-label="Nenhum registro de remoção encontrado."
                :loading="isHistoryLoading"
              >
                 <template v-slot:top-right>
                    <q-btn icon="download" flat round dense color="grey" title="Exportar" />
                 </template>
              </q-table>
            </div>
            <div class="col-12 col-lg-4">
              <q-card flat bordered class="full-height">
                <q-card-section>
                  <div class="text-subtitle1 text-weight-medium">Evolução de Custos (Mensal)</div>
                  <div class="text-caption text-grey">Gastos com aquisição de pneus</div>
                </q-card-section>
                <q-card-section>
                  <TireCostChart :costs="tireCostsByMonth" />
                </q-card-section>
              </q-card>
            </div>
          </div>
          <q-inner-loading :showing="tireStore.isLoading || isHistoryLoading" label="Atualizando dados..." />
        </q-tab-panel>

        <q-tab-panel name="history">
          <div class="column q-gutter-y-md">
            <div class="row items-center justify-between wrap q-gutter-y-sm">
              <div class="text-h6 row items-center">
                <q-icon name="manage_history" class="q-mr-sm" color="primary" />
                Histórico de Movimentações
              </div>
              <div class="row items-center q-gutter-sm">
                <q-input dense outlined v-model="dateRange.history" mask="##/##/####" label="De" style="width: 140px">
                  <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.history" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Ok" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
                </q-input>
                <q-input dense outlined v-model="dateRange.historyTo" mask="##/##/####" label="Até" style="width: 140px">
                  <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.historyTo" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Ok" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
                </q-input>
                <q-input dense outlined debounce="300" v-model="search.history" placeholder="Buscar por peça..." style="width: 250px">
                  <template v-slot:prepend><q-icon name="search" /></template>
                </q-input>
                <q-btn @click="exportToCsv('history')" color="secondary" outline icon="file_download" label="CSV" />
              </div>
            </div>

            <q-table
              :rows="filteredHistory"
              :columns="historyColumns"
              row-key="id"
              :loading="isHistoryLoading"
              no-data-label="Nenhuma movimentação encontrada."
              flat bordered
              class="sticky-header-table"
            >
              <template v-slot:body-cell-part_and_item="props">
                <q-td :props="props">
                  <div class="text-weight-medium">{{ getPartName(props.row.item?.part_id || props.row.part?.id) }}</div>
                  <div v-if="props.row.item" class="text-caption text-grey">
                    Cód: <a href="#" @click.prevent="goToItemDetails(props.row.item.id)" class="text-primary link-hover">{{ props.row.item.item_identifier }}</a>
                  </div>
                  <span v-else class="text-caption text-grey-5">(Sem identificador)</span>
                </q-td>
              </template>
              
               <template v-slot:body-cell-transaction_type="props">
                <q-td :props="props">
                   <q-chip 
                    dense square outline 
                    :color="props.value.includes('Saída') ? 'orange' : 'teal'" 
                    :icon="props.value.includes('Saída') ? 'arrow_upward' : 'arrow_downward'"
                   >
                     {{ props.value }}
                   </q-chip>
                </q-td>
              </template>
            </q-table>
          </div>
        </q-tab-panel>

        <q-tab-panel name="components">
          <div class="column q-gutter-y-md">
            <div class="row items-center justify-between wrap q-gutter-y-sm">
              <div class="text-h6 row items-center">
                 <q-icon name="extension" class="q-mr-sm" color="primary" />
                 Componentes Instalados
              </div>
              <div class="row items-center q-gutter-sm">
                <q-input dense outlined debounce="300" v-model="search.components" placeholder="Buscar componente..." style="width: 250px">
                  <template v-slot:prepend><q-icon name="search" /></template>
                </q-input>
                <q-btn @click="exportToCsv('components')" color="secondary" outline icon="file_download" label="CSV" />
                <q-btn @click="isInstallDialogOpen = true" color="primary" unelevated icon="add_circle" label="Instalar" />
              </div>
            </div>

            <q-table 
              :rows="filteredComponents" 
              :columns="componentColumns" 
              row-key="id" 
              :loading="componentStore.isLoading" 
              no-data-label="Nenhum componente instalado." 
              flat bordered
            >
              <template v-slot:body-cell-component_and_item="props">
                <q-td :props="props">
                  <div class="row items-center">
                    <q-avatar icon="settings" size="sm" color="grey-3" text-color="primary" class="q-mr-sm" />
                    <div>
                      <a href="#" @click.prevent="openPartHistoryDialog(props.row.part)" class="text-primary text-weight-bold link-hover">
                        {{ props.row.part?.name || 'Peça Desconhecida' }}
                      </a>
                      <div v-if="props.row.inventory_transaction?.item" class="text-caption text-grey">
                        Cód: <a href="#" @click.prevent="goToItemDetails(props.row.inventory_transaction.item.id)" class="text-secondary link-hover">{{ props.row.inventory_transaction.item.item_identifier }}</a>
                      </div>
                    </div>
                  </div>
                </q-td>
              </template>

              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn v-if="props.row.is_active" @click="confirmDiscard(props.row)" flat round dense color="negative" icon="delete_forever">
                    <q-tooltip>Descartar / Fim de Vida</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
            </q-table>
          </div>
        </q-tab-panel>

        <q-tab-panel name="costs">
          <div class="column q-gutter-y-md">
            <div class="row items-center justify-between wrap q-gutter-y-sm">
              <div class="text-h6 row items-center">
                <q-icon name="attach_money" class="q-mr-sm" color="primary" />
                Gestão de Despesas
              </div>
              <div class="row items-center q-gutter-sm">
                <q-input dense outlined v-model="dateRange.costs" mask="##/##/####" label="Início" style="width: 130px">
                   <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.costs" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Ok" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
                </q-input>
                <q-input dense outlined v-model="dateRange.costsTo" mask="##/##/####" label="Fim" style="width: 130px">
                   <template v-slot:append><q-icon name="event" class="cursor-pointer"><q-popup-proxy cover><q-date v-model="dateRange.costsTo" mask="DD/MM/YYYY"><div class="row items-center justify-end"><q-btn v-close-popup label="Ok" color="primary" flat /></div></q-date></q-popup-proxy></q-icon></template>
                </q-input>
                <q-input dense outlined debounce="300" v-model="search.costs" placeholder="Buscar custo..." style="width: 200px">
                   <template v-slot:prepend><q-icon name="search" /></template>
                </q-input>
                 <q-btn-dropdown color="primary" unelevated label="Ações" icon="bolt">
                    <q-list>
                      <q-item clickable v-close-popup @click="isAddCostDialogOpen = true">
                        <q-item-section avatar><q-icon name="add" /></q-item-section>
                        <q-item-section>Adicionar Custo</q-item-section>
                      </q-item>
                      <q-item clickable v-close-popup @click="exportToCsv('costs')">
                        <q-item-section avatar><q-icon name="file_download" /></q-item-section>
                        <q-item-section>Exportar CSV</q-item-section>
                      </q-item>
                    </q-list>
                 </q-btn-dropdown>
              </div>
            </div>

            <div class="row q-col-gutter-lg">
              <div class="col-12 col-md-8">
                <q-table 
                  :rows="filteredCosts" 
                  :columns="costColumns" 
                  row-key="id" 
                  :loading="costStore.isLoading" 
                  no-data-label="Nenhum custo registrado no período." 
                  flat bordered
                >
                  <template v-slot:bottom-row>
                    <q-tr class="text-weight-bold" :class="$q.dark.isActive ? '' : 'bg-grey-2'">
                      <q-td colspan="3" class="text-right text-uppercase">Total Filtrado:</q-td>
                      <q-td class="text-right text-primary text-h6">
                        {{ new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalCost) }}
                      </q-td>
                    </q-tr>
                  </template>
                </q-table>
              </div>
              <div class="col-12 col-md-4">
                <q-card flat bordered class="full-height">
                  <q-card-section>
                    <div class="text-subtitle1 text-weight-medium">Distribuição por Categoria</div>
                  </q-card-section>
                  <q-card-section class="flex flex-center">
                    <CostsPieChart v-if="filteredCosts.length > 0" :costs="filteredCosts" />
                    <div v-else class="text-center text-grey q-pa-xl column items-center">
                       <q-icon name="donut_small" size="40px" color="grey-4" />
                       <span class="q-mt-sm">Sem dados para o gráfico.</span>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </q-tab-panel>

        <q-tab-panel name="maintenance">
          <div class="column q-gutter-y-md">
            <div class="row items-center justify-between wrap q-gutter-y-sm">
              <div class="text-h6 row items-center">
                 <q-icon name="build" class="q-mr-sm" color="primary" />
                 Histórico de Manutenções
              </div>
              <div class="row items-center q-gutter-sm">
                <q-input dense outlined debounce="300" v-model="search.maintenances" placeholder="Buscar ordem de serviço..." style="width: 250px">
                  <template v-slot:prepend><q-icon name="search" /></template>
                </q-input>
                <q-btn @click="exportToCsv('maintenances')" color="secondary" outline icon="file_download" label="CSV" />
                <q-btn color="primary" unelevated icon="add" label="Nova OS" @click="isMaintenanceDialogOpen = true" />
              </div>
            </div>

            <q-table 
              :rows="filteredMaintenances" 
              :columns="maintenanceColumns" 
              row-key="id" 
              :loading="maintenanceStore.isLoading" 
              no-data-label="Nenhuma manutenção encontrada." 
              flat bordered
            >
              <template v-slot:body-cell-status="props">
                <q-td :props="props">
                  <q-chip 
                    :color="props.row.status === 'COMPLETED' ? 'positive' : (props.row.status === 'IN_PROGRESS' ? 'primary' : 'warning')" 
                    text-color="white" 
                    dense 
                    icon="info"
                  >
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn flat round dense color="primary" icon="visibility" @click="openMaintenanceDetails(props.row)">
                     <q-tooltip>Ver Detalhes da OS</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
            </q-table>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>

    <q-dialog v-model="isInstallTireDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallTire">
          <q-card-section class="bg-primary text-white row items-center">
            <div class="text-h6">Instalar Pneu</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup />
          </q-card-section>
          <q-card-section class="q-pt-md">
            <div class="text-subtitle2 q-mb-md text-grey-8">
              Posição Alvo: <strong>{{ targetPosition }}</strong>
            </div>
            <div class="q-gutter-y-md">
              <q-select outlined v-model="installTireForm.part_id" :options="tireOptions" label="Selecione o Pneu do Estoque *" emit-value map-options use-input @filter="filterTires" :rules="[val => !!val || 'Selecione um pneu']">
                 <template v-slot:option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                      </q-item-section>
                    </q-item>
                 </template>
              </q-select>
              <q-input v-if="!isAgro" outlined v-model.number="installTireForm.install_km" type="number" label="KM atual do Veículo *" :rules="[val => val !== null && val >= 0 || 'KM inválido']" />
              <q-input v-else outlined v-model.number="installTireForm.install_engine_hours" type="number" label="Horas do Motor atuais *" :rules="[val => val !== null && val >= 0 || 'Horas inválidas']" />
            </div>
          </q-card-section>
          <q-separator />
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup color="grey" />
            <q-btn type="submit" unelevated color="primary" label="Confirmar Instalação" :loading="tireStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isAxleConfigDialogOpen">
      <q-card style="width: 450px; max-width: 90vw;">
        <q-form @submit.prevent="handleUpdateAxleConfig">
          <q-card-section class="bg-secondary text-white">
            <div class="text-h6">Configuração de Eixos</div>
          </q-card-section>
          <q-card-section class="q-pt-lg">
            <q-select outlined v-model="selectedAxleConfig" :options="axleConfigOptions" label="Layout de Rodagem" hint="Selecione a disposição dos pneus" emit-value map-options :rules="[val => !!val || 'Selecione uma configuração']" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup color="grey" />
            <q-btn type="submit" unelevated color="secondary" label="Salvar Configuração" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isInstallDialogOpen">
      <q-card style="width: 500px; max-width: 90vw;">
        <q-form @submit.prevent="handleInstallComponent">
          <q-card-section class="bg-primary text-white"><div class="text-h6">Instalar Componente</div></q-card-section>
          <q-card-section class="q-gutter-y-md q-pt-md">
            <q-select outlined v-model="installFormComponent.part_id" :options="partOptions" label="Peça/Item do Estoque *" emit-value map-options use-input @filter="filterParts" :rules="[val => !!val || 'Selecione um item']">
              <template v-slot:no-option><q-item><q-item-section class="text-grey">Nenhum item encontrado</q-item-section></q-item></template>
            </q-select>
            <q-input outlined v-model.number="installFormComponent.quantity" type="number" label="Quantidade *" :rules="[val => val > 0 || 'Deve ser maior que zero']" />
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancelar" v-close-popup color="grey" />
            <q-btn type="submit" unelevated color="primary" label="Instalar" :loading="componentStore.isLoading" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <q-dialog v-model="isAddCostDialogOpen">
      <AddCostDialog :vehicle-id="vehicleId" @close="isAddCostDialogOpen = false" />
    </q-dialog>

    <PartHistoryDialog v-model="isPartHistoryDialogOpen" :part="selectedPart" />
    <MaintenanceDetailsDialog v-model="isMaintenanceDetailsOpen" :request="selectedMaintenance" />
    <CreateRequestDialog v-model="isMaintenanceDialogOpen" :preselected-vehicle-id="vehicleId" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar, type QTableColumn, exportFile } from 'quasar';
import { api } from 'boot/axios';
import { format, differenceInDays, parse } from 'date-fns';
import { storeToRefs } from 'pinia';

// Stores
import { useAuthStore } from 'stores/auth-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useVehicleCostStore } from 'stores/vehicle-cost-store';
import { useVehicleComponentStore } from 'stores/vehicle-component-store';
import { usePartStore } from 'stores/part-store';
import { useMaintenanceStore } from 'stores/maintenance-store';
import { useTireStore } from 'stores/tire-store';

// Models
import { InventoryItemStatus } from 'src/models/inventory-item-models';
import type { VehicleComponent } from 'src/models/vehicle-component-models';
import type { InventoryTransaction } from 'src/models/inventory-transaction-models';
import type { Part } from 'src/models/part-models';
import type { MaintenanceRequest } from 'src/models/maintenance-models';
import type { VehicleTire, TireWithStatus, VehicleTireHistory, TireInstallPayload } from 'src/models/tire-models';
import type { VehicleCost } from 'src/models/vehicle-cost-models';

// Components
import PartHistoryDialog from 'components/PartHistoryDialog.vue';
import CostsPieChart from 'components/CostsPieChart.vue';
import MaintenanceDetailsDialog from 'components/maintenance/MaintenanceDetailsDialog.vue';
import CreateRequestDialog from 'components/maintenance/CreateRequestDialog.vue';
import InteractiveTireLayout from 'components/InteractiveTireLayout.vue';
import TireCostChart from 'components/TireCostChart.vue';
import { axleLayouts } from 'src/config/tire-layouts';
import AddCostDialog from 'components/AddCostDialog.vue';

// --- INICIALIZAÇÃO ---
const route = useRoute();
const router = useRouter(); 
const $q = useQuasar();
const authStore = useAuthStore();
const vehicleStore = useVehicleStore();
const costStore = useVehicleCostStore();
const componentStore = useVehicleComponentStore();
const partStore = usePartStore();
const maintenanceStore = useMaintenanceStore();
const tireStore = useTireStore();

const { removedTiresHistory } = storeToRefs(tireStore);

const vehicleId = Number(route.params.id);
const tab = ref((route.query.tab as string) || 'tires');
const isAgro = computed(() => authStore.userSector === 'agronegocio');
const isHistoryLoading = ref(false);
const inventoryHistory = ref<InventoryTransaction[]>([]);

// VARIÁVEIS DE CONTROLE UI
const isAddCostDialogOpen = ref(false);
const isInstallDialogOpen = ref(false);
const isPartHistoryDialogOpen = ref(false);
const isMaintenanceDialogOpen = ref(false);
const isMaintenanceDetailsOpen = ref(false);
const selectedPart = ref<Part | null>(null);
const selectedMaintenance = ref<MaintenanceRequest | null>(null);
const installFormComponent = ref({ part_id: null, quantity: 1 });
const partOptions = ref<{label: string, value: number}[]>([]);
const isInstallTireDialogOpen = ref(false);
const targetPosition = ref('');
const tireOptions = ref<{label: string, value: number}[]>([]);
const installTireForm = ref<{
  part_id: number | null,
  install_km: number | null,
  install_engine_hours?: number | null
}>({ part_id: null, install_km: 0, install_engine_hours: 0 });
const isAxleConfigDialogOpen = ref(false);
const selectedAxleConfig = ref<string | null>(null);
const axleConfigOptions = Object.keys(axleLayouts).map(key => ({
  label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
  value: key
}));

async function refreshAllVehicleData() {
  isHistoryLoading.value = true;
  await partStore.fetchParts();
  await Promise.all([
    fetchHistory(),
    vehicleStore.fetchVehicleById(vehicleId),
    costStore.fetchCosts(vehicleId),
    componentStore.fetchComponents(vehicleId),
    maintenanceStore.fetchMaintenanceRequests({ vehicleId: vehicleId, limit: 100 }),
    tireStore.fetchTireLayout(vehicleId),
    tireStore.fetchRemovedTiresHistory(vehicleId),
  ]);
  isHistoryLoading.value = false;
}

// LÓGICA DE PNEUS E KPIS
const tiresWithStatus = computed((): TireWithStatus[] => {
  if (!tireStore.tireLayout?.tires || !vehicleStore.selectedVehicle) return [];
  const currentKm = vehicleStore.selectedVehicle.current_km || 0;
  const currentEngineHours = vehicleStore.selectedVehicle.current_engine_hours || 0;
  return tireStore.tireLayout.tires.map(tire => {
    const lifespan_unit = tire.part.lifespan_km || 0;
    if (lifespan_unit <= 0) return { ...tire, status: 'ok', wearPercentage: 0, km_rodados: 0, horas_de_uso: 0, lifespan_km: 0 };
    let units_used = 0;
    if (isAgro.value) {
      units_used = currentEngineHours - (tire.install_engine_hours || 0);
    } else {
      units_used = currentKm - tire.install_km;
    }
    units_used = Math.max(0, units_used);
    const wearPercentage = (units_used / lifespan_unit) * 100;
    let status: 'ok' | 'warning' | 'critical' = 'ok';
    if (wearPercentage >= 100) status = 'critical';
    else if (wearPercentage >= 80) status = 'warning';
    return { ...tire, status, wearPercentage, km_rodados: isAgro.value ? 0 : units_used, horas_de_uso: isAgro.value ? units_used : 0, lifespan_km: lifespan_unit };
  });
});

const kpiTireCostPerKm = computed(() => {
  const totalKm = removedTiresHistory.value.reduce((sum, tire) => sum + tire.km_run, 0);
  const totalCost = removedTiresHistory.value.reduce((sum, tire) => sum + (tire.part.value || 0), 0);
  if (totalKm <= 0 || totalCost <= 0) return 'N/A';
  return (totalCost / totalKm).toFixed(2);
});
const kpiTiresInAlert = computed(() => {
  return tiresWithStatus.value.filter(t => t.status === 'warning' || t.status === 'critical').length;
});
const kpiTotalTireCost = computed(() => {
  const removedCost = removedTiresHistory.value.reduce((sum, tire) => sum + (tire.part.value || 0), 0);
  const installedCost = tiresWithStatus.value.reduce((sum, tire) => sum + (tire.part.value || 0), 0);
  const total = removedCost + installedCost;
  return total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
});
const kpiAvgTireLifespan = computed(() => {
    if (removedTiresHistory.value.length === 0) return 'N/A';
    const validEntries = removedTiresHistory.value.filter(item => item.km_run > 0);
    if (validEntries.length === 0) return 'N/A';
    const totalKm = validEntries.reduce((sum, item) => sum + item.km_run, 0);
    return Math.round(totalKm / validEntries.length).toLocaleString('pt-BR');
});
const tireCostsByMonth = computed(() => {
  return inventoryHistory.value
    .filter(t => t.part?.category === 'Pneu' && t.transaction_type === 'Saída para Uso' && t.part?.value)
    .map(t => ({
      date: new Date(t.timestamp),
      amount: t.part!.value!,
    }));
});

// FILTROS E COMPUTED PROPERTIES
const search = ref({ history: '', components: '', costs: '', maintenances: '' });
const dateRange = ref({ history: '', historyTo: '', costs: '', costsTo: '' });

const filteredHistory = computed(() => {
  return inventoryHistory.value.filter(row => {
    const needle = search.value.history.toLowerCase();
    const startDate = dateRange.value.history ? parse(dateRange.value.history, 'dd/MM/yyyy', new Date()) : null;
    const endDate = dateRange.value.historyTo ? parse(dateRange.value.historyTo, 'dd/MM/yyyy', new Date()) : null;
    if(endDate) endDate.setHours(23, 59, 59, 999);
    const rowDate = new Date(row.timestamp);
    const dateMatch = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);
    const itemIdentifier = row.item?.item_identifier || '';
    const partName = row.part?.name || row.item?.part?.name || '';
    const textMatch = !needle || 
                      JSON.stringify(row).toLowerCase().includes(needle) ||
                      String(itemIdentifier).includes(needle) ||
                      partName.toLowerCase().includes(needle);
    return dateMatch && textMatch;
  });
});

const filteredComponents = computed(() => {
  const needle = search.value.components.toLowerCase();
  if (!needle) return componentStore.components;
  return componentStore.components.filter(row => {
    const itemIdentifier = row.inventory_transaction?.item?.item_identifier || '';
    return JSON.stringify(row).toLowerCase().includes(needle) || String(itemIdentifier).includes(needle);
  });
});

const filteredCosts = computed(() => {
  return costStore.costs.filter(row => {
    const needle = search.value.costs.toLowerCase();
    const startDate = dateRange.value.costs ? parse(dateRange.value.costs, 'dd/MM/yyyy', new Date()) : null;
    const endDate = dateRange.value.costsTo ? parse(dateRange.value.costsTo, 'dd/MM/yyyy', new Date()) : null;
    if(endDate) endDate.setHours(23, 59, 59, 999);
    const rowDate = new Date(row.date);
    const dateMatch = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);
    const textMatch = !needle || JSON.stringify(row).toLowerCase().includes(needle);
    return dateMatch && textMatch;
  });
});
const totalCost = computed(() => filteredCosts.value.reduce((sum, cost) => sum + cost.amount, 0));

const filteredMaintenances = computed(() => {
  const needle = search.value.maintenances.toLowerCase();
  if (!needle) return maintenanceStore.maintenances;
  return maintenanceStore.maintenances.filter(row => JSON.stringify(row).toLowerCase().includes(needle));
});

// DEFINIÇÃO DE COLUNAS
const historyTireColumns: QTableColumn<VehicleTireHistory>[] = [
  { name: 'part', label: 'Pneu (Série)', field: row => row.part.serial_number || 'N/A', align: 'left', sortable: true },
  { name: 'position', label: 'Posição', field: (row) => row.position_code || 'N/A', align: 'center' },
  { name: 'dates', label: 'Inst./Remoção', field: row => `${row.installation_date ? format(new Date(row.installation_date), 'dd/MM/yy') : 'N/A'} - ${row.removal_date ? format(new Date(row.removal_date), 'dd/MM/yy') : 'Em uso'}`, align: 'left' },
  { name: 'km_run', label: 'KM Rodados', field: 'km_run', align: 'right', sortable: true, format: (val: number) => val > 0 ? val.toLocaleString('pt-BR') : 'N/A' },
  { name: 'cost_per_km', label: 'Custo/KM', field: row => (row.km_run > 0 && row.part.value) ? `R$ ${(row.part.value / row.km_run).toFixed(2)}` : 'N/A', align: 'right', sortable: true },
];

const historyColumns: QTableColumn<InventoryTransaction>[] = [
    { name: 'timestamp', label: 'Data/Hora', field: 'timestamp', format: (val) => format(new Date(val), 'dd/MM/yyyy HH:mm'), align: 'left', sortable: true },
    { name: 'part_and_item', label: 'Item Movimentado', field: (row) => row.id, align: 'left', sortable: true },
    { name: 'transaction_type', label: 'Tipo', field: 'transaction_type', align: 'center', sortable: true },
    { name: 'user', label: 'Responsável', field: row => row.user?.full_name || 'Sistema', align: 'left' },
    { name: 'notes', label: 'Observações', field: 'notes', align: 'left', style: 'max-width: 250px; white-space: normal;' },
];

const componentColumns: QTableColumn<VehicleComponent>[] = [
    { name: 'component_and_item', label: 'Componente', field: (row) => row.id, align: 'left', sortable: true },
    { name: 'installation_date', label: 'Instalação', field: 'installation_date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), align: 'left', sortable: true },
    { name: 'age', label: 'Tempo de Uso (dias)', field: 'installation_date', format: (val) => `${differenceInDays(new Date(), new Date(val))}`, align: 'center', sortable: true },
    { name: 'installer', label: 'Instalador', field: row => row.inventory_transaction?.user?.full_name || 'N/A', align: 'left', sortable: true },
    { name: 'actions', label: '', field: () => '', align: 'right' },
];

const costColumns: QTableColumn[] = [
  { name: 'date', label: 'Data', field: 'date', format: (val) => format(new Date(val), 'dd/MM/yyyy'), sortable: true, align: 'left' },
  { name: 'cost_type', label: 'Categoria', field: 'cost_type', sortable: true, align: 'left' },
  { name: 'description', label: 'Descrição', field: 'description', sortable: false, align: 'left', style: 'max-width: 300px; white-space: pre-wrap;' },
  { name: 'amount', label: 'Valor (R$)', field: 'amount', format: (val) => val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), sortable: true, align: 'right' },
];

const maintenanceColumns: QTableColumn<MaintenanceRequest>[] = [
  { name: 'created_at', label: 'Data Solicitação', field: 'created_at', format: (val) => val ? format(new Date(val), 'dd/MM/yyyy') : 'A definir', sortable: true, align: 'left' },
  { name: 'category', label: 'Categoria', field: 'category', sortable: true, align: 'left' },
  { name: 'problem_description', label: 'Problema Reportado', field: 'problem_description', align: 'left', style: 'max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' },
  { name: 'status', label: 'Status', field: 'status', align: 'center', sortable: true },
  { name: 'actions', label: '', field: () => '', align: 'right' },
];

// MÉTODOS E AÇÕES
async function fetchHistory() {
  isHistoryLoading.value = true;
  try {
    const { data } = await api.get<InventoryTransaction[]>(`/vehicles/${vehicleId}/inventory-history`);
    inventoryHistory.value = data;
  } catch (error) {
    console.error("Falha ao carregar histórico:", error);
    $q.notify({ type: 'negative', message: 'Falha ao carregar o histórico do veículo.' });
  } finally {
    isHistoryLoading.value = false;
  }
}

function getPartName(partId: number | undefined | null): string {
  if (!partId) return 'Peça N/A';
  const part = partStore.parts.find(p => p.id === partId);
  return part?.name || 'Peça N/A';
}

function openInstallDialog(positionCode: string) {
  targetPosition.value = positionCode;
  installTireForm.value = {
    part_id: null,
    install_km: vehicleStore.selectedVehicle?.current_km || 0,
    install_engine_hours: vehicleStore.selectedVehicle?.current_engine_hours || 0
  };
  isInstallTireDialogOpen.value = true;
}

async function handleInstallTire() {
  if (!installTireForm.value.part_id) {
    $q.notify({ type: 'negative', message: 'Por favor, selecione um pneu.' });
    return;
  }
  const payload: TireInstallPayload = {
    position_code: targetPosition.value,
    part_id: installTireForm.value.part_id,
    install_km: installTireForm.value.install_km ?? 0
  };
  if (isAgro.value && typeof installTireForm.value.install_engine_hours === 'number') {
    payload.install_engine_hours = installTireForm.value.install_engine_hours;
  }
  const success = await tireStore.installTire(vehicleId, payload);
  if (success) {
    isInstallTireDialogOpen.value = false;
    await refreshAllVehicleData();
  }
}

function openRemoveDialog(tire: VehicleTire) {
  const message = isAgro.value
    ? `Digite as Horas do Motor atuais para remover o pneu (Série: ${tire.part.serial_number}) da posição ${tire.position_code}.`
    : `Digite o KM atual do veículo para remover o pneu (Série: ${tire.part.serial_number}) da posição ${tire.position_code}.`;
  const model = isAgro.value
    ? String(vehicleStore.selectedVehicle?.current_engine_hours || tire.install_engine_hours || 0)
    : String(vehicleStore.selectedVehicle?.current_km || tire.install_km);

  $q.dialog({
    title: 'Remover Pneu',
    message,
    prompt: { model, type: 'number' },
    cancel: true,
    persistent: false,
  }).onOk((valueStr: string) => {
    void (async () => {
      const value = Number(valueStr);
      const removal_km = isAgro.value ? (vehicleStore.selectedVehicle?.current_km || tire.install_km) : value;
      const removal_engine_hours = isAgro.value ? value : undefined;

      let validationOk = false;
      if (isAgro.value) {
        if (removal_engine_hours !== undefined && !isNaN(removal_engine_hours) && removal_engine_hours >= (tire.install_engine_hours || 0)) validationOk = true;
      } else {
        if (!isNaN(removal_km) && removal_km >= tire.install_km) validationOk = true;
      }

      if (!validationOk) {
        $q.notify({ type: 'negative', message: `O valor de remoção deve ser maior ou igual ao de instalação.` });
        return;
      }

      const success = await tireStore.removeTire(tire.id, removal_km, removal_engine_hours);
      if (success) {
        await refreshAllVehicleData();
      }
    })();
  });
}

async function handleUpdateAxleConfig() {
  if (!selectedAxleConfig.value) return;
  const success = await vehicleStore.updateAxleConfiguration(vehicleId, selectedAxleConfig.value);
  if (success) {
    isAxleConfigDialogOpen.value = false;
    await tireStore.fetchTireLayout(vehicleId);
  }
}

function filterTires(val: string, update: (cb: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    tireOptions.value = partStore.parts
      .filter(p => p.category === 'Pneu' && p.stock > 0 && (p.serial_number?.toLowerCase().includes(needle) || p.name.toLowerCase().includes(needle)))
      .map(p => ({ label: `${p.brand || ''} ${p.name} (Série: ${p.serial_number || 'N/A'})`, value: p.id }));
  });
}

function filterParts(val: string, update: (cb: () => void) => void) {
  update(() => {
    const needle = val.toLowerCase();
    partOptions.value = partStore.parts
      .filter(p => p.name.toLowerCase().includes(needle) && p.stock > 0 && p.category !== 'Pneu')
      .map(p => ({ label: `${p.name} (Estoque: ${p.stock})`, value: p.id }));
  });
}

async function handleInstallComponent() {
  if (!installFormComponent.value.part_id) return;
  $q.notify({ type: 'info', message: 'Função de Instalação Manual (sem Cód. Item) ainda não implementada.' });
  // Código comentado original mantido para referência futura
  // const success = await componentStore.installComponent(vehicleId, {
  //   part_id: installFormComponent.value.part_id,
  //   quantity: installFormComponent.value.quantity,
  // });
  // if (success) {
  //   isInstallDialogOpen.value = false;
  //   installFormComponent.value = { part_id: null, quantity: 1 };
     await refreshAllVehicleData();
  // }
}

function confirmDiscard(component: VehicleComponent) {
    const partName = component.part?.name || 'este item';
    $q.dialog({
        title: 'Confirmar Descarte',
        message: `Você tem certeza que deseja marcar o componente "${partName}" como "Fim de Vida"?`,
        cancel: true, persistent: false,
        ok: { label: 'Confirmar', color: 'negative', unelevated: true }
    }).onOk(() => {
      void (async () => {
        if (component.part) {
            const item_id = component.inventory_transaction?.item?.id;
            if (item_id) {
               const success = await partStore.setItemStatus(component.part.id, item_id, InventoryItemStatus.FIM_DE_VIDA, undefined, "Descartado pelo gerenciador de componentes.");
               if (success) await refreshAllVehicleData();
            } else {
              $q.notify({ type: 'negative', message: 'Erro: Não foi possível encontrar o ID do item de inventário associado.' });
            }
        }
      })();
    });
}

function openPartHistoryDialog(part: Part | null) {
  if (!part) return;
  selectedPart.value = part;
  void partStore.fetchHistory(part.id);
  isPartHistoryDialogOpen.value = true;
}

function openMaintenanceDetails(maintenance: MaintenanceRequest) {
  selectedMaintenance.value = maintenance;
  isMaintenanceDetailsOpen.value = true;
}

function goToItemDetails(itemId: number) {
  void router.push({ name: 'item-details', params: { id: itemId } });
}

function exportToCsv(tabName: 'history' | 'components' | 'costs' | 'maintenances') {
    let data: (InventoryTransaction | VehicleComponent | MaintenanceRequest | VehicleCost | VehicleTireHistory)[], columns: QTableColumn[], fileName: string;
    switch(tabName) {
        case 'history': data = filteredHistory.value; columns = historyColumns; fileName = 'historico'; break;
        case 'components': data = filteredComponents.value; columns = componentColumns; fileName = 'componentes'; break;
        case 'costs': data = filteredCosts.value; columns = costColumns; fileName = 'custos'; break;
        case 'maintenances': data = filteredMaintenances.value; columns = maintenanceColumns; fileName = 'manutencoes'; break;
    }
    if (!data || !columns || !fileName) return;

    const columnsToExp = columns.filter(c => c.name !== 'actions' && c.label);
    const content = [
        columnsToExp.map(col => col.label).join(';'),
        ...data.map(row => columnsToExp.map(col => {
          let val;
          if (typeof col.field === 'function') val = col.field(row as never);
          else val = row[col.field as keyof typeof row];
          if (col.format && val) val = col.format(val, row as never);
          const cleanVal = `"${String(val ?? '').replace(/"/g, '""')}"`;
          return cleanVal;
        }).join(';'))
    ].join('\r\n');

    const status = exportFile(
      `${fileName}_veiculo_${vehicleId}.csv`,
      '\ufeff' + content, 'text/csv'
    );
    if (status !== true) $q.notify({ message: 'O browser bloqueou o download...', color: 'negative' });
}

onMounted(async () => {
  await refreshAllVehicleData();
  selectedAxleConfig.value = vehicleStore.selectedVehicle?.axle_configuration || null;
});
</script>

<style lang="scss" scoped>
.link-hover {
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
}
.opacity-50 {
  opacity: 0.5;
}
.opacity-80 {
  opacity: 0.8;
}
.opacity-90 {
  opacity: 0.9;
}
.full-height {
  height: 100%;
}
</style>