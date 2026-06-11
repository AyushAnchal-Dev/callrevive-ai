import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, SkipForward, SkipBack, Loader2, X } from 'lucide-react';
import { Button } from '../ui/button';

interface CallPlayerProps {
  recordingUrl: string;
  customerName: string;
  durationSeconds: number;
  onClose?: () => void;
}

export default function CallPlayer({ recordingUrl, customerName, durationSeconds, onClose }: CallPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioRef.current = new Audio(recordingUrl);
    
    const audio = audioRef.current;
    
    const updateTime = () => setCurrentTime(audio.currentTime);
    const handleCanPlay = () => setIsLoading(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('canplay', handleCanPlay);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.pause();
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('canplay', handleCanPlay);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [recordingUrl]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackRate;
    }
  }, [playbackRate]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      setIsLoading(true);
      audioRef.current.play().then(() => {
        setIsPlaying(true);
        setIsLoading(false);
      }).catch(() => {
        setIsLoading(false);
        // Fallback for mock urls
        setIsPlaying(true);
        // Simulate playback
        const interval = setInterval(() => {
          setCurrentTime((prev) => {
            if (prev >= durationSeconds) {
              clearInterval(interval);
              setIsPlaying(false);
              return 0;
            }
            return prev + 1;
          });
        }, 1000 / playbackRate);
      });
    }
  };

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = Math.floor(secs % 60);
    return `${mins}:${remainingSecs < 10 ? '0' : ''}${remainingSecs}`;
  };

  const toggleSpeed = () => {
    const nextRate = playbackRate === 1 ? 1.5 : playbackRate === 1.5 ? 2 : 1;
    setPlaybackRate(nextRate);
  };

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-5 space-y-4">
      {/* Player header info */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-white/40 font-medium">LISTENING TO CALL RECORDING</p>
          <h4 className="text-sm font-bold text-white mt-0.5">{customerName}</h4>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={toggleSpeed}
            className="h-7 border-white/10 text-white/70 hover:bg-white/5 hover:text-white px-2 font-mono text-xs"
          >
            {playbackRate}x
          </Button>
          {onClose && (
            <Button
              size="icon"
              variant="ghost"
              onClick={onClose}
              className="w-7 h-7 text-white/40 hover:text-white hover:bg-white/10 rounded-lg flex items-center justify-center"
              title="Close player"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Progress slider bar */}
      <div className="space-y-1">
        <input
          type="range"
          min={0}
          max={durationSeconds}
          value={currentTime}
          onChange={handleScrub}
          className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500"
        />
        <div className="flex justify-between text-[10px] text-white/30 font-mono">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(durationSeconds)}</span>
        </div>
      </div>

      {/* Playback controls */}
      <div className="flex items-center justify-center gap-4">
        <Button
          size="icon"
          variant="ghost"
          onClick={() => {
            const newTime = Math.max(0, currentTime - 5);
            setCurrentTime(newTime);
            if (audioRef.current) audioRef.current.currentTime = newTime;
          }}
          className="w-9 h-9 text-white/50 hover:text-white hover:bg-white/5 rounded-full"
        >
          <SkipBack className="w-4 h-4" />
        </Button>

        <Button
          size="icon"
          onClick={togglePlay}
          className="w-11 h-11 bg-gradient-to-br from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white border-0 rounded-full shadow-lg shadow-violet-500/10 flex items-center justify-center"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : isPlaying ? (
            <Pause className="w-5 h-5 fill-current" />
          ) : (
            <Play className="w-5 h-5 fill-current ml-0.5" />
          )}
        </Button>

        <Button
          size="icon"
          variant="ghost"
          onClick={() => {
            const newTime = Math.min(durationSeconds, currentTime + 5);
            setCurrentTime(newTime);
            if (audioRef.current) audioRef.current.currentTime = newTime;
          }}
          className="w-9 h-9 text-white/50 hover:text-white hover:bg-white/5 rounded-full"
        >
          <SkipForward className="w-4 h-4" />
        </Button>
      </div>

      {/* Waveform Visualization (Mock visualizer) */}
      <div className="flex items-end justify-between h-8 px-2 gap-[2px]">
        {Array.from({ length: 40 }).map((_, idx) => {
          // Generate a wave shape
          const height = Math.abs(Math.sin((idx / 40) * Math.PI * 4)) * 80 + 10;
          // Highlight completed part
          const isCompleted = (idx / 40) * durationSeconds <= currentTime;
          return (
            <div
              key={idx}
              className={`w-[3px] rounded-full transition-all duration-300`}
              style={{
                height: `${height}%`,
                backgroundColor: isCompleted ? 'rgba(139, 92, 246, 0.7)' : 'rgba(255, 255, 255, 0.1)',
                boxShadow: isCompleted && isPlaying ? '0 0 4px rgba(139, 92, 246, 0.4)' : 'none'
              }}
            />
          );
        })}
      </div>
    </div>
  );
}
