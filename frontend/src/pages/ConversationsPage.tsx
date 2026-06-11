import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Phone, MessageSquareMore, Calendar, HeartPulse } from 'lucide-react';
import { useConversations, useConversation } from '../hooks/useConversations';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';

const formatMsgTime = (isoString: string) => {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return isoString;
  }
};

const formatTimeAgo = (isoString: string) => {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    const diffDays = Math.floor(diffHrs / 24);
    if (diffDays === 1) return 'Yesterday';
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  } catch (e) {
    return isoString;
  }
};

const ChannelIcon = ({ channel }: { channel: string }) => {
  if (channel === 'voice') return <Phone className="w-3.5 h-3.5 text-violet-400" />;
  if (channel === 'whatsapp') return <MessageSquareMore className="w-3.5 h-3.5 text-emerald-400" />;
  return <MessageSquare className="w-3.5 h-3.5 text-blue-400" />;
};

export default function ConversationsPage() {
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: conversationsResponse, isLoading: listLoading } = useConversations({
    page,
    limit: 15,
  });

  const { data: selectedConv, isLoading: detailLoading } = useConversation(selectedId || '');

  const conversations = conversationsResponse?.data || [];
  const totalPages = conversationsResponse?.totalPages || 1;

  // Select first conversation by default once loaded
  useEffect(() => {
    if (conversations.length > 0 && !selectedId) {
      setSelectedId(conversations[0].id);
    }
  }, [conversations, selectedId]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Conversations</h1>
        <p className="text-sm text-white/40">AI conversation transcripts and transcripts history</p>
      </div>

      {listLoading ? (
        <div className="text-center py-12 text-sm text-white/40 animate-pulse">
          Loading conversations...
        </div>
      ) : conversations.length === 0 ? (
        <div className="text-center py-12 text-sm text-white/40 bg-white/5 rounded-xl border border-white/10">
          No conversations found.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Conversations List Panel */}
          <div className="space-y-3">
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {conversations.map(c => (
                <div
                  key={c.id}
                  onClick={() => setSelectedId(c.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    selectedId === c.id
                      ? 'border-violet-500/40 bg-violet-500/10'
                      : 'border-white/10 bg-white/5 hover:border-white/20'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <ChannelIcon channel={c.channel || 'voice'} />
                      <p className="text-sm font-medium text-white truncate">{c.customerName}</p>
                    </div>
                    <span className="text-[10px] text-white/30 shrink-0">{formatTimeAgo(c.createdAt)}</span>
                  </div>
                  {c.summary && (
                    <p className="text-xs text-white/40 mt-2 line-clamp-2 italic">
                      "{c.summary}"
                    </p>
                  )}
                  <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-white/5">
                    <span className="text-[10px] text-violet-400 capitalize">via {c.channel}</span>
                    {c.duration > 0 && (
                      <span className="text-[10px] text-white/30">
                        {c.duration}s duration
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* List Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-between items-center px-1 pt-2">
                <p className="text-[10px] text-white/30">Page {page} of {totalPages}</p>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page <= 1}
                    onClick={() => setPage(p => Math.max(p - 1, 1))}
                    className="h-7 px-2.5 text-[10px] text-white border-white/10"
                  >
                    Prev
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page >= totalPages}
                    onClick={() => setPage(p => Math.min(p + 1, totalPages))}
                    className="h-7 px-2.5 text-[10px] text-white border-white/10"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Transcript Details Panel */}
          <div className="lg:col-span-2 rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 flex flex-col min-h-[450px]">
            {detailLoading ? (
              <div className="flex-1 flex items-center justify-center text-sm text-white/40 animate-pulse">
                Loading transcript...
              </div>
            ) : selectedConv ? (
              <>
                {/* Header info */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-4 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-violet-400" />
                    <div>
                      <h3 className="text-base font-semibold text-white">{selectedConv.customerName}</h3>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-white/40 capitalize">Channel: {selectedConv.channel}</span>
                        <span className="text-white/20">•</span>
                        <span className="text-xs text-white/40">{formatTimeAgo(selectedConv.createdAt)}</span>
                      </div>
                    </div>
                  </div>
                  {selectedConv.summary && (
                    <div className="md:max-w-md bg-white/5 rounded-lg p-3 border border-white/5 text-xs text-white/60">
                      <p className="font-semibold text-[10px] text-violet-400 uppercase tracking-wider mb-1">AI Summary</p>
                      <p className="italic">"{selectedConv.summary}"</p>
                    </div>
                  )}
                </div>

                {/* Messages Transcript */}
                <div className="flex-1 space-y-4 max-h-[450px] overflow-y-auto pr-2 pb-4">
                  {selectedConv.messages.length === 0 ? (
                    <div className="text-center py-12 text-sm text-white/30 italic">
                      No message exchange recorded in this conversation.
                    </div>
                  ) : (
                    selectedConv.messages.map((m, i) => (
                      <div key={m.id || i} className={`flex ${m.role === 'ai' ? 'justify-end' : 'justify-start'}`}>
                        <div
                          className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm ${
                            m.role === 'ai'
                              ? 'bg-violet-500/20 text-white/95 border border-violet-500/20 rounded-br-sm'
                              : 'bg-white/10 text-white/90 border border-white/5 rounded-bl-sm'
                          }`}
                        >
                          <p className="whitespace-pre-wrap">{m.content}</p>
                          <div className="flex items-center justify-end gap-1.5 mt-1">
                            <p className="text-[9px] text-white/30">{formatMsgTime(m.timestamp)}</p>
                            {m.sentiment && (
                              <Badge variant="outline" className={`text-[8px] px-1 py-0 ${
                                m.sentiment === 'positive' ? 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5' :
                                m.sentiment === 'negative' ? 'text-rose-400 border-rose-500/20 bg-rose-500/5' : 'text-white/30 border-white/5'
                              }`}>
                                {m.sentiment}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-sm text-white/30 italic">
                Select a conversation from the list to view its transcript.
              </div>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}

