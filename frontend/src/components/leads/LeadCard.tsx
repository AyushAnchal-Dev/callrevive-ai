import { motion } from 'framer-motion';
import { Phone, MessageSquare, AlertTriangle, Calendar, IndianRupee } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import LeadScoreBadge from './LeadScoreBadge';

interface LeadCardProps {
  lead: {
    id: string;
    name: string;
    phone: string;
    service: string;
    score: number;
    category: 'hot' | 'warm' | 'cold';
    revenue: string;
    urgency: 'High' | 'Medium' | 'Low';
    status: string;
  };
  onAction?: (action: 'call' | 'whatsapp' | 'view', leadId: string) => void;
}

export default function LeadCard({ lead, onAction }: LeadCardProps) {
  const getUrgencyColor = (urg: string) => {
    switch (urg.toLowerCase()) {
      case 'high': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'medium': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'low':
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    }
  };

  const getCategoryColor = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'hot': return 'bg-rose-500 text-white border-0';
      case 'warm': return 'bg-violet-500 text-white border-0';
      case 'cold':
      default:
        return 'bg-zinc-800 text-zinc-400 border-white/10';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      className="p-5 rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl hover:border-violet-500/30 transition-all flex flex-col justify-between"
    >
      <div>
        {/* Header containing name and score badge */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h4 className="text-base font-bold text-white leading-snug">{lead.name}</h4>
            <p className="text-xs text-white/40">{lead.phone}</p>
          </div>
          <LeadScoreBadge score={lead.score} size="sm" />
        </div>

        {/* Lead Category and Urgency */}
        <div className="flex gap-2 mb-4">
          <Badge className={getCategoryColor(lead.category)}>
            {lead.category.toUpperCase()}
          </Badge>
          <Badge variant="outline" className={getUrgencyColor(lead.urgency)}>
            {lead.urgency} Urgency
          </Badge>
        </div>

        {/* Info Rows */}
        <div className="space-y-2.5 text-xs mb-5">
          <div className="flex items-center justify-between">
            <span className="text-white/30">Service Requested</span>
            <span className="text-white font-medium">{lead.service}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white/30">Est. Opportunity</span>
            <span className="text-emerald-400 font-bold flex items-center">
              {lead.revenue}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white/30">Action Status</span>
            <span className="text-white/70 capitalize px-2 py-0.5 rounded bg-white/5 border border-white/5">
              {lead.status}
            </span>
          </div>
        </div>
      </div>

      {/* Action CTA Buttons */}
      <div className="grid grid-cols-2 gap-2 pt-3 border-t border-white/5">
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction?.('whatsapp', lead.id)}
          className="border-white/10 text-white/80 hover:bg-white/5 hover:text-white"
        >
          <MessageSquare className="w-3.5 h-3.5 mr-1 text-emerald-400" />
          WhatsApp
        </Button>
        <Button
          size="sm"
          onClick={() => onAction?.('call', lead.id)}
          className="bg-violet-600 hover:bg-violet-500 text-white border-0"
        >
          <Phone className="w-3.5 h-3.5 mr-1" />
          Call Owner
        </Button>
      </div>
    </motion.div>
  );
}
