import { defineStore } from 'pinia';
import { Dark } from 'quasar';

// Define o tipo do estado para ajudar o TypeScript
interface SettingsState {
  darkMode: boolean | 'auto';
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    // Tenta ler a preferência do localStorage, ou usa 'auto' como padrão
    darkMode: localStorage.getItem('darkMode') || 'auto',
  }),

  actions: {
    /**
     * Define o estado do modo escuro e aplica-o globalmente com o Quasar.
     * Também guarda a preferência no localStorage para persistir entre sessões.
     * @param mode O estado desejado: true (escuro), false (claro), ou 'auto'.
     */
    setDarkMode(mode: boolean | 'auto') {
      this.darkMode = mode;
      Dark.set(mode); // Comando do Quasar para aplicar o tema
      
      // Guarda a preferência
      if (typeof mode === 'boolean') {
        localStorage.setItem('darkMode', mode.toString());
      } else {
        localStorage.setItem('darkMode', 'auto');
      }
    },

    /**
     * Função de inicialização para ser chamada quando a aplicação arranca.
     * Garante que a preferência de tema do utilizador seja aplicada.
     */
    init() {
      // Usamos 'isActive' para lidar com o caso 'auto' na primeira vez
      Dark.set(Dark.isActive);
    }
  },
});