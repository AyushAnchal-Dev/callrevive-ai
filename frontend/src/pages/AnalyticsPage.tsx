import { motion } from 'framer-motion';
import { Target, DollarSign, TrendingUp, Calendar, Loader2 } from 'lucide-react';
import TrendChart from '../components/analytics/TrendChart';
import ConversionFunnel from '../components/analytics/ConversionFunnel';
import RevenueRecoveryChart from '../components/analytics/RevenueRecoveryChart';
import { useOverview } from '../hooks/useAnalytics';

export default function AnalyticsPage() {
  const { data: overview, isLoading } = useOverview();

  const miniStats = [
    { label: 'Conversion Rate', value: isLoading ? '...' : `${overview?.recoveryRate ?? 0}%`, icon: TrendingUp, color: 'from-emerald-500 to-teal-500' },
    { label: 'Avg Deal Value', value: isLoading ? '...' : `₹${Math.round((overview?.revenueRecovered ?? 0) / Math.max(overview?.totalLeads ?? 1, 1)).toLocaleString('en-IN')}`, icon: DollarSign, color: 'from-violet-500 to-indigo-500' },
    { label: 'Recovery Rate', value: isLoading ? '...' : `${overview?.recoveryRate ?? 0}%`, icon: Target, color: 'from-amber-500 to-orange-500' },
    { label: 'Total Leads', value: isLoading ? '...' : String(overview?.totalLeads ?? 0), icon: Calendar, color: 'from-blue-500 to-cyan-500' },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div><h1 className="text-2xl font-bold text-white">Analytics</h1><p className="text-sm text-white/40">Deep insights into your business performance</p></div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {miniStats.map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-4">
            <div className="flex items-center gap-3">
              <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${s.color} flex items-center justify-center`}><s.icon className="w-4 h-4 text-white" /></div>
              <div><p className="text-lg font-bold text-white">{s.value}</p><p className="text-[10px] text-white/40">{s.label}</p></div>
            </div>
          </motion.div>
        ))}
      </div>
      <TrendChart />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ConversionFunnel />
        <RevenueRecoveryChart />
      </div>
    </motion.div>
  );
}
