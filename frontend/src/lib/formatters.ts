export function formatCurrency(value: number): string {
  return (
    "$" +
    value.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
}

export function formatPercent(value: number): string {
  return `${value.toFixed(2)}%`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString();
}

export function pnlColor(value: number): string {
  return value >= 0 ? "text-green-400" : "text-red-400";
}

