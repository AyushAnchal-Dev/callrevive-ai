import { motion } from 'framer-motion';
import { Target, Flame, DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { useOverview } from '../../hooks/useAnalytics';

export default function StatsCards() {
  const { data: overview, isLoading } = useOverview();

  const stats = [
    {
      label: 'Total Leads',
      value: isLoading ? '...' : String(overview?.totalLeads ?? 0),
      trend: overview?.totalLeadsTrend ?? 0,
      icon: Target,
      color: 'from-indigo-500 to-violet-500',
    },
    {
      label: 'Hot Leads',
      value: isLoading ? '...' : String(overview?.hotLeads ?? 0),
      trend: overview?.hotLeadsTrend ?? 0,
      icon: Flame,
      color: 'from-rose-500 to-pink-500',
      pulse: (overview?.hotLeads ?? 0) > 0,
    },
    {
      label: 'Revenue Recovered',
      value: isLoading ? '...' : `₹${(overview?.revenueRecovered ?? 0).toLocaleString('en-IN')}`,
      trend: overview?.revenueRecoveredTrend ?? 0,
      icon: DollarSign,
      color: 'from-emerald-500 to-teal-500',
    },
    {
      label: 'Recovery Rate',
      value: isLoading ? '...' : `${overview?.recoveryRate ?? 0}%`,
      trend: overview?.recoveryRateTrend ?? 0,
      icon: TrendingUp,
      color: 'from-amber-500 to-orange-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {stats.map((stat, i) => {
        const isPositive = stat.trend >= 0;
        const TrendIcon = isPositive ? TrendingUp : TrendingDown;
        const trendLabel = stat.label === 'Hot Leads'
          ? `${isPositive ? '+' : ''}${stat.trend}`
          : `${isPositive ? '+' : ''}${stat.trend}%`;

        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.4 }}
            className="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-5 hover:border-white/20 transition-all duration-300 group"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-white/50 uppercase tracking-wider">{stat.label}</p>
                <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                <p className={`text-xs mt-1 flex items-center gap-1 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  <TrendIcon className="w-3 h-3" /> {trendLabel}
                </p>
              </div>
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg ${stat.pulse ? 'animate-pulse' : ''}`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
          </motion.div>
        );
      })}
    </div>
  );
}
