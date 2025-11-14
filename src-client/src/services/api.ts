// src/services/api.ts
import axios from 'axios';

// Esta função determina a URL base da API com base no ambiente
const getBaseURL = () => {
  // 'process.env.DEV' é uma variável booleana injetada pelo Quasar
  // que é 'true' quando você roda o projeto com 'quasar dev'
  if (process.env.DEV) {
    return 'http://localhost:8000/'; // URL para desenvolvimento local
  }
  // Para qualquer outro caso (como ao gerar o build para produção),
  // ele usará a URL do servidor na nuvem.
  return 'https://trucar-at4e.onrender.com'; // URL para produção
};

const api = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
});

export default api;