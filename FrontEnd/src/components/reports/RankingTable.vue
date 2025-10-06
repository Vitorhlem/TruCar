<template>
  <q-markup-table flat dense separator="horizontal">
    <thead>
      <tr>
        <th class="text-left">Veículo</th>
        <th class="text-right">Valor</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in data" :key="item.vehicle_id">
        <td class="text-left">{{ item.vehicle_identifier }}</td>
        <td class="text-right">{{ item.value.toFixed(2) }} {{ item.unit }}</td>
      </tr>
      <tr v-if="data.length === 0">
        <td colspan="2" class="text-center text-grey">Sem dados para este ranking.</td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<script setup lang="ts">
import { type PropType } from 'vue';
import type { VehicleRankingEntry } from 'src/models/report-models';

defineProps({
  data: {
    type: Array as PropType<VehicleRankingEntry[]>,
    required: true,
  },
});
</script>