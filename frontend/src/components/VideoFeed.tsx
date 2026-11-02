import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, Mic, MicOff, AlertCircle } from 'lucide-react';

interface VideoFeedProps {
  isRecording?: boolean;
  onVolumeChange?: (volume: number) => void;
}

export const VideoFeed: React.FC<VideoFeedProps> = ({ isRecording = false, onVolumeChange }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraEnabled, setCameraEnabled] = useState<boolean>(true);
  const [micEnabled, setMicEnabled] = useState<boolean>(true);
  const [permissionError, setPermissionError] = useState<string | null>(null);
  const [volumeLevel, setVolumeLevel] = useState<number>(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    let activeStream: MediaStream | null = null;

    const startMedia = async () => {
      try {
        setPermissionError(null);
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        activeStream = mediaStream;
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }

        // Setup Audio Analyser for volume level
        try {
          const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
          const audioCtx = new AudioContextClass();
          audioContextRef.current = audioCtx;
          const source = audioCtx.createMediaStreamSource(mediaStream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 64;
          source.connect(analyser);

          const dataArray = new Uint8Array(analyser.frequencyBinCount);
          const updateVolume = () => {
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
              sum += dataArray[i];
            }
            const avg = sum / dataArray.length;
            const normalized = Math.min(100, Math.round((avg / 128) * 100));
            setVolumeLevel(normalized);
            if (onVolumeChange) onVolumeChange(normalized);
            animationFrameRef.current = requestAnimationFrame(updateVolume);
          };
          updateVolume();
        } catch (e) {
          console.warn("Audio analyser not initialized:", e);
        }

      } catch (err) {
        console.warn('Camera/Microphone access error:', err);
        setPermissionError('Camera or microphone access was blocked. You can still participate via text.');
      }
    };

    startMedia();

    return () => {
      if (activeStream) {
        activeStream.getTracks().forEach((track) => track.stop());
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, []);

  const toggleCamera = () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setCameraEnabled(videoTrack.enabled);
      }
    }
  };

  const toggleMic = () => {
    if (stream) {
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setMicEnabled(audioTrack.enabled);
      }
    }
  };

  return (
    <div className="relative rounded-2xl overflow-hidden bg-slate-900 border border-slate-800 shadow-xl aspect-video flex items-center justify-center">
      {/* Video element */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={`w-full h-full object-cover transition-opacity duration-300 ${
          cameraEnabled && !permissionError ? 'opacity-100' : 'opacity-0'
        }`}
      />

      {/* Fallback avatar if camera is off or permission blocked */}
      {(!cameraEnabled || permissionError) && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 p-6 text-center">
          <div className="w-20 h-20 rounded-full bg-slate-800 border-2 border-indigo-500/30 flex items-center justify-center text-slate-400 mb-3">
            <CameraOff className="w-8 h-8" />
          </div>
          <p className="text-sm font-medium text-slate-300">Camera Inactive</p>
          {permissionError && (
            <p className="text-xs text-amber-400/90 mt-1 max-w-xs flex items-center gap-1 justify-center">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              {permissionError}
            </p>
          )}
        </div>
      )}

      {/* Live recording status overlay */}
      {isRecording && (
        <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-950/80 border border-rose-500/40 text-rose-400 text-xs font-semibold backdrop-blur shadow">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          <span>REC</span>
        </div>
      )}

      {/* Mic Audio Level Visualizer */}
      <div className="absolute bottom-4 left-4 right-20 flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800 backdrop-blur">
        <Mic className={`w-3.5 h-3.5 ${micEnabled ? 'text-indigo-400' : 'text-slate-600'}`} />
        <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-75"
            style={{ width: `${micEnabled ? volumeLevel : 0}%` }}
          />
        </div>
      </div>

      {/* Toggle Controls */}
      <div className="absolute bottom-4 right-4 flex items-center gap-2">
        <button
          onClick={toggleCamera}
          className={`p-2 rounded-xl backdrop-blur transition-colors ${
            cameraEnabled
              ? 'bg-slate-800/80 text-slate-200 hover:bg-slate-700'
              : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
          }`}
          title={cameraEnabled ? 'Disable Camera' : 'Enable Camera'}
        >
          {cameraEnabled ? <Camera className="w-4 h-4" /> : <CameraOff className="w-4 h-4" />}
        </button>

        <button
          onClick={toggleMic}
          className={`p-2 rounded-xl backdrop-blur transition-colors ${
            micEnabled
              ? 'bg-slate-800/80 text-slate-200 hover:bg-slate-700'
              : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
          }`}
          title={micEnabled ? 'Mute Microphone' : 'Unmute Microphone'}
        >
          {micEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
};
