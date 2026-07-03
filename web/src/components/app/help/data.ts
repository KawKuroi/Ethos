// Preguntas frecuentes de Ayuda (del prototipo App Ethos.dc.html).
export type Faq = { q: string; a: string };

export const FAQS: Faq[] = [
  {
    q: "¿Para qué sirve Ethos?",
    a: "Reúne tu gusto de muchas apps en un mismo esquema y lo convierte en contexto para tu IA. Ese contexto lo puedes descargar como archivos o servirlo en vivo como un servidor MCP.",
  },
  {
    q: "¿Cómo le doy mi contexto a la IA?",
    a: "De dos formas: descargas los archivos de contexto (.json) y se los pasas tú, o conectas Ethos como servidor MCP y tu IA lo consulta directamente.",
  },
  {
    q: "¿La IA carga todo mi perfil cada vez?",
    a: 'No. El servidor MCP expone un resumen y tools de consulta acotadas. Solo se entrega lo que la consulta pide — por eso ves "0,4 KB de 84 KB".',
  },
  {
    q: "¿Qué pasa si cambio de proveedor en una categoría?",
    a: "Te preguntamos si conservar el histórico ya normalizado o reemplazarlo por el del nuevo proveedor. Tú decides en cada cambio.",
  },
  {
    q: "¿Y si una fuente no tiene API?",
    a: "Subes su export (.json, .csv, .zip) y Ethos lo parsea contra el mismo esquema, o añades las entradas a mano.",
  },
];
