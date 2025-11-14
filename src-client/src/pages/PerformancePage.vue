<template>
  <q-page padding>
    <!-- CABEÇALHO -->
    <div class="flex items-center justify-between q-mb-md">
      <h1 class="text-h4 text-weight-bold q-my-none">Placar de Líderes</h1>
      <q-btn flat round dense icon="refresh" @click="leaderboardStore.fetchLeaderboard" :loading="leaderboardStore.isLoading" />
    </div>

    <!-- ESTADO DE CARREGAMENTO -->
    <div v-if="leaderboardStore.isLoading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="3em" />
    </div>

    <!-- PÓDIO TOP 3 -->
    <div v-else-if="leaderboard.length > 0" class="row q-col-gutter-md justify-center items-end q-mb-lg">
      <!-- 2º LUGAR -->
      <div v-if="leaderboard[1]" class="col-4 text-center podium-card silver">
        <q-avatar size="80px"><img :src="leaderboard[1].avatar_url || defaultAvatar" /></q-avatar>
        <div class="text-weight-bold text-black q-mt-sm ellipsis">{{ leaderboard[1].full_name }}</div>
        <div class="text-h5 text-black text-weight-bolder">{{ leaderboard[1].primary_metric_value.toFixed(1) }}</div>
        <div class="text-caption text-black">{{ unit }}</div>
      </div>
      <!-- 1º LUGAR -->
      <div v-if="leaderboard[0]" class="col-4 text-center podium-card gold">
        <q-avatar size="100px"><img :src="leaderboard[0].avatar_url || defaultAvatar" /></q-avatar>
        <div class="text-weight-bold text-black q-mt-sm ellipsis">{{ leaderboard[0].full_name }}</div>
        <div class="text-h4 text-black text-weight-bolder">{{ leaderboard[0].primary_metric_value.toFixed(1) }}</div>
        <div class="text-caption text-black">{{ unit }}</div>
      </div>
      <!-- 3º LUGAR -->
      <div v-if="leaderboard[2]" class="col-4 text-center podium-card bronze">
        <q-avatar size="70px"><img :src="leaderboard[2].avatar_url || defaultAvatar" /></q-avatar>
        <div class="text-weight-bold text-black q-mt-sm ellipsis">{{ leaderboard[2].full_name }}</div>
        <div class="text-h6 text-black text-weight-bolder">{{ leaderboard[2].primary_metric_value.toFixed(1) }}</div>
        <div class="text-caption text-black">{{ unit }}</div>
      </div>
    </div>

    <!-- LISTA DO RESTANTE DOS LÍDERES -->
    <q-card v-if="leaderboard.length > 0" flat bordered>
      <q-list separator>
        <q-item v-for="(user, index) in leaderboard" :key="user.id" clickable v-ripple>
          <q-item-section side class="text-h6 text-weight-medium text-grey-7" style="width: 50px;">
            {{ index + 1 }}
          </q-item-section>

          <q-item-section avatar>
            <q-avatar>
              <img :src="user.avatar_url || defaultAvatar" />
            </q-avatar>
          </q-item-section>

          <q-item-section>
            <q-item-label class="text-weight-medium">{{ user.full_name }}</q-item-label>
            <q-item-label caption>{{ user.total_journeys }} viagens</q-item-label>
          </q-item-section>

          <q-item-section side class="text-right">
            <q-item-label class="text-h6 text-weight-bold text-primary">
              {{ user.primary_metric_value.toFixed(1) }}
            </q-item-label>
            <q-item-label caption>{{ unit }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>

    <!-- ESTADO VAZIO -->
    <div v-else class="text-center q-pa-xl text-grey-7">
      <q-icon name="leaderboard" size="4em" />
      <p class="q-mt-md">Ainda não há dados suficientes para gerar o placar de líderes.</p>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useLeaderboardStore } from 'stores/leaderboard-store';
import defaultAvatar from '../assets/default-avatar.png';

const leaderboardStore = useLeaderboardStore();

const leaderboard = computed(() => leaderboardStore.leaderboard);
const unit = computed(() => leaderboardStore.unit);

onMounted(() => {
  void leaderboardStore.fetchLeaderboard();
});
</script>

<style scoped lang="scss">
.podium-card {
  padding: 16px 8px;
  border-radius: 8px;
  border-bottom: 4px solid;
  transition: transform 0.2s ease-in-out;

  &:hover {
    transform: translateY(-5px);
  }
}

.gold {
  border-color: #ffd700;
  background: linear-gradient(145deg, #fef5d6, #fff);
  order: 2; /* 1º lugar fica no meio */
  transform: scale(1.1);
}

.silver {
  border-color: #c0c0c0;
  background: linear-gradient(145deg, #f0f0f0, #fff);
  order: 1; /* 2º lugar fica na esquerda */
}

.bronze {
  border-color: #cd7f32;
  background: linear-gradient(145deg, #fce9d8, #fff);
  order: 3; /* 3º lugar fica na direita */
}
</style>

