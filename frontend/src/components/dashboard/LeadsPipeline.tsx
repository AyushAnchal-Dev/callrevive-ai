import { motion } from 'framer-motion';
import { useLeadAnalytics } from '../../hooks/useAnalytics';

export default function LeadsPipeline() {
  const { data: leadDist, isLoading } = useLeadAnalytics();

  const segments = leadDist && leadDist.length > 0 ? leadDist.map(item => ({
    label: item.category.charAt(0).toUpperCase() + item.category.slice(1).toLowerCase(),
    count: item.count,
    color: item.category === 'hot' ? 'bg-rose-500' : item.category === 'warm' ? 'bg-amber-500' : 'bg-slate-500',
  })) : [
    { label: 'Hot', count: 0, color: 'bg-rose-500' },
    { label: 'Warm', count: 0, color: 'bg-amber-500' },
    { label: 'Cold', count: 0, color: 'bg-slate-500' },
  ];

  const total = segments.reduce((s, seg) => s + seg.count, 0);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 h-full">
      <h3 className="text-sm font-semibold text-white mb-4">Lead Pipeline</h3>
      {isLoading ? (
        <div className="h-10 flex items-center justify-center text-xs text-white/40 mb-4 animate-pulse">
          Loading pipeline...
        </div>
      ) : total === 0 ? (
        <div className="h-10 bg-white/5 rounded-lg flex items-center justify-center text-xs text-white/40 mb-4">
          No leads in pipeline
        </div>
      ) : (
        <div className="flex rounded-lg overflow-hidden h-10 mb-4">
          {segments.map((seg, i) => {
            const widthPct = total > 0 ? (seg.count / total) * 100 : 0;
            if (widthPct === 0) return null;
            return (
              <motion.div
                key={seg.label}
                initial={{ width: 0 }}
                animate={{ width: `${widthPct}%` }}
                transition={{ delay: 0.3 + i * 0.15, duration: 0.6, ease: 'easeOut' }}
                className={`${seg.color} flex items-center justify-center min-w-[20px]`}
              >
                <span className="text-xs font-bold text-white">{seg.count}</span>
              </motion.div>
            );
          })}
        </div>
      )}
      <div className="flex justify-between mt-3">
        {segments.map((seg) => (
          <div key={seg.label} className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${seg.color}`} />
            <span className="text-xs text-white/60">{seg.label}</span>
          </div>
        ))}
      </div>
      <p className="text-xs text-white/40 mt-4">{total} total leads in pipeline</p>
    </div>
  );
}
