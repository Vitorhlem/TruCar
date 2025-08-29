<!-- ARQUIVO: src/components/KpiCard.vue -->
<template>
  <q-card flat bordered class="full-height floating-card">
    <q-card-section>
      <div class="row items-start no-wrap">
        <div class="col">
          <div class="text-overline text-grey-8">{{ label }}</div>
          <div class="text-h4 text-weight-bold">
            <span v-if="prefix" class="text-h5">{{ prefix }} </span>{{ value }}
            <span v-if="unit" class="text-body1 text-weight-regular q-ml-xs">{{ unit }}</span>
          </div>
        </div>
        <div class="col-auto">
          <q-icon :name="icon" color="primary" size="28px" class="q-mt-xs" />
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  prefix: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: 'bar_chart'
  }
});
</script>