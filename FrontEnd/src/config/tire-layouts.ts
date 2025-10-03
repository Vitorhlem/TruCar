export const axleLayouts: Record<string, { label: string; code: string; }[][]> = {
  // --- VEÍCULOS LEVES E MÉDIOS ---
  'VUC_4x2_SIMPLES': [ // VUC / Furgão / Camionete com rodado simples
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq.', code: '2E' }, { label: 'Eixo 2 - Dir.', code: '2D' }]
  ],

  // --- CAMINHÕES (CAVALO/RÍGIDO) ---
  '4x2': [ // Toco / Cavalo Simples com rodado duplo
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }]
  ],
  '6x2': [ // Truck / Cavalo Trucado
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }],
    [{ label: 'Eixo 3 - Esq. Int.', code: '3EI' }, { label: 'Eixo 3 - Esq. Ext.', code: '3EE' }, { label: 'Eixo 3 - Dir. Int.', code: '3DI' }, { label: 'Eixo 3 - Dir. Ext.', code: '3DE' }]
  ],
  '6x4': [ // Cavalo Traçado
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }],
    [{ label: 'Eixo 3 - Esq. Int.', code: '3EI' }, { label: 'Eixo 3 - Esq. Ext.', code: '3EE' }, { label: 'Eixo 3 - Dir. Int.', code: '3DI' }, { label: 'Eixo 3 - Dir. Ext.', code: '3DE' }]
  ],
  '8x2': [ // Bitruck Direcional
    [{ label: 'Eixo 1 - Esq.', code: '1E' }, { label: 'Eixo 1 - Dir.', code: '1D' }],
    [{ label: 'Eixo 2 - Esq.', code: '2E' }, { label: 'Eixo 2 - Dir.', code: '2D' }],
    [{ label: 'Eixo 3 - Esq. Int.', code: '3EI' }, { label: 'Eixo 3 - Esq. Ext.', code: '3EE' }, { label: 'Eixo 3 - Dir. Int.', code: '3DI' }, { label: 'Eixo 3 - Dir. Ext.', code: '3DE' }],
    [{ label: 'Eixo 4 - Esq. Int.', code: '4EI' }, { label: 'Eixo 4 - Esq. Ext.', code: '4EE' }, { label: 'Eixo 4 - Dir. Int.', code: '4DI' }, { label: 'Eixo 4 - Dir. Ext.', code: '4DE' }]
  ],

  // --- IMPLEMENTOS (CARRETAS) ---
  'CARRETA_2_EIXOS': [
    [{ label: 'Eixo 1 - Esq. Int.', code: '1EI' }, { label: 'Eixo 1 - Esq. Ext.', code: '1EE' }, { label: 'Eixo 1 - Dir. Int.', code: '1DI' }, { label: 'Eixo 1 - Dir. Ext.', code: '1DE' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }]
  ],
  'CARRETA_3_EIXOS': [
    [{ label: 'Eixo 1 - Esq. Int.', code: '1EI' }, { label: 'Eixo 1 - Esq. Ext.', code: '1EE' }, { label: 'Eixo 1 - Dir. Int.', code: '1DI' }, { label: 'Eixo 1 - Dir. Ext.', code: '1DE' }],
    [{ label: 'Eixo 2 - Esq. Int.', code: '2EI' }, { label: 'Eixo 2 - Esq. Ext.', code: '2EE' }, { label: 'Eixo 2 - Dir. Int.', code: '2DI' }, { label: 'Eixo 2 - Dir. Ext.', code: '2DE' }],
    [{ label: 'Eixo 3 - Esq. Int.', code: '3EI' }, { label: 'Eixo 3 - Esq. Ext.', code: '3EE' }, { label: 'Eixo 3 - Dir. Int.', code: '3DI' }, { label: 'Eixo 3 - Dir. Ext.', code: '3DE' }]
  ],

  // --- AGRONEGÓCIO ---
  'TRATOR_4x4': [
    [{ label: 'Diant. Esq.', code: 'DE' }, { label: 'Diant. Dir.', code: 'DD' }],
    [{ label: 'Tras. Esq.', code: 'TE' }, { label: 'Tras. Dir.', code: 'TD' }]
  ]
};