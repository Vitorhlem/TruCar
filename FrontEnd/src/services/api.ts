// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.API_URL || 'https://trucar-api.onrender.com/', // Adapte para a URL do seu backend
  withCredentials: true,
});

export default api;