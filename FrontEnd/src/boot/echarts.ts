import { boot } from 'quasar/wrappers';
import ECharts from 'vue-echarts';
import { use } from 'echarts/core';

// Importe os módulos necessários do ECharts
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, PieChart, LineChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components';

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
]);

export default boot(({ app }) => {
  app.component('VChart', ECharts);
});