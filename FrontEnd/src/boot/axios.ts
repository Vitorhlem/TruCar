import { boot } from 'quasar/wrappers';
import axios, { type AxiosInstance } from 'axios'; // <-- CORREÇÃO AQUI
import { useAuthStore } from 'stores/auth-store';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

const api = axios.create({ baseURL: 'https://trucar-api.onrender.com/' });

export default boot(({ app, store }) => {
  api.interceptors.request.use((config) => {
    const authStore = useAuthStore(store);
    
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`;
    }
    return config;
  });

  app.config.globalProperties.$api = api;
});

export { api };