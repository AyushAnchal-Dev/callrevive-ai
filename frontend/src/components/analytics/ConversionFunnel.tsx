import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { useConversionFunnel } from '../../hooks/useAnalytics';

export default function ConversionFunnel() {
  const { data: funnelData, isLoading } = useConversionFunnel();

  const stages = funnelData && funnelData.length > 0 ? funnelData.map((s: any) => ({
    label: s.stage,
    count: s.count,
    pct: s.percentage,
    color: s.stage === 'Missed Calls' ? 'bg-violet-500' : s.stage === 'Contacted' ? 'bg-indigo-500' : s.stage === 'Qualified' ? 'bg-blue-500' : 'bg-emerald-500',
  })) : [];

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
      <h3 className="text-sm font-semibold text-white mb-6">Conversion Funnel</h3>
      {isLoading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 text-violet-400 animate-spin" /></div>
      ) : stages.length === 0 ? (
        <div className="py-12 text-center text-xs text-white/40">No funnel data available</div>
      ) : (
        <div className="space-y-4">
          {stages.map((stage: any, i: number) => (
            <div key={stage.label}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-white/60">{stage.label}</span>
                <span className="text-white font-medium">{stage.count} ({stage.pct}%)</span>
              </div>
              <div className="w-full bg-white/5 rounded-full h-6 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.max(stage.pct, 2)}%` }}
                  transition={{ delay: 0.3 + i * 0.15, duration: 0.7, ease: 'easeOut' }}
                  className={`${stage.color} h-full rounded-full flex items-center justify-center`}>
                  {stage.pct > 15 && <span className="text-[10px] font-bold text-white">{stage.pct}%</span>}
                </motion.div>
              </div>
              {i < stages.length - 1 && (
                <p className="text-[10px] text-white/30 mt-1 text-right">
                  Drop-off: {stages[i].count - stages[i + 1].count} ({Math.round(((stages[i].count - stages[i + 1].count) / Math.max(stages[i].count, 1)) * 100)}%)
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
