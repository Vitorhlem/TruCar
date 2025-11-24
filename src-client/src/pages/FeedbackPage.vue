<template>
  <q-page class="q-pa-md q-pa-lg-xl flex flex-center">
    
    <div class="full-width" style="max-width: 800px">
      
      <div class="text-center q-mb-xl">
        <q-avatar size="80px" font-size="40px" color="primary" text-color="white" icon="support_agent" class="shadow-3 q-mb-md" />
        <h1 class="text-h4 text-weight-bolder q-my-none text-primary">Central de Ajuda</h1>
        <div class="text-subtitle1 text-grey-7 q-mt-sm" :class="{ 'text-grey-5': $q.dark.isActive }">
          Encontrou um erro ou tem uma ideia brilhante? Conte para nós.
        </div>
      </div>

      <q-card flat bordered :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-white'">
        <q-card-section class="q-pa-lg">
          <q-form @submit="onSubmit" class="q-gutter-y-lg">
            
            <div>
              <div class="text-subtitle2 q-mb-sm">Qual é o motivo do contato?</div>
              <div class="row q-col-gutter-sm">
                <div class="col-12 col-sm-4" v-for="type in typeOptions" :key="type.value">
                  <q-card 
                    flat 
                    bordered 
                    class="cursor-pointer transition-generic full-height"
                    :class="[
                      form.type === type.value 
                        ? ($q.dark.isActive ? 'bg-primary-dark text-white border-primary' : 'bg-blue-1 text-primary border-primary') 
                        : ($q.dark.isActive ? 'bg-grey-8' : 'bg-grey-1')
                    ]"
                    @click="form.type = type.value"
                  >
                    <q-card-section class="column flex-center q-py-lg">
                      <q-icon :name="type.icon" size="md" :color="form.type === type.value ? 'inherit' : type.color" class="q-mb-sm" />
                      <div class="text-weight-bold">{{ type.label }}</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <q-input
              outlined
              v-model="form.message"
              type="textarea"
              label="Descreva os detalhes *"
              :placeholder="placeholderText"
              hint="Quanto mais detalhes, mais rápido poderemos ajudar."
              rows="6"
              :bg-color="$q.dark.isActive ? 'grey-8' : 'white'"
              :rules="[val => !!val && val.length > 10 || 'A descrição deve ter pelo menos 10 caracteres']"
            >
               <template v-slot:prepend><q-icon name="description" /></template>
            </q-input>

            <div>
                <q-file
                  v-model="screenshotFile"
                  label="Anexar Captura de Tela (Opcional)"
                  outlined
                  dense
                  accept="image/*"
                  :bg-color="$q.dark.isActive ? 'grey-8' : 'white'"
                  @update:model-value="onFileSelected"
                >
                  <template v-slot:prepend><q-icon name="attach_file" /></template>
                  <template v-slot:append>
                     <q-icon name="close" @click.stop="clearFile" v-if="screenshotFile" class="cursor-pointer" />
                  </template>
                </q-file>

                <div v-if="screenshotPreview" class="q-mt-sm row items-center q-pa-sm rounded-borders" :class="$q.dark.isActive ? 'bg-grey-8' : 'bg-grey-2'">
                    <q-img :src="screenshotPreview" width="60px" height="60px" fit="cover" class="rounded-borders q-mr-md" />
                    <div class="text-caption text-grey-7">
                        Imagem anexada para análise.
                    </div>
                </div>
            </div>

            <q-separator />

            <div class="row justify-end items-center q-gutter-sm">
              <q-btn label="Cancelar" flat color="grey-7" to="/dashboard" />
              <q-btn 
                :label="submitLabel" 
                type="submit" 
                color="primary" 
                :loading="loading" 
                icon="send" 
                unelevated
                size="md"
                padding="8px 24px"
              />
            </div>

          </q-form>
        </q-card-section>
      </q-card>
      
      <div class="text-center q-mt-lg text-grey-6 text-caption">
        Sua identidade e dados do navegador serão enviados automaticamente para agilizar o suporte.
      </div>

    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';

const $q = useQuasar();
const router = useRouter();
const loading = ref(false);
const screenshotFile = ref<File | null>(null);
const screenshotPreview = ref<string | null>(null);

const form = ref({
  type: 'BUG',
  message: ''
});

const typeOptions = [
  { label: 'Reportar Erro', value: 'BUG', icon: 'bug_report', color: 'negative' },
  { label: 'Sugestão', value: 'SUGESTAO', icon: 'lightbulb', color: 'warning' },
  { label: 'Outro', value: 'OUTRO', icon: 'chat', color: 'primary' }
];

const placeholderText = computed(() => {
    if (form.value.type === 'BUG') return 'Ex: Ao tentar salvar um pneu, recebi um erro 500...';
    if (form.value.type === 'SUGESTAO') return 'Ex: Seria ótimo ter um gráfico de consumo por rota...';
    return 'Como podemos ajudar?';
});

const submitLabel = computed(() => {
    if (form.value.type === 'BUG') return 'Reportar Problema';
    if (form.value.type === 'SUGESTAO') return 'Enviar Ideia';
    return 'Enviar Mensagem';
});

function onFileSelected(val: File | null) {
    if (val) {
        screenshotPreview.value = URL.createObjectURL(val);
    } else {
        screenshotPreview.value = null;
    }
}

function clearFile() {
    screenshotFile.value = null;
    screenshotPreview.value = null;
}

async function onSubmit() {
  loading.value = true;
  try {
    // Mudança para FormData para permitir envio de arquivo
    const formData = new FormData();
    formData.append('type', form.value.type);
    formData.append('message', form.value.message);
    
    if (screenshotFile.value) {
        formData.append('file', screenshotFile.value);
    }

    // Nota: O Content-Type multipart/form-data é setado automaticamente pelo browser/axios ao usar FormData
    await api.post('/feedback/', formData);
    
    $q.notify({
      type: 'positive',
      message: 'Recebemos seu feedback! A equipe de produto analisará em breve.',
      position: 'top',
      timeout: 3000
    });
    
    router.push({ name: 'dashboard' });
  } catch (error) {
    console.error(error);
    $q.notify({
      type: 'negative',
      message: 'Erro ao enviar. Verifique sua conexão e tente novamente.'
    });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped lang="scss">
.border-primary {
    border: 2px solid var(--q-primary);
}

.transition-generic {
    transition: all 0.3s ease;
    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
}

.bg-primary-dark {
    background-color: rgba($primary, 0.2) !important;
}
</style>