"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { SkillCount } from "@/lib/queries";
import { AXIS_LINE, AXIS_TICK, CHART_COLORS, TOOLTIP_STYLE } from "./theme";

const ROW_PX = 30;

/** Horizontal ranked bar chart; height grows with the number of skills. */
export default function SkillsBarChart({ data }: { data: SkillCount[] }) {
  return (
    <div className="w-full" style={{ height: Math.max(data.length * ROW_PX + 30, 120) }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 16, bottom: 0, left: 8 }}>
          <CartesianGrid horizontal={false} stroke="#EFEBE3" />
          <XAxis type="number" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} allowDecimals={false} />
          <YAxis
            type="category"
            dataKey="name"
            width={110}
            tick={AXIS_TICK}
            axisLine={false}
            tickLine={false}
            interval={0}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            cursor={{ fill: "#F7F5F0" }}
            formatter={(v) => [v ?? 0, "Postings"]}
          />
          {/* Rounded on the outer end; the vertical-chart equivalent of radius [4,4,0,0]. */}
          <Bar dataKey="count" fill={CHART_COLORS[0]} radius={[0, 4, 4, 0]} barSize={16} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
