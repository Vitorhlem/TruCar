import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';

// Define a estrutura da resposta do nosso backend
interface AddressResponse {
  street: string;
  neighborhood: string;
  city: string;
  state: string;
}

export function useCepApi() {
  const isCepLoading = ref(false);

  const fetchAddressByCep = async (cep: string): Promise<AddressResponse | null> => {
    // Limpa o CEP, deixando apenas os dígitos
    const numericCep = cep.replace(/\D/g, '');

    if (numericCep.length !== 8) {
      return null;
    }

    isCepLoading.value = true;
    try {
      const response = await api.get<AddressResponse>(`/utils/cep/${numericCep}`);
      return response.data;
    } catch (error) {
      // CORRIGIDO: Utiliza a variável 'error' para o log
      console.error("Erro ao buscar CEP:", error); 
      Notify.create({
        type: 'negative',
        message: 'CEP não encontrado ou inválido.',
        icon: 'o_wrong_location'
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
