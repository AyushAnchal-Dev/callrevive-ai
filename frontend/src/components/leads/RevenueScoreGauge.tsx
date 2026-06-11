import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface RevenueScoreGaugeProps {
  score: number;
  value: string;
  className?: string;
}

export default function RevenueScoreGauge({ score, value, className }: RevenueScoreGaugeProps) {
  const getLabel = (s: number) => {
    if (s >= 80) return { text: 'High Recovery Opportunity', color: 'text-emerald-400' };
    if (s >= 50) return { text: 'Medium Opportunity', color: 'text-amber-400' };
    return { text: 'Low Opportunity', color: 'text-rose-400' };
  };

  const label = getLabel(score);
  
  // Semi-circle SVG settings
  const radius = 50;
  const strokeWidth = 8;
  const circumference = Math.PI * radius; // 180 degrees
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={cn("flex flex-col items-center justify-center p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl", className)}>
      <div className="relative w-36 h-20 overflow-hidden flex items-end justify-center">
        <svg className="w-full h-full absolute top-0 left-0" viewBox="0 0 120 70">
          {/* Base Track Arc */}
          <path
            d="M 10,60 A 50,50 0 0,1 110,60"
            fill="none"
            className="stroke-white/10"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          {/* Active Progress Arc */}
          <motion.path
            d="M 10,60 A 50,50 0 0,1 110,60"
            fill="none"
            className="stroke-violet-500"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: strokeDashoffset }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>
        <div className="text-center z-10 translate-y-[-5px]">
          <span className="text-2xl font-black text-white">{score}%</span>
          <p className="text-[10px] text-white/40 font-medium">RECOVERY PROBABILITY</p>
        </div>
      </div>
      <div className="text-center mt-3 space-y-1">
        <p className="text-lg font-bold text-white">{value}</p>
        <p className={cn("text-xs font-semibold", label.color)}>{label.text}</p>
      </div>
    </div>
  );
}
