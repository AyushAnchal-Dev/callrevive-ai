import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Loader2 } from 'lucide-react';
import { useRevenueAnalytics } from '../../hooks/useAnalytics';

export default function RevenueRecoveryChart() {
  const { data: revenueData, isLoading } = useRevenueAnalytics();

  // revenueData is the monthly_data array from the API
  const data = (revenueData && Array.isArray(revenueData) ? revenueData : []).map((d: any) => ({
    month: d.month || d.date || 'N/A',
    potential: Number(d.potential || d.predicted || 0),
    recovered: Number(d.recovered || d.actual || 0),
  }));

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
      <h3 className="text-sm font-semibold text-white mb-4">Revenue: Potential vs Recovered</h3>
      {isLoading ? (
        <div className="flex items-center justify-center h-[280px]"><Loader2 className="w-6 h-6 text-violet-400 animate-spin" /></div>
      ) : data.length === 0 ? (
        <div className="flex items-center justify-center h-[280px] text-xs text-white/40">No revenue data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="month" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
            <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
            <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', fontSize: 12 }} formatter={(v: any) => `₹${v.toLocaleString('en-IN')}`} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="potential" fill="rgba(100,116,139,0.5)" name="Potential" radius={[4, 4, 0, 0]} />
            <Bar dataKey="recovered" fill="#10b981" name="Recovered" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
