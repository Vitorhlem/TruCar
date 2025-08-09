<template>
  <q-page padding class="q-gutter-y-lg">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="flex items-center no-wrap">
            <q-icon name="local_shipping" color="primary" size="44px" class="q-mr-md" />
            <div>
              <div class="text-grey-8">Total de Veículos</div>
              <div class="text-h4 text-weight-bolder">{{ vehicleStore.totalCount }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
       <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="flex items-center no-wrap">
            <q-icon name="event_available" color="positive" size="44px" class="q-mr-md" />
            <div>
              <div class="text-grey-8">Disponíveis</div>
              <div class="text-h4 text-weight-bolder">{{ vehicleStore.availableCount }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
       <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="flex items-center no-wrap">
            <q-icon name="map" color="orange-8" size="44px" class="q-mr-md" />
            <div>
              <div class="text-grey-8">Em Viagem</div>
              <div class="text-h4 text-weight-bolder">{{ vehicleStore.inUseCount }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
       <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="flex items-center no-wrap">
            <q-icon name="build" color="negative" size="44px" class="q-mr-md" />
            <div>
              <div class="text-grey-8">Em Manutenção</div>
              <div class="text-h4 text-weight-bolder">{{ vehicleStore.maintenanceCount }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div>
      <q-table
        flat
        bordered
        title="Viagens em Andamento"
        :rows="journeyStore.activeJourneys"
        :columns="columns"
        row-key="id"
        :loading="journeyStore.isLoading || vehicleStore.isLoading"
        :rows-per-page-options="[5, 10, 0]"
          no-data-label="Nenhuma viagem em andamento"
      >
        <template v-slot:body-cell-vehicle="props">
          <q-td :props="props">
            <div class="text-weight-bold">{{ props.row.vehicle.model }}</div>
            <div class="text-grey-8">{{ props.row.vehicle.license_plate }}</div>
          </q-td>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import type { QTableColumn } from 'quasar';
import { useVehicleStore } from 'stores/vehicle-store';
import { useJourneyStore } from 'stores/journey-store';
import type { Journey } from 'src/models/journey-models';

const vehicleStore = useVehicleStore();
const journeyStore = useJourneyStore();

const columns: QTableColumn[] = [
  { name: 'vehicle', label: 'Veículo', field: (row: Journey) => row.vehicle, align: 'left', sortable: true },
  { name: 'driver', label: 'Motorista', field: (row: Journey) => row.driver.full_name, align: 'left', sortable: true },
  { name: 'destination', label: 'Destino', field: (row: Journey) => row.destination_address || row.trip_description, align: 'left' },
  { name: 'startTime', label: 'Início', field: 'start_time', align: 'center', sortable: true, format: (val: string) => new Date(val).toLocaleTimeString('pt-br', { hour: '2-digit', minute: '2-digit' }) },
];

onMounted(async () => {
  await vehicleStore.fetchAllVehicles();
  // CORREÇÃO FINAL: Chamando a função que agora existe na store
  await journeyStore.fetchAllJourneys(); 
});
</script>