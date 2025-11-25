<template>
  <div class="fullscreen flex flex-center text-center q-pa-md" :class="$q.dark.isActive ? 'bg-dark' : 'bg-grey-1'">
    
    <div class="animate-pop" style="max-width: 500px">
      <div class="relative-position inline-block q-mb-xl">
         <div class="absolute-center bg-primary opacity-10 rounded-circle" style="width: 200px; height: 200px;"></div>
         
         <q-icon name="map" size="120px" :color="$q.dark.isActive ? 'grey-8' : 'grey-4'" />
         
         <div class="absolute-bottom-right float-animation" style="right: -20px; bottom: -10px">
            <div class="bg-white q-pa-sm rounded-borders shadow-3 row flex-center" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-white'">
               <q-icon name="question_mark" color="negative" size="20px" class="absolute-top-right" style="top: -10px; right: -5px" />
               <q-icon name="directions_car" size="48px" color="primary" />
            </div>
         </div>
      </div>

      <div class="text-h1 text-weight-bolder text-primary q-my-none font-mono tracking-tighter line-height-1">
        404
      </div>
      
      <div class="text-h5 text-weight-bold q-mt-sm" :class="$q.dark.isActive ? 'text-grey-3' : 'text-grey-9'">
        Destino não encontrado
      </div>

      <p class="text-body1 q-mt-md q-mb-xl" :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-6'">
        Parece que você pegou um desvio para uma estrada que não existe ou foi movida. Vamos recalcular a rota?
      </p>

      <div class="row justify-center q-gutter-md">
        <q-btn
          outline
          :color="$q.dark.isActive ? 'grey-5' : 'grey-7'"
          label="Voltar página"
          icon="arrow_back"
          @click="router.back()"
          no-caps
          class="rounded-borders q-px-lg"
        />
        <q-btn
          unelevated
          color="primary"
          to="/"
          label="Ir para o Início"
          icon-right="home"
          no-caps
          class="rounded-borders q-px-lg shadow-2"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar'; // <--- 1. Importar useQuasar

const router = useRouter(); 
const $q = useQuasar(); // <--- 2. Instanciar e expor para o template
</script>

<style scoped lang="scss">
.font-mono {
  font-family: 'Roboto Mono', monospace;
}

.tracking-tighter {
  letter-spacing: -4px;
}

.line-height-1 {
  line-height: 1;
}

.rounded-circle {
  border-radius: 50%;
}

.opacity-10 {
  opacity: 0.1;
}

/* Animação suave de entrada */
.animate-pop {
  animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* Animação flutuante para o carro */
.float-animation {
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>