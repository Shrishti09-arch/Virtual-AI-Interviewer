import React, { useState, useEffect, useRef } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ConfirmationModal } from '../components/ConfirmationModal';
import {
  Video,
  VideoOff,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Square,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  Award,
  Sparkles,
  ArrowRight,
  Send,
  Clock,
  MessageSquare,
  Bot,
  Zap,
  Download,
  Trash2,
  Eye,
  Info,
  ShieldCheck,
  Building,
  TrendingUp,
  FileText,
  Sliders,
  Check,
  X,
} from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';

const SUPPORTED_ROLES = [
  'Software Development Engineer',
  'AI/ML Engineer',
  'Data Scientist',
  'Data Analyst',
  'Python Developer',
  'Java Developer',
  'Full Stack Developer',
  'Backend Developer',
  'Frontend Developer',
  'Cybersecurity Engineer',
  'Cloud Engineer',
  'DevOps Engineer',
];

const INTERVIEW_TYPES = [
  'Technical',
  'HR',
  'Behavioral',
  'Managerial',
  'AI/ML',
  'Coding',
  'Company-specific',
];

const TARGET_COMPANIES = [
  'Amazon',
  'Google',
  'Meta',
  'Microsoft',
  'Apple',
  'Netflix',
  'Uber',
  'High-Growth Startup',
];

const EXPERIENCE_LEVELS = ['Student/Fresher', '1-3 years', '4-7 years', '8+ years'];

const ALL_SUBJECTS = [
  'Data Structures and Algorithms',
  'System Design',
  'Databases & Concurrency',
  'Distributed Systems',
  'Operating Systems',
  'Computer Networks',
  'Object-Oriented Design',
  'Machine Learning & RAG',
  'Cloud Architecture & DevOps',
];

interface Question {
  id: number;
  question_order: number;
  category: string;
  question_text: string;
  is_follow_up?: boolean;
  difficulty_level?: string;
  candidate_answer?: string;
  time_spent_seconds?: number;
  score?: number;
  score_out_of_10?: number;
  technical_accuracy?: number;
  completeness?: number;
  problem_solving_rating?: number;
  feedback?: string;
  correct_points?: string[];
  incorrect_points?: string[];
  missing_concepts?: string[];
  model_answer?: string;
  ideal_answer?: string;
  improvement_suggestions?: string;
  filler_words?: Record<string, number>;
  total_fillers?: number;
  repeated_words?: string[];
  pauses_count?: number;
  wpm?: number;
  vocabulary_score?: number;
  star_analysis?: Record<string, { detected: boolean; label: string }>;
  is_fallback?: boolean;
  provider_used?: string;
  model_used?: string;
}

interface InterviewSession {
  id: number;
  role_title: string;
  experience_level: string;
  interview_type: string;
  difficulty: string;
  technical_subjects: string[];
  interview_duration_mins: number;
  target_company?: string;
  status: string;
  total_questions: number;
  current_question_index: number;
  duration_seconds: number;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  behavioral_score: number;
  answer_quality_score: number;
  problem_solving_score: number;
  verdict: string;
  overall_summary: string;
  key_strengths: string[];
  areas_to_improve: string[];
  recommended_topics: string[];
  improvement_plan: string[];
  full_transcript?: string;
  assessment_disclaimer?: string;
  total_filler_words: number;
  average_wpm: number;
  clarity_rating: string;
  questions: Question[];
}

