import { defineStore } from 'pinia';
import { Dark } from 'quasar';

interface SettingsState {
  darkMode: boolean | 'auto';
}

// Função auxiliar para ler e converter o valor do localStorage
function getInitialDarkMode(): boolean | 'auto' {
  const storedValue = localStorage.getItem('darkMode');
  if (storedValue === 'true') return true;
  if (storedValue === 'false') return false;
  return 'auto'; // Padrão
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    // Usamos a função auxiliar para definir o estado inicial corretamente
    darkMode: getInitialDarkMode(),
  }),

  actions: {
    setDarkMode(mode: boolean | 'auto') {
      this.darkMode = mode;
      Dark.set(mode);
      // Salvamos como string, que é como o localStorage funciona
      localStorage.setItem('darkMode', String(mode));
    },

    // A função init agora lê o estado e aplica-o
    init() {
      Dark.set(this.darkMode);
    }
  },
});