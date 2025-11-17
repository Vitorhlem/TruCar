import { boot } from 'quasar/wrappers';
import VueApexCharts from 'vue3-apexcharts';


export default boot(({ app }) => {
  app.component('ApexChart', VueApexCharts);
});