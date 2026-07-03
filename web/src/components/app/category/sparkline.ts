// Mapea una serie a los puntos de un polyline en un viewBox 100×26 (como el
// helper `spark()` del prototipo). Se dibuja con vector-effect no escalado.
export function sparkPoints(values: number[]): string {
  const w = 100;
  const h = 26;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const span = max - min || 1;
  return values
    .map((v, i) => {
      const x = ((i / (values.length - 1)) * w).toFixed(1);
      const y = (h - ((v - min) / span) * (h - 4) - 2).toFixed(1);
      return `${x},${y}`;
    })
    .join(" ");
}
