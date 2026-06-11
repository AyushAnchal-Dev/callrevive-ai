import { Phone, PhoneMissed, PhoneForwarded } from 'lucide-react';
import { Badge } from '../ui/badge';
import { useCalls } from '../../hooks/useCalls';
import { Link, useNavigate } from 'react-router-dom';

const statusConfig: Record<string, { icon: any; color: string; badge: string }> = {
  missed: { icon: PhoneMissed, color: 'text-rose-400', badge: 'destructive' },
  answered: { icon: Phone, color: 'text-emerald-400', badge: 'default' },
  callback: { icon: PhoneForwarded, color: 'text-blue-400', badge: 'secondary' },
};

const formatRelativeTime = (isoString: string) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  const diffHrs = Math.floor(diffMins / 60);
  if (diffHrs < 24) return `${diffHrs} hr${diffHrs > 1 ? 's' : ''} ago`;
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
};

const formatDuration = (secs: number) => {
  if (!secs) return '0s';
  const mins = Math.floor(secs / 60);
  const remainSecs = secs % 60;
  if (mins === 0) return `${remainSecs}s`;
  return `${mins}m ${remainSecs}s`;
};

export default function RecentCalls() {
  const { data: callsResponse, isLoading } = useCalls({ page: 1, limit: 5 });
  const calls = callsResponse?.data || [];
  const navigate = useNavigate();

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-white">Recent Calls</h3>
        <Link to="/calls" className="text-xs text-violet-400 hover:text-violet-300 transition-colors" aria-label="View all recent calls">
          View all recent calls →
        </Link>
      </div>
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-4 text-xs text-white/40 animate-pulse">
            Loading recent calls...
          </div>
        ) : calls.length === 0 ? (
          <div className="text-center py-4 text-xs text-white/40">
            No recent calls logged.
          </div>
        ) : (
          calls.map((call) => {
            const cfg = statusConfig[call.status] || statusConfig.missed;
            const Icon = cfg.icon;
            return (
              <div key={call.id} onClick={() => navigate('/calls')} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0 hover:bg-white/5 rounded-lg px-2 -mx-2 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center ${cfg.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{call.customerName}</p>
                    <p className="text-xs text-white/40">{call.customerPhone}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant={cfg.badge as any} className="text-[10px] mb-1">{call.status}</Badge>
                  <p className="text-[10px] text-white/30">{formatRelativeTime(call.startTime)} · {formatDuration(call.duration)}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