export const MockInterviewPage: React.FC = () => {
  const { user } = useAuth();
  const toast = useToast();

  // Navigation Stages: 'setup' | 'active' | 'completed'
  const [stage, setStage] = useState<'setup' | 'active' | 'completed'>('setup');

  // Setup Configuration State
  const [roleTitle, setRoleTitle] = useState<string>(user?.role_target || 'Software Development Engineer');
  const [interviewType, setInterviewType] = useState<string>('Technical');
  const [experienceLevel, setExperienceLevel] = useState<string>('1-3 years');
  const [difficulty, setDifficulty] = useState<string>('Intermediate');
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([
    'Data Structures and Algorithms',
    'System Design',
  ]);
  const [targetCompany, setTargetCompany] = useState<string>('Amazon');
  const [totalQuestions, setTotalQuestions] = useState<number>(3);
  const [isStarting, setIsStarting] = useState<boolean>(false);

  // Active Session State
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState<number>(0);
  const [candidateAnswer, setCandidateAnswer] = useState<string>('');
  const [questionTimer, setQuestionTimer] = useState<number>(0);
  const [pausesCount, setPausesCount] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [stepEvaluation, setStepEvaluation] = useState<Question | null>(null);
  const [showEndEarlyModal, setShowEndEarlyModal] = useState<boolean>(false);

  // Audio / Video Recording State (MediaRecorder)
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const [cameraEnabled, setCameraEnabled] = useState<boolean>(true);
  const [micEnabled, setMicEnabled] = useState<boolean>(true);
  const [volumeLevel, setVolumeLevel] = useState<number>(0);
  const [recordingStatus, setRecordingStatus] = useState<'idle' | 'recording' | 'paused' | 'stopped'>('idle');
  const [recordedVideoUrl, setRecordedVideoUrl] = useState<string | null>(null);
  const [showPlaybackModal, setShowPlaybackModal] = useState<boolean>(false);

  // Speech Recognition & TTS State
  const [isSpeechRecognitionActive, setIsSpeechRecognitionActive] = useState<boolean>(false);
  const [aiVoiceMuted, setAiVoiceMuted] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);

  // PDF Download State
  const [isDownloadingPdf, setIsDownloadingPdf] = useState<boolean>(false);

  // Timer interval for question
  useEffect(() => {
    let interval: any = null;
    if (stage === 'active' && !stepEvaluation) {
      interval = setInterval(() => {
        setQuestionTimer((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [stage, stepEvaluation, currentQuestionIdx]);

  // Setup Web Audio Level Meter
  useEffect(() => {
    if (stage !== 'active') return;

    let audioCtx: AudioContext | null = null;
    let animId: number | null = null;

    const initMedia = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        mediaStreamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        // AudioContext Level Analyser
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioCtx) {
          audioCtx = new AudioCtx();
          const source = audioCtx.createMediaStreamSource(stream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 64;
          source.connect(analyser);

          const data = new Uint8Array(analyser.frequencyBinCount);
          const checkVolume = () => {
            analyser.getByteFrequencyData(data);
            let sum = 0;
            for (let i = 0; i < data.length; i++) sum += data[i];
            const avg = sum / data.length;
            const norm = Math.min(100, Math.round((avg / 128) * 100));
            setVolumeLevel(norm);
            animId = requestAnimationFrame(checkVolume);
          };
          checkVolume();
        }
      } catch (err) {
        console.warn('Camera / Microphone access denied or not present:', err);
      }
    };

    initMedia();

    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (animId) cancelAnimationFrame(animId);
      if (audioCtx) audioCtx.close().catch(() => {});
    };
  }, [stage]);

  // TTS: AI Interviewer speaks question
  const speakQuestion = (text: string) => {
    if (aiVoiceMuted || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  // Start Interactive Interview Session
  const handleStartInterview = async () => {
    setIsStarting(true);
    try {
      const res = await apiClient.post('/interviews/start', {
        role_title: roleTitle,
        interview_type: interviewType,
        experience_level: experienceLevel,
        difficulty: difficulty,
        technical_subjects: selectedSubjects,
        interview_duration_mins: totalQuestions === 3 ? 10 : totalQuestions === 5 ? 15 : 25,
        target_company: interviewType === 'Company-specific' ? targetCompany : undefined,
        total_questions: totalQuestions,
      });

      setSession(res.data);
      setCurrentQuestionIdx(0);
      setCandidateAnswer('');
      setQuestionTimer(0);
      setPausesCount(0);
      setStepEvaluation(null);
      setRecordingStatus('idle');
      setRecordedVideoUrl(null);
      setStage('active');

      toast.success('Interview session started! Listen to the interviewer.');
      if (res.data.questions && res.data.questions.length > 0) {
        speakQuestion(res.data.questions[0].question_text);
      }
    } catch (err) {
      console.error('Failed to start interview:', err);
      toast.error('Error launching interview. Please verify backend connectivity.');
    } finally {
      setIsStarting(false);
    }
  };

  // Toggle Camera
  const handleToggleCamera = () => {
    if (mediaStreamRef.current) {
      const videoTrack = mediaStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setCameraEnabled(videoTrack.enabled);
        toast.info(videoTrack.enabled ? 'Webcam enabled' : 'Webcam disabled');
      }
    }
  };

  // Toggle Mic
  const handleToggleMic = () => {
    if (mediaStreamRef.current) {
      const audioTrack = mediaStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setMicEnabled(audioTrack.enabled);
        toast.info(audioTrack.enabled ? 'Microphone enabled' : 'Microphone muted');
      }
    }
  };

  // MediaRecorder: Start Recording
  const handleStartRecording = () => {
    if (!mediaStreamRef.current) {
      toast.warning('Microphone and camera stream not available.');
      return;
    }

    recordedChunksRef.current = [];
    let options: any = { mimeType: 'video/webm;codecs=vp9,opus' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      options = { mimeType: 'video/webm' };
    }

    try {
      const recorder = new MediaRecorder(mediaStreamRef.current, options);
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };
      recorder.onstop = () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        setRecordedVideoUrl(url);
      };
      recorder.start(1000);
      mediaRecorderRef.current = recorder;
      setRecordingStatus('recording');
      toast.info('Recording started...');

      // Start Web Speech API transcription
      startSpeechRecognition();
    } catch (err) {
      console.error('Error starting MediaRecorder:', err);
      toast.error('MediaRecorder could not start on this browser format.');
    }
  };

  // MediaRecorder: Pause Recording
  const handlePauseRecording = () => {
    if (mediaRecorderRef.current && recordingStatus === 'recording') {
      mediaRecorderRef.current.pause();
      setRecordingStatus('paused');
      setPausesCount((p) => p + 1);
    }
  };

  // MediaRecorder: Resume Recording
  const handleResumeRecording = () => {
    if (mediaRecorderRef.current && recordingStatus === 'paused') {
      mediaRecorderRef.current.resume();
      setRecordingStatus('recording');
    }
  };

  // MediaRecorder: Stop Recording
  const handleStopRecording = () => {
    if (mediaRecorderRef.current && recordingStatus !== 'idle' && recordingStatus !== 'stopped') {
      mediaRecorderRef.current.stop();
      setRecordingStatus('stopped');
      stopSpeechRecognition();
    }
  };

  // Save Recorded Video Locally
  const handleSaveRecordingLocally = () => {
    if (!recordedVideoUrl || !session) return;
    const a = document.createElement('a');
    a.href = recordedVideoUrl;
    a.download = `MockInterview_Session_${session.id}_Q${currentQuestionIdx + 1}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Delete Recording
  const handleDeleteRecording = () => {
    if (recordedVideoUrl) {
      URL.revokeObjectURL(recordedVideoUrl);
    }
    setRecordedVideoUrl(null);
    setRecordingStatus('idle');
  };

  // Web Speech API Transcription
  const startSpeechRecognition = () => {
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRec) {
      console.warn('Web Speech API not supported in this browser. Manual transcript entry available.');
      return;
    }

    try {
      const recognition = new SpeechRec();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript + ' ';
        }
        setCandidateAnswer(currentTranscript.trim());
      };

      recognition.onerror = (e: any) => {
        console.warn('Speech recognition event:', e.error);
      };

      recognition.start();
      recognitionRef.current = recognition;
      setIsSpeechRecognitionActive(true);
    } catch (e) {
      console.warn('Speech recognition init error:', e);
    }
  };

  const stopSpeechRecognition = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsSpeechRecognitionActive(false);
    }
  };

  // Submit Answer to Current Question
  const handleSubmitAnswer = async () => {
    if (!session || !candidateAnswer.trim()) {
      toast.warning('Please record or enter your response transcript before submitting.');
      return;
    }

    handleStopRecording();
    setIsSubmitting(true);

    const activeQ = session.questions[currentQuestionIdx];
    try {
      const res = await apiClient.post(`/interviews/${session.id}/answer`, {
        question_id: activeQ.id,
        candidate_answer: candidateAnswer.trim(),
        time_spent_seconds: Math.max(15, questionTimer),
        pauses_count: pausesCount,
        has_local_recording: !!recordedVideoUrl,
        recording_storage_key: recordedVideoUrl ? `local_blob_${activeQ.id}` : undefined,
      });

      setStepEvaluation(res.data);
      toast.success('Answer evaluated successfully!');

      // Refresh session questions to fetch any dynamic follow-up created
      const sessionRes = await apiClient.get(`/interviews/${session.id}`);
      setSession(sessionRes.data);
    } catch (err) {
      console.error('Answer submission failed:', err);
      toast.error('Failed to evaluate answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Proceed to Next Question
  const handleProceedNextQuestion = () => {
    if (!session) return;
    const nextIdx = currentQuestionIdx + 1;

    if (nextIdx < session.total_questions) {
      setCurrentQuestionIdx(nextIdx);
      setCandidateAnswer('');
      setQuestionTimer(0);
      setPausesCount(0);
      setStepEvaluation(null);
      setRecordingStatus('idle');
      setRecordedVideoUrl(null);

      const nextQ = session.questions[nextIdx];
      if (nextQ) {
        speakQuestion(nextQ.question_text);
      }
    } else {
      // Completed all questions -> finalize session
      handleCompleteInterview();
    }
  };

  // Finalize Interview & Generate Executive Report
  const handleCompleteInterview = async () => {
    if (!session) return;
    setIsSubmitting(true);
    try {
      const res = await apiClient.post(`/interviews/${session.id}/complete`);
      setSession(res.data);
      setStage('completed');
      toast.success('Interview complete! Executive scorecard generated.');
    } catch (err) {
      console.error('Failed to complete interview:', err);
      toast.error('Failed to synthesize final scorecard.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Download PDF Report
  const handleDownloadPdf = async () => {
    if (!session) return;
    setIsDownloadingPdf(true);
    try {
      const response = await apiClient.get(`/interviews/${session.id}/report-pdf`, {
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Mock_Interview_Report_Session_${session.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Report PDF downloaded successfully!');
    } catch (err) {
      console.error('PDF download failed:', err);
      toast.error('Error downloading report PDF.');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const activeQuestion = session?.questions?.[currentQuestionIdx];

  // Radar chart data for final report
  const radarData = session
    ? [
        { subject: 'Technical', score: session.technical_score, fullMark: 100 },
        { subject: 'Communication', score: session.communication_score, fullMark: 100 },
        { subject: 'Problem Solving', score: session.problem_solving_score || session.overall_score, fullMark: 100 },
        { subject: 'Answer Quality', score: session.answer_quality_score || session.overall_score, fullMark: 100 },
        { subject: 'Behavioral / STAR', score: session.behavioral_score, fullMark: 100 },
      ]
    : [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-black text-slate-100 flex items-center gap-2.5">
            <Bot className="w-7 h-7 text-cyan-400" />
            <span>Virtual AI Mock Interview & Career Coach</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Realistic turn-by-turn interview simulation, private local video recording, speech analytics, and executive evaluation.
          </p>
        </div>

        {stage === 'active' && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAiVoiceMuted(!aiVoiceMuted)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                aiVoiceMuted
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                  : 'bg-slate-900 text-slate-300 border-slate-800 hover:text-white'
              }`}
            >
              {aiVoiceMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 text-cyan-400" />}
              <span>{aiVoiceMuted ? 'Interviewer Muted' : 'Interviewer Voice Active'}</span>
            </button>

            <button
              onClick={() => setShowEndEarlyModal(true)}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border border-rose-500/30 text-rose-400 hover:bg-rose-500/10 transition-all"
              title="Conclude interview early and generate scorecard"
            >
              <Square className="w-3.5 h-3.5 fill-rose-400/40" />
              <span>Conclude Early</span>
            </button>
          </div>
        )}
      </div>

      {/* STAGE 1: INTERVIEW SETUP */}
      {stage === 'setup' && (
        <div className="p-6 md:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-black text-slate-100 flex items-center gap-2">
                <Sliders className="w-5 h-5 text-cyan-400" />
                <span>Customize Your Mock Interview Session</span>
              </h2>
              <p className="text-xs text-slate-400">
                Configure your target role, interview specialization, experience level, and duration.
              </p>
            </div>
            <div className="flex items-center gap-1 text-[11px] text-emerald-400 font-semibold bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Private Local Recording</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Target Job Role */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Target Job Role</label>
              <select
                value={roleTitle}
                onChange={(e) => setRoleTitle(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {SUPPORTED_ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            {/* Interview Type */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Interview Type</label>
              <select
                value={interviewType}
                onChange={(e) => setInterviewType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {INTERVIEW_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            {/* Target Company (if Company-Specific) */}
            {interviewType === 'Company-specific' && (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
                  <Building className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Target Company Culture</span>
                </label>
                <select
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  {TARGET_COMPANIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Experience Level */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Experience Level</label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {EXPERIENCE_LEVELS.map((lvl) => (
                  <option key={lvl} value={lvl}>{lvl}</option>
                ))}
              </select>
            </div>

            {/* Difficulty */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Difficulty Level</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {['Beginner', 'Intermediate', 'Advanced', 'Expert'].map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Question Count / Duration */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Interview Duration</label>
              <select
                value={totalQuestions}
                onChange={(e) => setTotalQuestions(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value={3}>Express Mock (3 Questions • ~10 mins)</option>
                <option value={5}>Standard Mock (5 Questions • ~15 mins)</option>
                <option value={7}>In-Depth Mock (7 Questions • ~25 mins)</option>
              </select>
            </div>
          </div>

          {/* Technical Subjects Tags */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Core Technical Focus (Select topics to drill)
            </label>
            <div className="flex flex-wrap gap-2">
              {ALL_SUBJECTS.map((subj) => {
                const isSelected = selectedSubjects.includes(subj);
                return (
                  <button
                    key={subj}
                    type="button"
                    onClick={() => {
                      if (isSelected) {
                        setSelectedSubjects(selectedSubjects.filter((s) => s !== subj));
                      } else {
                        setSelectedSubjects([...selectedSubjects, subj]);
                      }
                    }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
                      isSelected
                        ? 'bg-cyan-600/20 text-cyan-300 border-cyan-500/50 shadow-sm'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {subj} {isSelected && '✓'}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Launch Button */}
          <button
            onClick={handleStartInterview}
            disabled={isStarting}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-black text-sm flex items-center justify-center gap-2.5 shadow-xl shadow-cyan-600/20 disabled:opacity-50 transition-all hover:scale-[1.01]"
          >
            {isStarting ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Initializing AI Interviewer Persona...
              </span>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Enter AI Interview Chamber</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* STAGE 2: ACTIVE INTERVIEW CHAIR */}
      {stage === 'active' && activeQuestion && (
        <div className="space-y-6">
          {/* Header Progress Counter */}
          <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4 shadow-lg">
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Question {currentQuestionIdx + 1} of {session?.total_questions}
              </span>
              <span className="text-xs font-bold text-slate-300">{activeQuestion.category}</span>
              {activeQuestion.is_follow_up && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Adaptive Follow-Up
                </span>
              )}
            </div>

            <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Timer: {Math.floor(questionTimer / 60)}:{String(questionTimer % 60).padStart(2, '0')}</span>
            </div>
          </div>

          {/* AI Question Persona Bubble */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-cyan-500/30 shadow-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
              <Bot className="w-4 h-4" />
              <span>AI Senior Technical Interviewer</span>
            </div>
            <p className="text-base font-bold text-slate-100 leading-relaxed font-sans">
              "{activeQuestion.question_text}"
            </p>
          </div>

          {/* Dual-Column Studio Workspace */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column: Webcam & MediaRecorder Recording Studio */}
            <div className="lg:col-span-6 space-y-4">
              <div className="relative rounded-2xl overflow-hidden bg-slate-950 border border-slate-800 shadow-2xl aspect-video flex items-center justify-center">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className={`w-full h-full object-cover transform -scale-x-100 transition-opacity ${
                    cameraEnabled ? 'opacity-100' : 'opacity-0'
                  }`}
                />

                {!cameraEnabled && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950 text-slate-500">
                    <VideoOff className="w-10 h-10 mb-2" />
                    <span className="text-xs">Camera Feed Inactive</span>
                  </div>
                )}

                {/* Live REC Indicator */}
                {recordingStatus === 'recording' && (
                  <div className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1 rounded-full bg-rose-950/80 border border-rose-500/40 text-rose-400 text-[11px] font-bold backdrop-blur">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    <span>REC (Live WebM)</span>
                  </div>
                )}

                {/* Audio Level VU Bar */}
                <div className="absolute bottom-3 left-3 right-20 flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800 backdrop-blur">
                  <Mic className={`w-3.5 h-3.5 ${micEnabled ? 'text-cyan-400' : 'text-slate-600'}`} />
                  <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 transition-all duration-75"
                      style={{ width: `${micEnabled ? volumeLevel : 0}%` }}
                    />
                  </div>
                </div>

                {/* Hardware Toggle Buttons */}
                <div className="absolute bottom-3 right-3 flex items-center gap-1.5">
                  <button
                    onClick={handleToggleCamera}
                    className={`p-2 rounded-xl backdrop-blur transition-all ${
                      cameraEnabled ? 'bg-slate-900/80 text-slate-200' : 'bg-rose-500/20 text-rose-400'
                    }`}
                    title={cameraEnabled ? 'Turn Off Camera' : 'Turn On Camera'}
                  >
                    {cameraEnabled ? <Video className="w-3.5 h-3.5" /> : <VideoOff className="w-3.5 h-3.5" />}
                  </button>
                  <button
                    onClick={handleToggleMic}
                    className={`p-2 rounded-xl backdrop-blur transition-all ${
                      micEnabled ? 'bg-slate-900/80 text-slate-200' : 'bg-rose-500/20 text-rose-400'
                    }`}
                    title={micEnabled ? 'Mute Mic' : 'Unmute Mic'}
                  >
                    {micEnabled ? <Mic className="w-3.5 h-3.5" /> : <MicOff className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* MediaRecorder Controls Toolbar */}
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-3 shadow">
                <div className="flex items-center gap-2">
                  {recordingStatus === 'idle' && (
                    <button
                      onClick={handleStartRecording}
                      className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs flex items-center gap-2 shadow"
                    >
                      <span className="w-2.5 h-2.5 rounded-full bg-white" />
                      <span>Record Answer</span>
                    </button>
                  )}

                  {recordingStatus === 'recording' && (
                    <>
                      <button
                        onClick={handlePauseRecording}
                        className="px-3 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs flex items-center gap-1.5"
                      >
                        <Pause className="w-3.5 h-3.5" />
                        <span>Pause</span>
                      </button>
                      <button
                        onClick={handleStopRecording}
                        className="px-4 py-2 rounded-xl bg-rose-700 hover:bg-rose-600 text-white font-bold text-xs flex items-center gap-1.5"
                      >
                        <Square className="w-3.5 h-3.5 fill-white" />
                        <span>Finish Recording</span>
                      </button>
                    </>
                  )}

                  {recordingStatus === 'paused' && (
                    <button
                      onClick={handleResumeRecording}
                      className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5"
                    >
                      <Play className="w-3.5 h-3.5 fill-white" />
                      <span>Resume</span>
                    </button>
                  )}

                  {recordingStatus === 'stopped' && (
                    <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Recording Stored Locally</span>
                    </span>
                  )}
                </div>

                {/* Local Storage Recording Actions */}
                {recordedVideoUrl && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowPlaybackModal(true)}
                      className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold flex items-center gap-1 border border-slate-700"
                    >
                      <Eye className="w-3 h-3" />
                      <span>Review Video</span>
                    </button>
                    <button
                      onClick={handleSaveRecordingLocally}
                      className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1 border border-slate-700"
                      title="Save recording to local storage"
                    >
                      <Download className="w-3 h-3" />
                      <span>Save</span>
                    </button>
                    <button
                      onClick={handleDeleteRecording}
                      className="p-1.5 rounded-xl bg-slate-800 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 text-xs border border-slate-700"
                      title="Discard video"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>

              {/* Local Storage Privacy Assurance */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-[11px] text-slate-400 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>
                  Video and audio are held strictly in private browser local memory. No media streams are uploaded without explicit consent.
                </span>
              </div>
            </div>

            {/* Right Column: Transcript, Speech-to-Text & Evaluation */}
            <div className="lg:col-span-6 space-y-4">
              <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-cyan-400" />
                    <span>Answer Transcript (Spoken or Typed)</span>
                  </label>
                  {isSpeechRecognitionActive && (
                    <span className="text-[10px] text-cyan-400 animate-pulse font-mono flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                      <span>Live Transcribing Speech...</span>
                    </span>
                  )}
                </div>

                <textarea
                  rows={8}
                  value={candidateAnswer}
                  onChange={(e) => setCandidateAnswer(e.target.value)}
                  placeholder="Your speech transcript will populate live here as you record, or you may manually draft your answer directly..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                />

                {/* Submit Action */}
                {!stepEvaluation ? (
                  <button
                    onClick={handleSubmitAnswer}
                    disabled={isSubmitting || !candidateAnswer.trim()}
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-black text-xs flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 transition-all hover:scale-[1.01]"
                  >
                    {isSubmitting ? (
                      <span className="flex items-center gap-2">
                        <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        AI Evaluating Response & Pacing...
                      </span>
                    ) : (
                      <>
                        <Send className="w-3.5 h-3.5" />
                        <span>Submit Answer for AI Review</span>
                      </>
                    )}
                  </button>
                ) : (
                  <div className="space-y-4 pt-2">
                    {/* Evaluation Score Card */}
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-xs font-bold text-slate-200">Answer Evaluation</div>
                          <div className="text-[11px] text-slate-400 mt-0.5">
                            Speech: {stepEvaluation.wpm} WPM • {stepEvaluation.total_fillers || 0} Filler Words
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-lg font-black text-emerald-400">
                            {stepEvaluation.score_out_of_10 || (stepEvaluation.score ? round(stepEvaluation.score / 10, 1) : 0)} / 10
                          </span>
                          <div className="text-[10px] text-slate-400">({stepEvaluation.score}% Grade)</div>
                        </div>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                        {stepEvaluation.feedback}
                      </p>

                      {/* Correct vs Missing Points */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        <div className="space-y-1">
                          <div className="text-[11px] font-bold text-emerald-400 uppercase flex items-center gap-1">
                            <Check className="w-3 h-3" />
                            <span>Strong Points</span>
                          </div>
                          <ul className="list-disc pl-4 text-slate-300 space-y-0.5">
                            {stepEvaluation.correct_points?.map((cp, i) => (
                              <li key={i}>{cp}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="space-y-1">
                          <div className="text-[11px] font-bold text-amber-400 uppercase flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Missing Concepts</span>
                          </div>
                          <ul className="list-disc pl-4 text-slate-300 space-y-0.5">
                            {stepEvaluation.missing_concepts?.map((mc, i) => (
                              <li key={i}>{mc}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Proceed Button */}
                    <button
                      onClick={handleProceedNextQuestion}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg"
                    >
                      <span>
                        {currentQuestionIdx + 1 < (session?.total_questions || 5)
                          ? 'Advance to Next Question'
                          : 'Conclude Interview & Review Full Scorecard'}
                      </span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* VIDEO PLAYBACK MODAL */}
      {showPlaybackModal && recordedVideoUrl && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-2xl w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Video className="w-4 h-4 text-cyan-400" />
                <span>Review Recorded Answer Video</span>
              </h3>
              <button
                onClick={() => setShowPlaybackModal(false)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="rounded-2xl overflow-hidden aspect-video bg-black">
              <video src={recordedVideoUrl} controls autoPlay className="w-full h-full object-cover" />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={handleSaveRecordingLocally}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 border border-slate-700"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Save to Disk</span>
              </button>
              <button
                onClick={() => setShowPlaybackModal(false)}
                className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STAGE 3: EXECUTIVE FINAL REPORT */}
      {stage === 'completed' && session && (
        <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-8 animate-fadeIn">
          {/* Header Verdict Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
            <div>
              <div className="flex items-center gap-2.5">
                <Award className="w-7 h-7 text-amber-400" />
                <h2 className="text-2xl font-black text-slate-100">Executive Mock Interview Report</h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Role: <span className="text-slate-200 font-semibold">{session.role_title}</span> • Track:{' '}
                <span className="text-slate-200 font-semibold">{session.interview_type}</span> • Experience:{' '}
                <span className="text-slate-200 font-semibold">{session.experience_level}</span>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleDownloadPdf}
                disabled={isDownloadingPdf}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg disabled:opacity-50"
              >
                {isDownloadingPdf ? (
                  <span className="flex items-center gap-2">
                    <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Generating PDF...
                  </span>
                ) : (
                  <>
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Official PDF Report</span>
                  </>
                )}
              </button>

              <button
                onClick={() => {
                  setSession(null);
                  setStage('setup');
                }}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center gap-2 border border-slate-700"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Start New Mock</span>
              </button>
            </div>
          </div>

          {/* Key Score Highlights */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Overall Score</div>
              <div className="text-3xl font-black text-cyan-400">{session.overall_score}%</div>
              <div className="text-[10px] text-slate-400 font-mono">({round(session.overall_score / 10, 1)} / 10)</div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Technical Score</div>
              <div className="text-3xl font-black text-slate-100">{session.technical_score}%</div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Communication</div>
              <div className="text-3xl font-black text-indigo-400">{session.communication_score}%</div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Problem Solving</div>
              <div className="text-3xl font-black text-slate-100">{session.problem_solving_score || session.overall_score}%</div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-1 col-span-2 md:col-span-1">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Hiring Verdict</div>
              <div className={`text-xl font-black mt-1 ${
                session.verdict === 'Strong Hire' || session.verdict === 'Hire' ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {session.verdict}
              </div>
            </div>
          </div>

          {/* Radar Chart & Speech Analysis Side-by-Side */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Competency Radar Chart */}
            <div className="lg:col-span-6 p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <span>Multi-Dimensional Competency Profile</span>
              </h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
                    <Radar name="Candidate" dataKey="score" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.4} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Speech Communication Metrics */}
            <div className="lg:col-span-6 p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Mic className="w-4 h-4 text-cyan-400" />
                <span>Speech & Fluency Indicators</span>
              </h3>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[11px]">Average Speaking Pace</div>
                  <div className="text-lg font-bold text-slate-100">{session.average_wpm} WPM</div>
                  <div className="text-[10px] text-emerald-400">Target: 120-165 WPM</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[11px]">Total Filler Words</div>
                  <div className="text-lg font-bold text-amber-400">{session.total_filler_words}</div>
                  <div className="text-[10px] text-slate-400">('um', 'like', 'basically')</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[11px]">Clarity Rating</div>
                  <div className="text-lg font-bold text-cyan-400">{session.clarity_rating}</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[11px]">Total Speaking Time</div>
                  <div className="text-lg font-bold text-slate-100">{Math.round(session.duration_seconds / 60)} mins</div>
                </div>
              </div>

              {/* Actionable Coaching Summary */}
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                {session.overall_summary}
              </div>
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-slate-950 border border-emerald-500/20 space-y-3">
              <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4" />
                <span>Demonstrated Technical Strengths</span>
              </div>
              <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1.5">
                {session.key_strengths?.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-slate-950 border border-amber-500/20 space-y-3">
              <div className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" />
                <span>Targeted Growth Opportunities</span>
              </div>
              <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1.5">
                {session.areas_to_improve?.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Actionable 4-Step Improvement Plan */}
          {session.improvement_plan && session.improvement_plan.length > 0 && (
            <div className="p-6 rounded-2xl bg-slate-950 border border-indigo-500/20 space-y-3">
              <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                <span>Personalized 4-Step Career Coach Improvement Plan</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {session.improvement_plan.map((step, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 leading-relaxed font-sans">
                    {step}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Question-by-Question Deep Dive */}
          <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Question-by-Question Detailed Breakdown</span>
            </h3>

            <div className="space-y-4">
              {session.questions?.map((q) => (
                <div key={q.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-400">
                      Q{q.question_order} • {q.category} {q.is_follow_up && '(Adaptive Follow-up)'}
                    </span>
                    <span className="text-xs font-black text-emerald-400">
                      {q.score_out_of_10 || (q.score ? round(q.score / 10, 1) : 0)} / 10 ({q.score}% Grade)
                    </span>
                  </div>

                  <p className="text-xs font-bold text-slate-200">{q.question_text}</p>

                  <div className="p-3 rounded-lg bg-slate-950 text-xs text-slate-400 italic">
                    Candidate: "{q.candidate_answer || 'No response recorded'}"
                  </div>

                  <div className="text-xs text-slate-300">
                    <strong className="text-indigo-400">Coaching Feedback: </strong>
                    {q.feedback}
                  </div>

                  {q.ideal_answer && (
                    <div className="p-3 rounded-lg bg-slate-950 border border-emerald-500/20 text-xs text-slate-300">
                      <strong className="text-emerald-400 uppercase text-[10px] block mb-1">Model Answer:</strong>
                      {q.ideal_answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Ethical AI Limitations Disclaimer */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-500 text-[11px] leading-relaxed flex items-center gap-2.5">
            <Info className="w-4 h-4 shrink-0 text-slate-400" />
            <span>
              {session.assessment_disclaimer ||
                'Notice: Audio, video, and speech analyses are heuristic coaching estimates. Antigravity AI does not claim to detect personality, honesty, or cognitive suitability from facial appearance.'}
            </span>
          </div>
        </div>
      )}

      {/* Early Conclusion Confirmation Dialog */}
      <ConfirmationModal
        isOpen={showEndEarlyModal}
        title="Conclude Interview Early?"
        message="Are you sure you want to conclude the mock interview now? An executive scorecard will be synthesized based on your responses completed so far."
        confirmText="Yes, Conclude Interview"
        cancelText="Continue Interview"
        isDestructive={false}
        icon="warning"
        onConfirm={() => {
          setShowEndEarlyModal(false);
          handleCompleteInterview();
        }}
        onCancel={() => setShowEndEarlyModal(false)}
      />
    </div>
  );
};

// Helper for round display
function round(num: number, decimals: number) {
  return Number(Math.round(Number(num + 'e' + decimals)) + 'e-' + decimals);
}
