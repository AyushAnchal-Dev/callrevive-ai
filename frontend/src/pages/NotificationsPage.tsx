import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Check, Trash2, ShieldAlert, Calendar, MessageSquare, PhoneMissed, DollarSign, ExternalLink, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { cn } from '../lib/utils';
import { useNotifications, useMarkAsRead, useMarkAllAsRead } from '../hooks/useNotifications';
import { useNavigate } from 'react-router-dom';

const typeConfig: Record<string, { icon: any; bg: string; color: string; route: string }> = {
  hot_lead: { icon: ShieldAlert, bg: 'bg-rose-500/10 border-rose-500/20', color: 'text-rose-400', route: '/leads' },
  missed_call: { icon: PhoneMissed, bg: 'bg-amber-500/10 border-amber-500/20', color: 'text-amber-400', route: '/calls' },
  appointment: { icon: Calendar, bg: 'bg-indigo-500/10 border-indigo-500/20', color: 'text-indigo-400', route: '/appointments' },
  revenue_alert: { icon: DollarSign, bg: 'bg-emerald-500/10 border-emerald-500/20', color: 'text-emerald-400', route: '/analytics' },
  daily_summary: { icon: MessageSquare, bg: 'bg-violet-500/10 border-violet-500/20', color: 'text-violet-400', route: '/analytics' },
  new_lead: { icon: MessageSquare, bg: 'bg-violet-500/10 border-violet-500/20', color: 'text-violet-400', route: '/leads' },
  lead: { icon: ShieldAlert, bg: 'bg-rose-500/10 border-rose-500/20', color: 'text-rose-400', route: '/leads' },
  call: { icon: PhoneMissed, bg: 'bg-amber-500/10 border-amber-500/20', color: 'text-amber-400', route: '/calls' },
  insight: { icon: MessageSquare, bg: 'bg-violet-500/10 border-violet-500/20', color: 'text-violet-400', route: '/ai-insights' },
  system: { icon: Bell, bg: 'bg-white/5 border-white/10', color: 'text-white/50', route: '/dashboard' },
};

const defaultConfig = { icon: Bell, bg: 'bg-white/5 border-white/10', color: 'text-white/50', route: '/dashboard' };

export default function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const { data: notifData, isLoading } = useNotifications({ page: 1, limit: 50 });
  const markAsReadMut = useMarkAsRead();
  const markAllMut = useMarkAllAsRead();
  const navigate = useNavigate();

  // Handle both paginated response and direct array
  const rawData = notifData as any;
  const notifications = rawData?.items || rawData?.data || [];
  const unreadCount = rawData?.unread_count ?? rawData?.unreadCount ?? notifications.filter((n: any) => !n.is_read && !n.read).length;

  const filteredNotifications = notifications.filter((n: any) => {
    const isRead = n.is_read ?? n.read ?? false;
    if (filter === 'unread') return !isRead;
    if (filter === 'read') return isRead;
    return true;
  });

  const formatTime = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs} hr${diffHrs > 1 ? 's' : ''} ago`;
    const diffDays = Math.floor(diffHrs / 24);
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 max-w-4xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white">Notifications</h1>
            {unreadCount > 0 && <Badge className="bg-rose-500 text-white border-0 font-medium">{unreadCount} New</Badge>}
          </div>
          <p className="text-sm text-white/40">Keep track of incoming calls, leads, and analytics updates</p>
        </div>
        {unreadCount > 0 && (
          <Button size="sm" variant="ghost" onClick={() => markAllMut.mutate()} disabled={markAllMut.isPending}
            className="text-xs text-violet-400 hover:text-violet-300 hover:bg-white/5">
            <Check className="w-4 h-4 mr-1.5" /> Mark all as read
          </Button>
        )}
      </div>

      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <div className="flex items-center gap-1">
          {(['all', 'unread', 'read'] as const).map(f => (
            <Button key={f} size="sm" variant={filter === f ? 'secondary' : 'ghost'} onClick={() => setFilter(f)}
              className={cn('text-xs px-3 h-8', filter === f ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white')}>
              {f === 'all' ? 'All' : f === 'unread' ? `Unread (${unreadCount})` : 'Read'}
            </Button>
          ))}
        </div>
        <span className="text-xs text-white/30">Showing {filteredNotifications.length} items</span>
      </div>

      <div className="space-y-3">
        {isLoading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 text-violet-400 animate-spin" /></div>
        ) : (
          <AnimatePresence mode="popLayout">
            {filteredNotifications.length > 0 ? (
              filteredNotifications.map((notif: any) => {
                const isRead = notif.is_read ?? notif.read ?? false;
                const cfg = typeConfig[notif.type] || defaultConfig;
                const Icon = cfg.icon;
                return (
                  <motion.div key={notif.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
                    className={cn(
                      'p-4 rounded-xl border backdrop-blur-xl flex gap-4 items-start group transition-all',
                      isRead ? 'bg-white/[0.02] border-white/5 opacity-70 hover:opacity-100' : 'bg-white/5 border-white/10 hover:border-violet-500/20 shadow-md shadow-violet-950/5'
                    )}>
                    {!isRead && <div className="w-2 h-2 rounded-full bg-violet-400 mt-2 flex-shrink-0 animate-pulse" />}
                    <div className={cn('w-9 h-9 rounded-lg border flex items-center justify-center flex-shrink-0 mt-0.5', cfg.bg)}>
                      <Icon className={cn('w-4 h-4', cfg.color)} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-1">
                        <p className="text-sm font-semibold text-white">{notif.title}</p>
                        <span className="text-[10px] text-white/30 font-medium">{formatTime(notif.created_at || notif.createdAt)}</span>
                      </div>
                      <p className="text-xs text-white/60 mt-1 leading-relaxed">{notif.message}</p>
                      <div className="flex items-center gap-3 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button size="sm" variant="ghost" onClick={() => markAsReadMut.mutate(notif.id)}
                          className="text-[10px] h-6 px-2 text-white/50 hover:text-white hover:bg-white/5">
                          {isRead ? 'Mark Unread' : 'Mark Read'}
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => navigate(cfg.route)}
                          className="text-[10px] h-6 px-2 text-violet-400 hover:text-violet-300 hover:bg-white/5">
                          View Details <ExternalLink className="w-2.5 h-2.5 ml-1" />
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                );
              })
            ) : (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="py-12 text-center rounded-xl border border-white/5 bg-white/[0.01]">
                <Bell className="w-8 h-8 text-white/20 mx-auto mb-3" />
                <p className="text-sm text-white/40">No notifications found</p>
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>
    </motion.div>
  );
}
