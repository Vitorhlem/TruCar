// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.API_URL || 'http://localhost:8000', // Adapte para a URL do seu backend
  withCredentials: true,
});

export default api;