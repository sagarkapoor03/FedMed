/**
 * Dual-axis training curve.
 *
 * Dice similarity and loss live on completely different scales (0-100 vs
 * 0-1), so they are plotted against separate Y axes. The baseline Dice is
 * drawn as a reference line so the federated-vs-centralized comparison is
 * visible at a glance.
 */
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function TrainingChart({ data, baselineDice, height = 300 }) {
  if (!data?.length) {
    return (
      <div className="chart chart-empty">
        <p>No rounds recorded yet.</p>
        <span>Start a federated run to stream live metrics.</span>
      </div>
    );
  }

  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 10, right: 12, left: -8, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="round"
            label={{ value: "Round", position: "insideBottom", offset: -4 }}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            yAxisId="dice"
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            label={{
              value: "Dice (%)",
              angle: -90,
              position: "insideLeft",
              style: { fill: "#2563eb", fontSize: 12 },
            }}
          />
          <YAxis
            yAxisId="loss"
            orientation="right"
            domain={["auto", "auto"]}
            tick={{ fontSize: 12 }}
            label={{
              value: "Loss",
              angle: 90,
              position: "insideRight",
              style: { fill: "#ef4444", fontSize: 12 },
            }}
          />
          <Tooltip
            contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0" }}
            formatter={(value, name) => {
              if (name === "Dice Score") return [`${value}%`, name];
              if (name === "Training Loss") return [Number(value).toFixed(4), name];
              return [value, name];
            }}
          />
          <Legend verticalAlign="top" height={28} />
          {baselineDice ? (
            <ReferenceLine
              yAxisId="dice"
              y={baselineDice}
              stroke="#16a34a"
              strokeDasharray="6 4"
              label={{
                value: `Centralized baseline ${baselineDice}%`,
                position: "insideTopLeft",
                fill: "#16a34a",
                fontSize: 11,
              }}
            />
          ) : null}
          <Line
            yAxisId="dice"
            type="monotone"
            dataKey="dice"
            name="Dice Score"
            stroke="#2563eb"
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            isAnimationActive={false}
          />
          <Line
            yAxisId="loss"
            type="monotone"
            dataKey="loss"
            name="Training Loss"
            stroke="#ef4444"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrainingChart;
