<template>
  <q-page padding>
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h5 text-weight-bold q-my-none">Placar de Líderes de Performance</h1>
      <q-btn @click="performanceStore.fetchLeaderboard()" flat round dense icon="refresh" :loading="performanceStore.isLoading" />
    </div>

    <div v-if="performanceStore.isLoading" class="text-center q-pa-xl">
      <q-spinner-dots color="primary" size="40px" />
    </div>

    <div v-else-if="performanceStore.leaderboard.length === 0" class="text-center q-pa-xl text-grey-7">
      <q-icon name="leaderboard" size="4em" />
      <p class="q-mt-md">Ainda não há dados suficientes para gerar o ranking.</p>
    </div>

    <div v-else class="q-gutter-y-lg">
      <div v-if="topThree[0]" class="row items-end q-col-gutter-md">
        <div v-if="topThree[1]" class="col text-center">
          <PodiumCard :driver="topThree[1]" rank="2" />
        </div>
        <div class="col text-center">
          <PodiumCard :driver="topThree[0]" rank="1" />
        </div>
        <div v-if="topThree[2]" class="col text-center">
          <PodiumCard :driver="topThree[2]" rank="3" />
        </div>
      </div>

      <div class="q-gutter-y-md">
        <q-card
          v-for="(driver, index) in remainingDrivers"
          :key="driver.user_id"
          flat bordered
          class="floating-card"
        >
          <q-card-section horizontal class="items-center">
            <q-item-section class="col-auto text-center text-h6 text-weight-bold text-grey-6 q-pa-md">
              {{ performanceStore.leaderboard.length < 3 ? index + 1 : index + 4 }}
            </q-item-section>
            <q-separator vertical inset />
            <q-item-section avatar class="q-pl-md">
               <q-avatar size="56px">
                <img v-if="driver.avatar_url" :src="driver.avatar_url">
                <q-icon v-else name="account_circle" color="grey-5" size="56px" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <div class="text-body1 text-weight-medium">{{ driver.full_name }}</div>
            </q-item-section>
            <q-item-section side class="q-pa-md">
              <div class="text-h6 text-weight-bold">{{ driver.performance_score.toFixed(0) }}</div>
              <div class="text-caption">Score</div>
            </q-item-section>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { usePerformanceStore } from 'stores/performance-store';
import PodiumCard from 'src/components/performance/PodiumCard.vue';

const performanceStore = usePerformanceStore();

const topThree = computed(() => performanceStore.leaderboard.slice(0, 3));
const remainingDrivers = computed(() => {
  return performanceStore.leaderboard.length < 3
    ? performanceStore.leaderboard
    : performanceStore.leaderboard.slice(3);
});

onMounted(() => {
  void performanceStore.fetchLeaderboard();
});
</script>