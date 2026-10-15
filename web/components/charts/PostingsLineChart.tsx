"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DayCount } from "@/lib/queries";
import { AXIS_LINE, AXIS_TICK, CHART_COLORS, TOOLTIP_STYLE } from "./theme";

function label(date: string): string {
  return new Date(`${date}T12:00:00Z`).toLocaleDateString("en-CA", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default function PostingsLineChart({ data }: { data: DayCount[] }) {
  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
          <CartesianGrid vertical={false} stroke="#EFEBE3" />
          <XAxis
            dataKey="date"
            tickFormatter={label}
            tick={AXIS_TICK}
            axisLine={AXIS_LINE}
            tickLine={false}
            interval={4}
          />
          <YAxis tick={AXIS_TICK} axisLine={false} tickLine={false} allowDecimals={false} />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            labelFormatter={(d) => label(String(d))}
            formatter={(v) => [v ?? 0, "New postings"]}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke={CHART_COLORS[0]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
