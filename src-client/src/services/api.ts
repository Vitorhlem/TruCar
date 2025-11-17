
import axios from 'axios';


const getBaseURL = () => {


  if (process.env.DEV) {
    return 'http:
  }


  return 'https:
};

const api = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
});

export default api;