// src/services/api.ts
import axios from 'axios';

// Esta função determina a URL base da API com base no ambiente
const getBaseURL = () => {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
};

const api = axios.create({
    baseURL: getBaseURL(),
    withCredentials: true,
});

export default api;
// EXPORTAÇÃO NOMEADA ADICIONADA: O arquivo de boot precisa disso.
export { api };