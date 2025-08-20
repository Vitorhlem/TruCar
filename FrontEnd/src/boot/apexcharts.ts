import { boot } from 'quasar/wrappers';
import VueApexCharts from 'vue3-apexcharts';

// Usaremos 'ApexChart' como o nome oficial do nosso componente
export default boot(({ app }) => {
  app.component('ApexChart', VueApexCharts);
});