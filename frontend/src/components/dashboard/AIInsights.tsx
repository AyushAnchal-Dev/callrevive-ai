import { motion } from 'framer-motion';
import { Brain, AlertTriangle, TrendingUp, Clock, Sparkles } from 'lucide-react';
import { Button } from '../ui/button';
import { useHotLeads } from '../../hooks/useLeads';
import { useOverview } from '../../hooks/useAnalytics';
import { useNavigate } from 'react-router-dom';

export default function AIInsights() {
  const { data: hotLeads, isLoading: loadingLeads } = useHotLeads();
  const { data: overview, isLoading: loadingOverview } = useOverview();
  const navigate = useNavigate();

  const insights = [];

  // Insight 1: Hot Leads
  if (hotLeads && hotLeads.length > 0) {
    const names = hotLeads.slice(0, 3).map(l => l.customerName).join(', ');
    const potentialRevenue = hotLeads.reduce((acc, l) => acc + l.revenueEstimate, 0);
    insights.push({
      icon: AlertTriangle,
      color: 'text-rose-400 bg-rose-500/10',
      title: `${hotLeads.length} hot lead${hotLeads.length > 1 ? 's' : ''} uncontacted`,
      desc: `${names} ${hotLeads.length > 3 ? 'and others' : ''} have active inquiries. Call them to secure ₹${potentialRevenue.toLocaleString('en-IN')} in recovered sales.`,
      action: 'View Hot Leads',
      href: '/leads'
    });
  } else {
    insights.push({
      icon: Brain,
      color: 'text-violet-400 bg-violet-500/10',
      title: 'Inbox is fully caught up',
      desc: 'All recent inbound missed calls and lead inquiries have been successfully followed up. Good job!',
      action: 'Configure Automations',
      href: '/settings'
    });
  }

  // Insight 2: Recovery Performance
  const recoveryRate = overview?.recoveryRate || 0;
  if (recoveryRate > 0) {
    insights.push({
      icon: TrendingUp,
      color: 'text-emerald-400 bg-emerald-500/10',
      title: `Recovery Rate: ${recoveryRate}%`,
      desc: `Your automated voice callback assistant recovered ₹${(overview?.revenueRecovered || 0).toLocaleString('en-IN')} this month. Keep it up!`,
      action: 'View Analytics',
      href: '/analytics'
    });
  } else {
    insights.push({
      icon: TrendingUp,
      color: 'text-emerald-400 bg-emerald-500/10',
      title: 'AC Service Recovery Opportunity',
      desc: 'AC maintenance requests are starting to surge this week. Set up an outbound promo campaign.',
      action: 'View Trends',
      href: '/analytics'
    });
  }

  // Insight 3: Appointments/Conversations Reminder
  const activeConversations = overview?.appointmentsToday || 0;
  if (activeConversations > 0) {
    insights.push({
      icon: Clock,
      color: 'text-amber-400 bg-amber-500/10',
      title: `${activeConversations} active chat${activeConversations > 1 ? 's' : ''}`,
      desc: `You have ${activeConversations} active customer conversation sessions in progress. Check the transcripts.`,
      action: 'View Chats',
      href: '/conversations'
    });
  } else {
    insights.push({
      icon: Clock,
      color: 'text-amber-400 bg-amber-500/10',
      title: 'Contact reminders are active',
      desc: 'Schedule appointment confirmations and automated follow-ups via WhatsApp to boost booking rates by 15%.',
      action: 'Manage Reminders',
      href: '/appointments'
    });
  }

  const isLoading = loadingLeads || loadingOverview;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center">
          <Brain className="w-4 h-4 text-white" />
        </div>
        <h3 className="text-sm font-semibold text-white">AI Insights</h3>
        <Sparkles className="w-3 h-3 text-violet-400 animate-pulse" />
      </div>
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-8 text-xs text-white/40 animate-pulse">
            Loading business insights...
          </div>
        ) : (
          insights.map((insight, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.2 }}
              className="flex gap-3 p-3 rounded-lg border border-white/5 hover:border-white/10 transition-all group"
            >
              <div className={`w-8 h-8 rounded-lg ${insight.color} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                <insight.icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white">{insight.title}</p>
                <p className="text-xs text-white/40 mt-1 leading-relaxed">{insight.desc}</p>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => { navigate(insight.href); }}
                  className="text-xs text-violet-400 hover:text-violet-300 px-0 mt-1 h-6 hover:bg-transparent"
                >
                  {insight.action} →
                </Button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
