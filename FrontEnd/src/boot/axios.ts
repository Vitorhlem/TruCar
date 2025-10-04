// src/boot/axios.ts
import { boot } from 'quasar/wrappers';
// Importe o tipo InternalAxiosRequestConfig em vez de AxiosRequestConfig
import { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'; 
import { useAuthStore } from 'stores/auth-store';
import api from 'src/services/api';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}



export default boot(({ app, store }) => {
  // Use o tipo 'InternalAxiosRequestConfig' que é o correto para interceptors
  api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore(store);
    
    // Com o tipo correto, 'headers' já é garantido como existente.
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`;
    }
    
    return config;
  });

  // Injete a instância da API nas propriedades globais do Vue
  app.config.globalProperties.$api = api;
});

export { api };