import { useState } from 'react';
import { motion } from 'framer-motion';
import { useCalls, useInitiateCallback } from '../hooks/useCalls';
import { callsApi } from '../api/calls';
import CallLog from '../components/calls/CallLog';
import CallPlayer from '../components/calls/CallPlayer';
import { Button } from '../components/ui/button';
import { Loader2 } from 'lucide-react';

const tabs = ['All', 'Missed', 'Answered', 'Callback'];

export default function CallsPage() {
  const [tab, setTab] = useState('All');
  const [page, setPage] = useState(1);
  const [activePlayer, setActivePlayer] = useState<{
    recordingUrl: string;
    customerName: string;
    durationSeconds: number;
  } | null>(null);
  const [loadingRecordingId, setLoadingRecordingId] = useState<string | null>(null);

  const { data: callsResponse, isLoading } = useCalls({
    page,
    limit: 15,
    status: tab,
  });

  const initiateCallbackMutation = useInitiateCallback();

  const calls = callsResponse?.data || [];
  const totalPages = callsResponse?.totalPages || 1;

  const handleCallback = (callId: string) => {
    initiateCallbackMutation.mutate(callId);
  };

  const handlePlayRecording = async (callId: string) => {
    const call = calls.find(c => c.id === callId);
    if (!call) return;
    setLoadingRecordingId(callId);
    try {
      const recording = await callsApi.getCallRecording(callId);
      setActivePlayer({
        recordingUrl: recording.url,
        customerName: call.customerName || 'Customer',
        durationSeconds: recording.duration || call.duration || 30
      });
    } catch (err) {
      console.error("Failed to load call recording:", err);
    } finally {
      setLoadingRecordingId(null);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 relative pb-20">
      <div>
        <h1 className="text-2xl font-bold text-white">Call Log</h1>
        <p className="text-sm text-white/40">All incoming and outgoing calls</p>
      </div>
      <div className="flex gap-2">
        {tabs.map(t => (
          <button
            key={t}
            onClick={() => {
              setTab(t);
              setPage(1);
            }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-white/40 hover:text-white/60 border border-transparent'}`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="relative">
        {isLoading ? (
          <div className="text-center py-12 text-sm text-white/40 animate-pulse">
            Loading call logs...
          </div>
        ) : calls.length === 0 ? (
          <div className="text-center py-12 text-sm text-white/40">
            No calls found in this category.
          </div>
        ) : (
          <CallLog
            calls={calls}
            onPlayRecording={handlePlayRecording}
            onInitiateCallback={handleCallback}
          />
        )}
      </div>

      {/* Pagination Controls */}
      {!isLoading && totalPages > 1 && (
        <div className="flex justify-between items-center px-2">
          <p className="text-xs text-white/40">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={page <= 1}
              onClick={() => setPage(p => Math.max(p - 1, 1))}
              className="text-xs text-white border-white/10"
            >
              Previous
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={page >= totalPages}
              onClick={() => setPage(p => Math.min(p + 1, totalPages))}
              className="text-xs text-white border-white/10"
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Loading Overlay for recordings */}
      {loadingRecordingId && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-zinc-900 border border-white/10 rounded-xl p-6 flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
            <p className="text-sm text-white font-medium">Fetching Call Recording...</p>
          </div>
        </div>
      )}

      {/* Floating Audio Player */}
      {activePlayer && (
        <div className="fixed bottom-6 right-6 w-96 z-50 shadow-2xl animate-in slide-in-from-bottom-5 duration-300">
          <CallPlayer
            recordingUrl={activePlayer.recordingUrl}
            customerName={activePlayer.customerName}
            durationSeconds={activePlayer.durationSeconds}
            onClose={() => setActivePlayer(null)}
          />
        </div>
      )}
    </motion.div>
  );
}
