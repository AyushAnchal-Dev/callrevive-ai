import { MessageSquare, Calendar, Globe, AlertTriangle, ArrowRight } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

interface Message {
  role: 'ai' | 'customer';
  content: string;
  ts: string;
}

interface Conversation {
  id: string;
  customerName: string;
  channel: 'voice' | 'whatsapp' | 'sms';
  status: 'active' | 'completed' | 'failed';
  language: string;
  aiSummary?: string;
  startedAt: string;
  messages: Message[];
  intent?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
}

interface ConversationViewProps {
  conversation: Conversation;
}

export default function ConversationView({ conversation }: ConversationViewProps) {
  const getChannelBadge = (ch: Conversation['channel']) => {
    switch (ch) {
      case 'voice':
        return <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20">VOICE AI</Badge>;
      case 'whatsapp':
        return <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">WHATSAPP</Badge>;
      case 'sms':
      default:
        return <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20">SMS</Badge>;
    }
  };

  const getSentimentColor = (s?: Conversation['sentiment']) => {
    switch (s) {
      case 'positive': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'negative': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'neutral':
      default:
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  };

  return (
    <div className="flex flex-col h-full rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl overflow-hidden">
      {/* Session Metadata Header */}
      <div className="p-5 border-b border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white/[0.01]">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white">{conversation.customerName}</h3>
            {getChannelBadge(conversation.channel)}
          </div>
          <div className="flex items-center gap-3 text-xs text-white/40 mt-1">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {conversation.startedAt}
            </span>
            <span className="flex items-center gap-1">
              <Globe className="w-3.5 h-3.5" />
              {conversation.language.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Dynamic AI Badges */}
        <div className="flex items-center gap-2">
          {conversation.intent && (
            <Badge variant="outline" className="border-white/10 text-white/60 text-[10px] capitalize">
              Intent: {conversation.intent}
            </Badge>
          )}
          {conversation.sentiment && (
            <Badge variant="outline" className={getSentimentColor(conversation.sentiment)}>
              Sentiment: {conversation.sentiment.toUpperCase()}
            </Badge>
          )}
        </div>
      </div>

      {/* AI summary banner if available */}
      {conversation.aiSummary && (
        <div className="p-4 bg-violet-500/5 border-b border-violet-500/10 flex items-start gap-2.5">
          <MessageSquare className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-[10px] font-bold text-violet-300 tracking-wider uppercase">AI Generated Summary</span>
            <p className="text-xs text-white/70 leading-relaxed mt-0.5">{conversation.aiSummary}</p>
          </div>
        </div>
      )}

      {/* Transcript bubbles list */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 max-h-[400px]">
        {conversation.messages.map((m, idx) => {
          const isAI = m.role === 'ai';
          return (
            <div key={idx} className={`flex ${isAI ? 'justify-end' : 'justify-start'}`}>
              <div className="space-y-1 max-w-[80%]">
                <div
                  className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                    isAI
                      ? 'bg-violet-500/10 border border-violet-500/20 text-white/90 rounded-br-sm'
                      : 'bg-white/10 border border-white/5 text-white/80 rounded-bl-sm'
                  }`}
                >
                  <p>{m.content}</p>
                </div>
                <p className={`text-[10px] text-white/30 ${isAI ? 'text-right' : 'text-left'}`}>
                  {isAI ? 'AI Agent' : 'Customer'} · {m.ts}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
