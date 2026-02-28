import { useState } from "react";
import { useSecurities } from "../hooks/useSecurities";
import { useTechnicalAnalysis } from "../hooks/useTechnicalAnalysis";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { formatCurrency } from "../lib/formatters";

export function TechnicalAnalysisPage() {
  const { data: securitiesData } = useSecurities();
  const securities = securitiesData?.items || [];
  const [selectedTicker, setSelectedTicker] = useState<string>("");
  const [selectedIndicators, setSelectedIndicators] = useState<string>("SMA_20,RSI_14,MACD");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  const { data: taData, isLoading } = useTechnicalAnalysis(
    selectedTicker,
    selectedIndicators,
    startDate || undefined,
    endDate || undefined
  );

  // Prepare chart data
  const chartData = taData?.price_bars.map((bar, idx) => {
    const data: any = {
      timestamp: new Date(bar.timestamp).toLocaleDateString(),
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
      volume: bar.volume,
    };

    // Add indicator values
    Object.entries(taData.indicators).forEach(([indicator, points]) => {
      if (points[idx]) {
        if (indicator === "MACD" && points[idx].parameters) {
          data.macd = points[idx].value;
          data.macd_signal = points[idx].parameters.signal?.[idx]?.value;
          data.macd_histogram = points[idx].parameters.histogram?.[idx]?.value;
        } else if (indicator === "BB_20" && points[idx].parameters) {
          data.bb_upper = points[idx].parameters.upper?.[idx]?.value;
          data.bb_middle = points[idx].value;
          data.bb_lower = points[idx].parameters.lower?.[idx]?.value;
        } else {
          data[indicator.toLowerCase()] = points[idx].value;
        }
      }
    });

    return data;
  }) || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Technical Analysis</h1>

      {/* Controls */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Ticker
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
            >
              <option value="">Select ticker</option>
              {securities?.map((s) => (
                <option key={s.id} value={s.ticker}>
                  {s.ticker}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Indicators (comma-separated)
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={selectedIndicators}
              onChange={(e) => setSelectedIndicators(e.target.value)}
              placeholder="SMA_20,RSI_14,MACD"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Start Date
            </label>
            <input
              type="date"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              End Date
            </label>
            <input
              type="date"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Chart */}
      {isLoading ? (
        <LoadingSpinner />
      ) : chartData.length > 0 ? (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="mb-4 text-sm font-semibold text-slate-200">
            Price Chart with Indicators
          </h2>
          <ResponsiveContainer width="100%" height={500}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="timestamp" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="close"
                stroke="#10b981"
                strokeWidth={2}
                name="Close Price"
                dot={false}
              />
              {selectedIndicators.includes("SMA_20") && (
                <Line
                  type="monotone"
                  dataKey="sma_20"
                  stroke="#3b82f6"
                  strokeWidth={1}
                  name="SMA 20"
                  dot={false}
                />
              )}
              {selectedIndicators.includes("RSI_14") && (
                <Line
                  type="monotone"
                  dataKey="rsi_14"
                  stroke="#f59e0b"
                  strokeWidth={1}
                  name="RSI 14"
                  dot={false}
                />
              )}
              {selectedIndicators.includes("MACD") && (
                <>
                  <Line
                    type="monotone"
                    dataKey="macd"
                    stroke="#8b5cf6"
                    strokeWidth={1}
                    name="MACD"
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="macd_signal"
                    stroke="#ec4899"
                    strokeWidth={1}
                    name="MACD Signal"
                    dot={false}
                  />
                </>
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : selectedTicker ? (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-center text-slate-400">
          No data available for {selectedTicker}
        </div>
      ) : (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-center text-slate-400">
          Select a ticker to view technical analysis
        </div>
      )}
    </div>
  );
}
