import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useState, useMemo } from 'react';
import { Loader2 } from 'lucide-react';
import { useTrends } from '../../hooks/useAnalytics';

const rangeMap: Record<string, number> = { '7d': 7, '30d': 30, '90d': 90 };

export default function TrendChart() {
  const [range, setRange] = useState('30d');
  const { data: rawData, isLoading } = useTrends(String(rangeMap[range]));

  const data = useMemo(() => {
    if (!rawData) return [];
    return rawData.map((t: any) => ({
      date: new Date(t.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
      leads: t.leads,
      conversions: t.conversions,
      revenue: Number(t.revenue || 0),
    }));
  }, [rawData]);

  const ranges = ['7d', '30d', '90d'];

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-white">Performance Trends</h3>
        <div className="flex gap-1">
          {ranges.map(r => (
            <button key={r} onClick={() => setRange(r)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${range === r ? 'bg-violet-500/20 text-violet-400' : 'text-white/40 hover:text-white/60'}`}>
              {r}
            </button>
          ))}
        </div>
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center h-[300px]"><Loader2 className="w-6 h-6 text-violet-400 animate-spin" /></div>
      ) : data.length === 0 ? (
        <div className="flex items-center justify-center h-[300px] text-xs text-white/40">No trend data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} interval={Math.max(Math.floor(data.length / 8), 1)} />
            <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} />
            <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="leads" stroke="#8b5cf6" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="conversions" stroke="#10b981" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
