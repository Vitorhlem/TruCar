<template>
  <q-page padding class="q-gutter-y-md bg">
    
    <div class="row items-center justify-between q-mb-sm">
      <div>
        <div class="row items-center text-primary q-mb-xs">
          <q-icon name="emoji_events" size="24px" class="q-mr-sm" />
          <div class="text-overline text-weight-bold">PERFORMANCE & RANKING</div>
        </div>
        <h1 class="text-h5 text-weight-bold q-my-none text-grey-9">Placar de Líderes</h1>
      </div>

      <div class="row q-gutter-sm">
        <q-btn-toggle
          v-model="period"
          toggle-color="primary"
          color=""
          text-color="grey-7"
          unelevated
          dense
          class="border-gray rounded-borders"
          :options="[
            {label: 'Semana', value: 'week'},
            {label: 'Mês', value: 'month'},
            {label: 'Geral', value: 'all'}
          ]"
        />
        <q-btn flat round dense icon="refresh" color="grey-7" @click="refreshData" :loading="leaderboardStore.isLoading" />
      </div>
    </div>

    <div v-if="leaderboardStore.isLoading" class="row justify-center q-pa-xl">
      <q-spinner-dots color="primary" size="3em" />
    </div>

    <div v-else-if="leaderboard.length > 0">
      
      <div class="row justify-center items-end q-mb-xl q-px-md relative-position">
        
        <div v-if="leaderboard[1]" class="col-4 col-sm-3 col-md-3 text-center q-px-sm relative-position z-top">
          <div class="podium-card silver shadow-1 animate-up-delay-1">
            <q-avatar size="60px" class="podium-avatar shadow-2">
              <img :src="leaderboard[1].avatar_url || defaultAvatar" />
              <div class="badge-rank ">2</div>
            </q-avatar>
            <div class="q-mt-md">
              <div class="text-weight-bold text-grey-9 ellipsis text-subtitle2">{{ leaderboard[1].full_name.split(' ')[0] }}</div>
              <div class="text-h6 text-primary text-weight-bolder lh-tight">{{ formatScore(leaderboard[1].primary_metric_value) }}</div>
              <div class="text-caption text-grey-6 text-uppercase font-mono">{{ unit }}</div>
            </div>
          </div>
        </div>

        <div v-if="leaderboard[0]" class="col-5 col-sm-4 col-md-3 text-center q-px-sm relative-position z-max">
          <div class="podium-card gold shadow-3 animate-up">
            <q-icon name="workspace_premium" class="crown-icon text-amber-8" size="32px" />
            <q-avatar size="90px" class="podium-avatar shadow-3 ring-gold">
              <img :src="leaderboard[0].avatar_url || defaultAvatar" />
              <div class="badge-rank bg-amber-8">1</div>
            </q-avatar>
            <div class="q-mt-md">
              <div class="text-weight-bold text-grey-9 ellipsis text-subtitle1">{{ leaderboard[0].full_name }}</div>
              <div class="text-h4 text-primary text-weight-bolder lh-tight">{{ formatScore(leaderboard[0].primary_metric_value) }}</div>
              <div class="text-caption text-grey-6 text-uppercase font-mono">{{ unit }}</div>
              <q-chip dense color="amber-1" text-color="amber-9" class="q-mt-sm" icon="star">Líder</q-chip>
            </div>
          </div>
        </div>

        <div v-if="leaderboard[2]" class="col-4 col-sm-3 col-md-3 text-center q-px-sm relative-position z-top">
          <div class="podium-card bronze shadow-1 animate-up-delay-2">
            <q-avatar size="60px" class="podium-avatar shadow-2">
              <img :src="leaderboard[2].avatar_url || defaultAvatar" />
              <div class="badge-rank bg-brown-5">3</div>
            </q-avatar>
            <div class="q-mt-md">
              <div class="text-weight-bold text-grey-9 ellipsis text-subtitle2">{{ leaderboard[2].full_name.split(' ')[0] }}</div>
              <div class="text-h6 text-primary text-weight-bolder lh-tight">{{ formatScore(leaderboard[2].primary_metric_value) }}</div>
              <div class="text-caption text-grey-6 text-uppercase font-mono">{{ unit }}</div>
            </div>
          </div>
        </div>
      </div>

      <q-card flat class=" rounded-borders border-gray shadow-sm overflow-hidden animate-fade">
        <q-list separator>
          <q-item-label header class="bg text-grey-7 text-uppercase text-caption text-weight-bold q-py-sm">
            Classificação Geral
          </q-item-label>
          
          <q-item v-for="(user, index) in leaderboard" :key="user.id" clickable v-ripple class="q-py-md hover-effect">
            <q-item-section side style="width: 40px" class="text-center">
              <div v-if="index < 3" class="text-h6">
                 <q-icon :name="getMedalIcon(index)" :color="getMedalColor(index)" />
              </div>
              <div v-else class="text-h6 text-grey-5 font-mono">{{ index + 1 }}</div>
            </q-item-section>

            <q-item-section avatar>
              <q-avatar size="42px">
                <img :src="user.avatar_url || defaultAvatar" />
              </q-avatar>
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-subtitle1 text-weight-bold text-grey-9">{{ user.full_name }}</q-item-label>
              <div class="row items-center q-gutter-x-sm text-caption text-grey-6">
                <span class="row items-center"><q-icon name="local_shipping" size="14px" class="q-mr-xs"/> {{ user.total_journeys }} viagens</span>
                <span>&bull;</span>
                <span>Eficiência: 98%</span>
              </div>
            </q-item-section>

            <q-item-section side class="text-right">
              <q-item-label class="text-h6 text-weight-bold text-primary font-mono">
                {{ formatScore(user.primary_metric_value) }}
              </q-item-label>
              <q-item-label caption class="text-uppercase">{{ unit }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>

    <div v-else class="column flex-center q-pa-xl text-grey-6">
      <div class=" q-pa-xl rounded-borders text-center border-dashed">
        <q-icon name="leaderboard" size="4em" color="grey-  " />
        <div class="text-h6 text-grey-8 q-mt-md">Sem dados de performance</div>
        <p class="q-mt-sm">Não há registros suficientes neste período para gerar o ranking.</p>
        <q-btn outline color="primary" label="Atualizar" @click="refreshData" />
      </div>
    </div>

  </q-page>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue';
import { useLeaderboardStore } from 'stores/leaderboard-store';
import defaultAvatar from '../assets/default-avatar.png';

const leaderboardStore = useLeaderboardStore();
const period = ref('month'); // Filtro de período

const leaderboard = computed(() => leaderboardStore.leaderboard);
const unit = computed(() => leaderboardStore.unit);

async function refreshData() {
  // Aqui você pode passar o "period" para a store se sua API suportar filtros
  await leaderboardStore.fetchLeaderboard();
}

function formatScore(val: number): string {
  return val % 1 === 0 ? val.toString() : val.toFixed(1);
}

function getMedalIcon(index: number): string {
  if (index === 0) return 'emoji_events';
  if (index === 1) return 'workspace_premium';
  if (index === 2) return 'workspace_premium';
  return '';
}

function getMedalColor(index: number): string {
  if (index === 0) return 'amber-8';
  if (index === 1) return 'blue-grey-4';
  if (index === 2) return 'brown-5';
  return 'grey';
}

onMounted(() => {
  void refreshData();
});
</script>

<style scoped lang="scss">
.border-gray {
  border: 1px solid #ffffff67;
}

.border-dashed {
  border: 2px dashed #e0e0e0;
}

.lh-tight {
  line-height: 1.1;
}

.font-mono {
  font-family: 'Roboto Mono', monospace;
}

/* PODIUM STYLES */
.podium-card {
  padding: 24px 12px 16px;
  border-radius: 16px;
  background: white;
  position: relative;
  transition: all 0.3s ease;
  height: 100%;
  
  /* Glass/Gradient Effect */
  &.gold {
    background: linear-gradient(180deg, #fffcf5 0%, #ffffff 100%);
    border: 1px solid #ffe082;
    transform: scale(1.05);
    z-index: 2;
  }
  
  &.silver {
    background: linear-gradient(180deg, #f7f9fa 0%, #ffffff 100%);
    border: 1px solid #cfd8dc;
    margin-top: 20px;
  }
  
  &.bronze {
    background: linear-gradient(180deg, #fff8f5 0%, #ffffff 100%);
    border: 1px solid #d7ccc8;
    margin-top: 40px;
  }

  &:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  }
}

.crown-icon {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
  animation: float 3s ease-in-out infinite;
}

.podium-avatar {
  border: 3px solid white;
  position: relative;
}

.ring-gold {
  border-color: #ffc107;
}

.badge-rank {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  color: rgb(255, 255, 255);
  font-size: 10px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

/* LIST STYLES */
.hover-effect {
  transition: background-color 0.2s;
  &:hover {
    background-color: rgba(255, 255, 255, 0.158);
  }
}

/* ANIMATIONS */
@keyframes float {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-5px); }
}

.animate-up {
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.animate-up-delay-1 {
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.1s backwards;
}
.animate-up-delay-2 {
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.2s backwards;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* DARK MODE OVERRIDES */
body.body--dark {
  .podium-card {
    background: #1d1d1d;
    &.gold { border-color: #ffd700; background: linear-gradient(180deg, #2a2510 0%, #1d1d1d 100%); }
    &.silver { border-color: #78909c; background: linear-gradient(180deg, #263238 0%, #1d1d1d 100%); }
    &.bronze { border-color: #8d6e63; background: linear-gradient(180deg, #3e2723 0%, #1d1d1d 100%); }
  }
  .bg-white { background: #1d1d1d !important; }
  .text-grey-9 { color: #f5f5f5 !important; }
  .podium-avatar { border-color: #1d1d1d; }
}
</style>