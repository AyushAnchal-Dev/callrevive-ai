import { cn } from '@/lib/utils';

interface LeadScoreBadgeProps {
  score: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function LeadScoreBadge({ score, className, size = 'md' }: LeadScoreBadgeProps) {
  const getColors = (val: number) => {
    if (val >= 80) return { text: 'text-emerald-400', stroke: 'stroke-emerald-500', bg: 'bg-emerald-500/10' };
    if (val >= 50) return { text: 'text-amber-400', stroke: 'stroke-amber-500', bg: 'bg-amber-500/10' };
    return { text: 'text-rose-400', stroke: 'stroke-rose-500', bg: 'bg-rose-500/10' };
  };

  const colors = getColors(score);
  
  const sizeClasses = {
    sm: 'w-8 h-8 text-[10px]',
    md: 'w-12 h-12 text-xs',
    lg: 'w-16 h-16 text-sm',
  };

  // SVG parameters
  const radius = 18;
  const strokeWidth = 3.5;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={cn("relative flex items-center justify-center rounded-full font-bold", colors.bg, sizeClasses[size], className)}>
      <svg className="w-full h-full transform -rotate-90">
        {/* Track circle */}
        <circle
          cx="50%"
          cy="50%"
          r={radius}
          className="stroke-white/10 fill-none"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx="50%"
          cy="50%"
          r={radius}
          className={cn("fill-none transition-all duration-500 ease-out", colors.stroke)}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
        />
      </svg>
      <span className={cn("absolute inset-0 flex items-center justify-center", colors.text)}>
        {score}
      </span>
    </div>
  );
}
