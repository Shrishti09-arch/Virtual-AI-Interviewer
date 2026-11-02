import { useState, useRef, useCallback } from 'react';

export interface UseMediaRecorderOptions {
  mimeType?: string;
  onDataAvailable?: (chunk: Blob) => void;
  onStop?: (blobUrl: string, blob: Blob) => void;
}

export const useMediaRecorder = (options: UseMediaRecorderOptions = {}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const start = useCallback((stream: MediaStream) => {
    chunksRef.current = [];
    const mime = options.mimeType || 'video/webm';
    const recorder = new MediaRecorder(stream, { mimeType: mime });

    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        chunksRef.current.push(e.data);
        options.onDataAvailable?.(e.data);
      }
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: mime });
      const url = URL.createObjectURL(blob);
      setRecordedUrl(url);
      options.onStop?.(url, blob);
      setIsRecording(false);
      setIsPaused(false);
    };

    recorder.start(1000);
    mediaRecorderRef.current = recorder;
    setIsRecording(true);
    setIsPaused(false);
  }, [options]);

  const pause = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
    }
  }, [isRecording, isPaused]);

  const resume = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
    }
  }, [isRecording, isPaused]);

  const stop = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  }, [isRecording]);

  const clear = useCallback(() => {
    if (recordedUrl) {
      URL.revokeObjectURL(recordedUrl);
      setRecordedUrl(null);
    }
    chunksRef.current = [];
  }, [recordedUrl]);

  return {
    isRecording,
    isPaused,
    recordedUrl,
    start,
    pause,
    resume,
    stop,
    clear,
  };
};
