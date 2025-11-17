import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';


interface AddressResponse {
  street: string;
  neighborhood: string;
  city: string;
  state: string;
}

export function useCepApi() {
  const isCepLoading = ref(false);

  const fetchAddressByCep = async (cep: string): Promise<AddressResponse | null> => {

    const numericCep = cep.replace(/\D/g, '');

    if (numericCep.length !== 8) {
      return null;
    }

    isCepLoading.value = true;
    try {
      const response = await api.get<AddressResponse>(`/utils/cep/${numericCep}`);
      return response.data;
    } catch (error) {

      console.error("Erro ao buscar CEP:", error); 
      Notify.create({
        type: 'negative',
        message: 'CEP não encontrado ou inválido.',
        icon: 'wrong_location'
      });
      return null;
    } finally {
      isCepLoading.value = false;
    }
  };

  return {
    isCepLoading,
    fetchAddressByCep,
  };
}
