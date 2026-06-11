import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { PhoneIncoming, PhoneOutgoing, PhoneMissed, Play, RotateCcw } from 'lucide-react';
import type { Call } from '@/types';

interface CallLogProps {
  calls: Call[];
  onPlayRecording?: (callId: string) => void;
  onInitiateCallback?: (callId: string) => void;
}

export default function CallLog({ calls, onPlayRecording, onInitiateCallback }: CallLogProps) {
  const getDirectionIcon = (direction: Call['direction'], status: Call['status']) => {
    if (status === 'missed') return <PhoneMissed className="w-4 h-4 text-rose-400" />;
    return direction === 'inbound' ? (
      <PhoneIncoming className="w-4 h-4 text-emerald-400" />
    ) : (
      <PhoneOutgoing className="w-4 h-4 text-violet-400" />
    );
  };

  const getStatusBadge = (status: Call['status']) => {
    switch (status) {
      case 'missed':
        return <Badge variant="destructive">MISSED</Badge>;
      case 'answered':
        return <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">ANSWERED</Badge>;
      case 'callback':
        return <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20">CALLBACK RINGING</Badge>;
      case 'voicemail':
        return <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20">VOICEMAIL</Badge>;
      default:
        return <Badge variant="outline" className="text-zinc-500 border-zinc-700">FAILED</Badge>;
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds === 0) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const formatTime = (timeStr: string) => {
    if (!timeStr) return '';
    try {
      const date = new Date(timeStr);
      const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
      if (seconds < 60) return 'Just now';
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.floor(hours / 24);
      if (days < 7) return `${days}d ago`;
      return date.toLocaleDateString();
    } catch {
      return timeStr;
    }
  };

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/10 bg-white/[0.02] text-xs text-white/40 uppercase tracking-wider font-semibold">
              <th className="px-5 py-3.5">Direction</th>
              <th className="px-5 py-3.5">Customer</th>
              <th className="px-5 py-3.5">Status</th>
              <th className="px-5 py-3.5">Duration</th>
              <th className="px-5 py-3.5">Time</th>
              <th className="px-5 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-sm">
            {calls.map((call) => (
              <tr key={call.id} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                      {getDirectionIcon(call.direction, call.status)}
                    </div>
                    <span className="text-xs text-white/50 capitalize">{call.direction}</span>
                  </div>
                </td>
                <td className="px-5 py-4">
                  <p className="font-semibold text-white">{call.customerName}</p>
                  <p className="text-xs text-white/40">{call.customerPhone}</p>
                </td>
                <td className="px-5 py-4">{getStatusBadge(call.status)}</td>
                <td className="px-5 py-4 text-white/60 font-mono text-xs">{formatDuration(call.duration)}</td>
                <td className="px-5 py-4 text-white/50 text-xs">{formatTime(call.startTime)}</td>
                <td className="px-5 py-4 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    {call.hasRecording && (
                      <Button
                         size="icon"
                         variant="ghost"
                         onClick={() => onPlayRecording?.(call.id)}
                         className="w-8 h-8 text-white/60 hover:text-white hover:bg-white/10 rounded-lg"
                         title="Listen to recording"
                       >
                         <Play className="w-3.5 h-3.5" />
                       </Button>
                    )}
                    {call.status === 'missed' && (
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => onInitiateCallback?.(call.id)}
                        className="w-8 h-8 text-violet-400 hover:text-violet-300 hover:bg-violet-500/10 rounded-lg"
                        title="Retry Callback"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
