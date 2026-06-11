import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTrends } from '../../hooks/useAnalytics';

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-white/10 bg-[#1a1a2e]/95 backdrop-blur-xl px-4 py-3 shadow-xl">
      <p className="text-xs text-white/50">{label}</p>
      <p className="text-sm font-semibold text-white">₹{payload[0].value.toLocaleString('en-IN')}</p>
    </div>
  );
};

export default function RevenueChart() {
  const { data: trendData, isLoading } = useTrends();

  const chartData = (trendData || []).map(t => {
    const d = new Date(t.date);
    return {
      date: d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
      revenue: t.revenue,
    };
  });

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
      <h3 className="text-sm font-semibold text-white mb-4">Revenue Recovery (30 Days)</h3>
      {isLoading ? (
        <div className="h-[280px] flex items-center justify-center text-sm text-white/40">
          Loading charts...
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-[280px] flex items-center justify-center text-sm text-white/40">
          No revenue recovery data logged yet.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} interval={4} />
            <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="revenue" stroke="#8b5cf6" strokeWidth={2} fill="url(#revenueGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
