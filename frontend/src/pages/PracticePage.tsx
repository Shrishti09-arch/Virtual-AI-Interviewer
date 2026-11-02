import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useToast } from '../context/ToastContext';
import { ConfirmationModal } from '../components/ConfirmationModal';
import {
  Code2,
  Search,
  Filter,
  CheckCircle,
  HelpCircle,
  Sparkles,
  ArrowRight,
  Send,
  Zap,
  BookOpen,
  Play,
  Terminal,
  Check,
  X,
  ExternalLink,
  Award,
  AlertCircle,
  RotateCcw,
  Layers,
  ListChecks,
  GraduationCap,
  TrendingUp,
  ChevronRight,
} from 'lucide-react';

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

const SUPPORTED_SUBJECTS = [
  'Data Structures and Algorithms',
  'Java',
  'Python',
  'C++',
  'Operating Systems',
  'DBMS',
  'Computer Networks',
  'Artificial Intelligence',
  'Machine Learning',
  'Deep Learning',
  'SQL',
  'System Design',
  'OOP',
  'Computer Science Fundamentals',
];

const SUPPORTED_DIFFICULTIES = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];

const SUPPORTED_TYPES = [
  'Comprehensive Mixed',
  'MCQs',
  'Coding questions',
  'Theoretical questions',
  'Scenario-based questions',
  'Problem-solving questions',
  'Company-level questions',
  'Real-world technical questions',
];

const SUPPORTED_LANGUAGES = ['Python', 'Java', 'C++', 'SQL', 'JavaScript', 'Go'];

interface QuestionItem {
  id: number;
  category: string;
  subject?: string;
  difficulty: string;
  role_track: string;
  programming_language?: string;
  question_type?: string;
  title: string;
  question_text: string;
  expected_keywords?: string[];
  sample_answer?: string;
  hints?: string[];
  options?: string[];
  explanation?: string;
  code_template?: string;
  test_cases?: any[];
  source_type?: string;
  source_name?: string;
  source_url?: string;
}

interface EvaluationResult {
  id?: number;
  question_id: number;
  question_type?: string;
  score: number;
  feedback?: string;
  strengths?: string[];
  missing_concepts?: string[];
  is_correct?: boolean;
  selected_option_index?: number;
  correct_option_index?: number;
  explanation?: string;
  sample_answer?: string;
  ideal_answer?: string;
  status?: string;
  passed_tests?: number;
  total_tests?: number;
  test_results?: any[];
  error?: string;
  is_fallback?: boolean;
  provider_used?: string;
  model_used?: string;
}

interface FinalReport {
  session_id: number;
  job_role: string;
  subject: string;
  programming_language: string;
  difficulty: string;
  total_questions: number;
  correct_count: number;
  incorrect_count: number;
  accuracy: number;
  topic_performance: Record<string, { total: number; correct: number; average_score: number }>;
  weak_areas: string[];
  recommended_topics: string[];
  answers_review: any[];
}

export const PracticePage: React.FC = () => {
  const toast = useToast();
  // Navigation Tabs: 'interactive' or 'bank'
  const [activeTab, setActiveTab] = useState<'interactive' | 'bank'>('interactive');

  // Interactive Session Config State
  const [configRole, setConfigRole] = useState<string>('Software Development Engineer');
  const [configSubject, setConfigSubject] = useState<string>('Data Structures and Algorithms');
  const [configLang, setConfigLang] = useState<string>('Python');
  const [configDifficulty, setConfigDifficulty] = useState<string>('Intermediate');
  const [configCount, setConfigCount] = useState<number>(3);
  const [configType, setConfigType] = useState<string>('Comprehensive Mixed');
  const [isStartingSession, setIsStartingSession] = useState<boolean>(false);

  // Active Session State
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [currentIdx, setCurrentIdx] = useState<number>(0);
  const [totalQuestions, setTotalQuestions] = useState<number>(0);
  const [activeQuestion, setActiveQuestion] = useState<QuestionItem | null>(null);
  const [isSessionCompleted, setIsSessionCompleted] = useState<boolean>(false);
  const [finalReport, setFinalReport] = useState<FinalReport | null>(null);
  const [showExitModal, setShowExitModal] = useState<boolean>(false);

  // Active Question Input State
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [codeAnswer, setCodeAnswer] = useState<string>('');
  const [theoryAnswer, setTheoryAnswer] = useState<string>('');
  const [showHints, setShowHints] = useState<boolean>(false);
  const [showSampleAnswer, setShowSampleAnswer] = useState<boolean>(false);

  // Subprocess Sandbox Test-run State
  const [isExecutingSandbox, setIsExecutingSandbox] = useState<boolean>(false);
  const [sandboxResult, setSandboxResult] = useState<any | null>(null);

  // Step Evaluation State (after submitting current question)
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState<boolean>(false);
  const [stepEvaluation, setStepEvaluation] = useState<EvaluationResult | null>(null);

  // Question Bank Browse State
  const [bankQuestions, setBankQuestions] = useState<QuestionItem[]>([]);
  const [bankSubject, setBankSubject] = useState<string>('All');
  const [bankDifficulty, setBankDifficulty] = useState<string>('All');
  const [bankType, setBankType] = useState<string>('All');
  const [bankSearch, setBankSearch] = useState<string>('');
  const [bankSelectedQ, setBankSelectedQ] = useState<QuestionItem | null>(null);
  const [bankUserAns, setBankUserAns] = useState<string>('');
  const [bankEval, setBankEval] = useState<EvaluationResult | null>(null);
  const [isBankSubmitting, setIsBankSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (activeTab === 'bank') {
      fetchBankQuestions();
    }
  }, [activeTab, bankSubject, bankDifficulty, bankType]);

  const fetchBankQuestions = async () => {
    try {
      const res = await apiClient.get('/practice/questions', {
        params: {
          subject: bankSubject !== 'All' ? bankSubject : undefined,
          difficulty: bankDifficulty !== 'All' ? bankDifficulty : undefined,
          question_type: bankType !== 'All' ? bankType : undefined,
          search: bankSearch.trim() || undefined,
        },
      });
      setBankQuestions(res.data);
      if (res.data.length > 0 && !bankSelectedQ) {
        setBankSelectedQ(res.data[0]);
      }
    } catch (err) {
      console.error('Failed to load question bank:', err);
    }
  };

  // Start Interactive Practice Session
  const handleStartSession = async () => {
    setIsStartingSession(true);
    setStepEvaluation(null);
    setFinalReport(null);
    setIsSessionCompleted(false);

    try {
      const res = await apiClient.post('/practice/session/start', {
        job_role: configRole,
        subject: configSubject,
        programming_language: configLang,
        difficulty: configDifficulty,
        total_questions: configCount,
        interview_type: configType,
      });

      setSessionId(res.data.session_id);
      setCurrentIdx(res.data.current_index);
      setTotalQuestions(res.data.total_questions);
      setActiveQuestion(res.data.active_question);

      // Reset question answer states
      resetQuestionInput(res.data.active_question);
      toast.success('Practice session started!');
    } catch (err) {
      console.error('Failed to start session:', err);
      toast.error('Failed to start practice session. Please try again.');
    } finally {
      setIsStartingSession(false);
    }
  };

  const resetQuestionInput = (q: QuestionItem | null) => {
    setSelectedOption(null);
    setTheoryAnswer('');
    setShowHints(false);
    setShowSampleAnswer(false);
    setStepEvaluation(null);
    setSandboxResult(null);

    if (q?.question_type === 'Coding' && q.code_template) {
      setCodeAnswer(q.code_template);
    } else {
      setCodeAnswer('');
    }
  };

  // Execute Code in Subprocess Sandbox
  const handleRunSandbox = async () => {
    if (!activeQuestion || !codeAnswer.trim()) return;

    setIsExecutingSandbox(true);
    try {
      const res = await apiClient.post('/practice/execute-code', {
        language: (activeQuestion.programming_language || configLang).toLowerCase(),
        code: codeAnswer,
        test_cases: activeQuestion.test_cases || [],
      });
      setSandboxResult(res.data);
      if (res.data?.success) {
        toast.success(`Executed successfully (${res.data.passed_tests || 0}/${res.data.total_tests || 0} tests passed)`);
      } else {
        toast.warning('Execution completed with errors or test failures.');
      }
    } catch (err) {
      console.error('Sandbox execution error:', err);
      toast.error('Error communicating with code execution sandbox.');
    } finally {
      setIsExecutingSandbox(false);
    }
  };

  // Submit Answer to Active Question
  const handleSubmitSessionAnswer = async () => {
    if (!sessionId || !activeQuestion) return;

    const qType = activeQuestion.question_type || 'Theory';

    let payload: any = {
      question_id: activeQuestion.id,
      answer_type: qType === 'MCQ' ? 'mcq' : qType === 'Coding' ? 'coding' : 'theory',
    };

    if (qType === 'MCQ') {
      if (selectedOption === null) {
        toast.warning('Please select an option before submitting.');
        return;
      }
      payload.selected_option_index = selectedOption;
    } else if (qType === 'Coding') {
      if (!codeAnswer.trim()) {
        toast.warning('Please enter your code solution.');
        return;
      }
      payload.code = codeAnswer;
      payload.language = (activeQuestion.programming_language || configLang).toLowerCase();
    } else {
      if (!theoryAnswer.trim()) {
        toast.warning('Please enter your response.');
        return;
      }
      payload.user_answer = theoryAnswer.trim();
    }

    setIsSubmittingAnswer(true);
    try {
      const res = await apiClient.post(`/practice/session/${sessionId}/answer`, payload);
      setStepEvaluation(res.data.evaluation);
      toast.success('Answer evaluated!');

      if (res.data.is_completed) {
        setIsSessionCompleted(true);
        setFinalReport(res.data.final_report);
        toast.success('Practice session completed! Final report ready.');
      } else {
        // Prepare next question cache
        setActiveQuestion(res.data.next_question);
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
      toast.error('Failed to evaluate response. Please try again.');
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleNextQuestion = () => {
    setStepEvaluation(null);
    setCurrentIdx((prev) => prev + 1);
    resetQuestionInput(activeQuestion);
  };

  // Submit in Bank Mode
  const handleBankSubmit = async () => {
    if (!bankSelectedQ || !bankUserAns.trim()) return;

    setIsBankSubmitting(true);
    try {
      const res = await apiClient.post(`/practice/questions/${bankSelectedQ.id}/submit`, {
        question_id: bankSelectedQ.id,
        user_answer: bankUserAns.trim(),
      });
      setBankEval(res.data);
      toast.success('Answer evaluated!');
    } catch (err) {
      console.error('Bank evaluation failed:', err);
      toast.error('Failed to evaluate question.');
    } finally {
      setIsBankSubmitting(false);
    }
  };

  const getDifficultyBadge = (diff: string) => {
    if (diff === 'Beginner' || diff === 'Easy') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    }
    if (diff === 'Intermediate' || diff === 'Medium') {
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
    }
    if (diff === 'Advanced' || diff === 'Hard') {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
    return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-black text-slate-100 flex items-center gap-2.5">
            <GraduationCap className="w-7 h-7 text-cyan-400" />
            <span>AI Technical Interview Practice & Sandbox</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Adaptive technical mock sessions, AST-isolated code runner, instant MCQ grading, and executive feedback.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1.5 rounded-2xl">
          <button
            onClick={() => setActiveTab('interactive')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'interactive'
                ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Play className="w-3.5 h-3.5" />
            <span>Mock Practice Session</span>
          </button>
          <button
            onClick={() => setActiveTab('bank')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'bank'
                ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Question Bank ({SUPPORTED_SUBJECTS.length} Subjects)</span>
          </button>
        </div>
      </div>

      {/* TAB 1: INTERACTIVE PRACTICE SESSION */}
      {activeTab === 'interactive' && (
        <div className="space-y-6">
          {/* Configuration Launchpad (shown when no active session or completed) */}
          {(!sessionId || isSessionCompleted) && !finalReport && (
            <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <span>Configure Your Practice Session</span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    Customize your target role, core subject, language, and difficulty.
                  </p>
                </div>
                <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Unique Questions Guard Active
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Job Role */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Target Job Role</label>
                  <select
                    value={configRole}
                    onChange={(e) => setConfigRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {SUPPORTED_ROLES.map((role) => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                </div>

                {/* Subject */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Subject (14 Standard)</label>
                  <select
                    value={configSubject}
                    onChange={(e) => setConfigSubject(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {SUPPORTED_SUBJECTS.map((subj) => (
                      <option key={subj} value={subj}>{subj}</option>
                    ))}
                  </select>
                </div>

                {/* Programming Language */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Programming Language</label>
                  <select
                    value={configLang}
                    onChange={(e) => setConfigLang(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {SUPPORTED_LANGUAGES.map((lang) => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>

                {/* Difficulty */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Difficulty Level</label>
                  <select
                    value={configDifficulty}
                    onChange={(e) => setConfigDifficulty(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {SUPPORTED_DIFFICULTIES.map((diff) => (
                      <option key={diff} value={diff}>{diff}</option>
                    ))}
                  </select>
                </div>

                {/* Interview Type */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Interview Type</label>
                  <select
                    value={configType}
                    onChange={(e) => setConfigType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {SUPPORTED_TYPES.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Number of Questions */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Number of Questions</label>
                  <select
                    value={configCount}
                    onChange={(e) => setConfigCount(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    {[3, 5, 8, 10].map((num) => (
                      <option key={num} value={num}>{num} Questions</option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                onClick={handleStartSession}
                disabled={isStartingSession}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-black text-sm flex items-center justify-center gap-2 shadow-xl shadow-cyan-600/20 disabled:opacity-50 transition-all hover:scale-[1.01]"
              >
                {isStartingSession ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Generating Session & Checking Uniqueness...
                  </span>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    <span>Launch Interactive Mock Session</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* ACTIVE PRACTICE WORKSPACE (Show one question at a time) */}
          {sessionId && !isSessionCompleted && activeQuestion && (
            <div className="space-y-6">
              {/* Progress & Metadata Bar */}
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4 shadow-lg">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    Question {currentIdx + 1} of {totalQuestions}
                  </span>
                  <span className="text-slate-400 text-xs font-semibold">{activeQuestion.subject}</span>
                  <span className="text-slate-600">•</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${getDifficultyBadge(activeQuestion.difficulty)}`}>
                    {activeQuestion.difficulty}
                  </span>
                  <span className="text-xs font-bold text-slate-400 bg-slate-950 px-2.5 py-0.5 rounded-lg border border-slate-800">
                    {activeQuestion.question_type}
                  </span>
                </div>

                {/* Transparent Source Attribution Label */}
                <div className="flex items-center gap-2 text-xs">
                  {activeQuestion.source_type === 'ai_generated' ? (
                    <span className="px-2.5 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-medium flex items-center gap-1.5">
                      <Sparkles className="w-3 h-3" />
                      <span>{activeQuestion.source_name || 'AI-Generated (Ollama)'}</span>
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium flex items-center gap-1.5">
                      <BookOpen className="w-3 h-3" />
                      <span>{activeQuestion.source_name || 'Curated Educational'}</span>
                      {activeQuestion.source_url && (
                        <a
                          href={activeQuestion.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:text-emerald-300 ml-1 inline-flex items-center"
                          title="View verified documentation source"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </span>
                  )}

                  <button
                    onClick={() => setShowExitModal(true)}
                    className="px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold flex items-center gap-1 transition-colors"
                    title="Exit and abandon current session"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Exit Session</span>
                  </button>
                </div>
              </div>

              {/* Question Statement Card */}
              <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-slate-100">{activeQuestion.title}</h2>
                  {activeQuestion.hints && activeQuestion.hints.length > 0 && (
                    <button
                      onClick={() => setShowHints(!showHints)}
                      className="text-xs text-amber-400 hover:text-amber-300 font-semibold flex items-center gap-1 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20"
                    >
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>{showHints ? 'Hide Hints' : 'View Hints'}</span>
                    </button>
                  )}
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-sm text-slate-200 leading-relaxed font-sans">
                  {activeQuestion.question_text}
                </div>

                {showHints && activeQuestion.hints && (
                  <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-1.5">
                    <div className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1">
                      <Zap className="w-3.5 h-3.5" />
                      <span>Architecture Hints:</span>
                    </div>
                    <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1">
                      {activeQuestion.hints.map((h, i) => (
                        <li key={i}>{h}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* QUESTION TYPE INTERFACES */}

              {/* 1. MCQ MODE */}
              {activeQuestion.question_type === 'MCQ' && (
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
                  <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Select the Most Appropriate Option:
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {activeQuestion.options?.map((opt, idx) => {
                      let optionClasses =
                        'p-4 rounded-2xl border text-xs font-medium text-left transition-all flex items-center gap-3 ';

                      if (stepEvaluation) {
                        // After submission: highlight correct in green, selected incorrect in red
                        if (idx === stepEvaluation.correct_option_index) {
                          optionClasses += 'bg-emerald-950/40 border-emerald-500 text-emerald-300';
                        } else if (idx === selectedOption) {
                          optionClasses += 'bg-rose-950/40 border-rose-500 text-rose-300';
                        } else {
                          optionClasses += 'bg-slate-950 border-slate-800 text-slate-500';
                        }
                      } else {
                        // Before submission
                        if (selectedOption === idx) {
                          optionClasses +=
                            'bg-indigo-950/50 border-indigo-500 text-slate-100 shadow-lg shadow-indigo-950/40';
                        } else {
                          optionClasses +=
                            'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300 hover:bg-slate-900';
                        }
                      }

                      return (
                        <button
                          key={idx}
                          disabled={stepEvaluation !== null}
                          onClick={() => setSelectedOption(idx)}
                          className={optionClasses}
                        >
                          <span
                            className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[11px] border ${
                              selectedOption === idx
                                ? 'bg-indigo-600 border-indigo-400 text-white'
                                : 'bg-slate-900 border-slate-700 text-slate-400'
                            }`}
                          >
                            {String.fromCharCode(65 + idx)}
                          </span>
                          <span className="flex-1 leading-relaxed">{opt}</span>
                          {stepEvaluation && idx === stepEvaluation.correct_option_index && (
                            <Check className="w-4 h-4 text-emerald-400" />
                          )}
                          {stepEvaluation && idx === selectedOption && idx !== stepEvaluation.correct_option_index && (
                            <X className="w-4 h-4 text-rose-400" />
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Submit / Next Button */}
                  {!stepEvaluation ? (
                    <button
                      onClick={handleSubmitSessionAnswer}
                      disabled={isSubmittingAnswer || selectedOption === null}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 transition-all"
                    >
                      {isSubmittingAnswer ? (
                        <span className="flex items-center gap-2">
                          <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Evaluating Option...
                        </span>
                      ) : (
                        <>
                          <CheckCircle className="w-4 h-4" />
                          <span>Submit MCQ Answer</span>
                        </>
                      )}
                    </button>
                  ) : (
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {stepEvaluation.is_correct ? (
                            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                              <CheckCircle className="w-4 h-4" />
                              <span>Correct (+100 pts)</span>
                            </span>
                          ) : (
                            <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                              <X className="w-4 h-4" />
                              <span>Incorrect (0 pts)</span>
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-slate-400">Score: {stepEvaluation.score} / 100</span>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
                        <strong className="text-cyan-400">Explanation: </strong>
                        {stepEvaluation.explanation}
                      </p>

                      <button
                        onClick={handleNextQuestion}
                        className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2"
                      >
                        <span>Advance to Next Question</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* 2. CODING CHALLENGE MODE */}
              {activeQuestion.question_type === 'Coding' && (
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-cyan-400" />
                      <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                        Isolated Code Sandbox Editor
                      </span>
                    </div>
                    <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/40 px-2.5 py-1 rounded-lg border border-cyan-800">
                      Language: {activeQuestion.programming_language || configLang}
                    </span>
                  </div>

                  {/* Code Editor Area */}
                  <div className="rounded-2xl border border-slate-800 bg-slate-950 overflow-hidden">
                    <div className="bg-slate-900/80 px-4 py-2 border-b border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                      <span>solution.py</span>
                      <span>Subprocess Sandbox (Timeout 3.0s, AST Protected)</span>
                    </div>
                    <textarea
                      rows={10}
                      value={codeAnswer}
                      onChange={(e) => setCodeAnswer(e.target.value)}
                      placeholder="# Write your algorithmic solution here..."
                      className="w-full bg-slate-950 p-4 text-xs font-mono text-cyan-300 focus:outline-none focus:ring-1 focus:ring-cyan-500 leading-relaxed resize-y"
                    />
                  </div>

                  {/* Test Cases Overview */}
                  {activeQuestion.test_cases && activeQuestion.test_cases.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Test Cases:</div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {activeQuestion.test_cases.map((tc: any, i: number) => (
                          <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-1">
                            <div className="text-slate-400 text-[10px]">Case {i + 1} {tc.hidden ? '(Hidden)' : ''}:</div>
                            <div className="text-slate-300 truncate">Input: <span className="text-slate-200">{tc.input}</span></div>
                            <div className="text-slate-300 truncate">Expected: <span className="text-emerald-400">{tc.expected_output}</span></div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sandbox Run Output */}
                  {sandboxResult && (
                    <div className={`p-4 rounded-2xl border space-y-2 ${
                      sandboxResult.passed
                        ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                        : 'bg-rose-950/20 border-rose-500/30 text-rose-300'
                    }`}>
                      <div className="flex items-center justify-between text-xs font-bold">
                        <span className="flex items-center gap-1.5">
                          {sandboxResult.passed ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <AlertCircle className="w-4 h-4 text-rose-400" />}
                          <span>Execution Status: {sandboxResult.status}</span>
                        </span>
                        <span>{sandboxResult.passed_tests} / {sandboxResult.total_tests} Tests Passed</span>
                      </div>

                      {sandboxResult.error && (
                        <div className="p-2.5 rounded-lg bg-slate-950 text-rose-400 text-xs font-mono">
                          {sandboxResult.error}
                        </div>
                      )}

                      <div className="space-y-1 max-h-36 overflow-y-auto">
                        {sandboxResult.test_results?.map((tr: any, idx: number) => (
                          <div key={idx} className="text-[11px] font-mono flex items-center justify-between p-1.5 bg-slate-950/60 rounded">
                            <span>Case {tr.test_index}: {tr.passed ? '✓ Passed' : '✗ Failed'}</span>
                            <span className="text-slate-400">{tr.execution_time_ms} ms</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons: Run in Sandbox vs Submit */}
                  <div className="flex flex-col sm:flex-row items-center gap-3">
                    <button
                      onClick={handleRunSandbox}
                      disabled={isExecutingSandbox || !codeAnswer.trim()}
                      className="w-full sm:w-1/2 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center gap-2 border border-slate-700 disabled:opacity-50 transition-all"
                    >
                      {isExecutingSandbox ? (
                        <span className="flex items-center gap-2">
                          <span className="w-3.5 h-3.5 border-2 border-slate-400 border-t-white rounded-full animate-spin" />
                          Testing in Sandbox...
                        </span>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Run Tests in Sandbox</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={handleSubmitSessionAnswer}
                      disabled={isSubmittingAnswer || !codeAnswer.trim()}
                      className="w-full sm:w-1/2 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 transition-all"
                    >
                      {isSubmittingAnswer ? (
                        <span className="flex items-center gap-2">
                          <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Grading Code...
                        </span>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>Submit Solution</span>
                        </>
                      )}
                    </button>
                  </div>

                  {stepEvaluation && (
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-200">
                          Score: {stepEvaluation.score} / 100 ({stepEvaluation.passed_tests}/{stepEvaluation.total_tests} Tests)
                        </span>
                        <span className="text-xs font-mono text-emerald-400">{stepEvaluation.status}</span>
                      </div>
                      <button
                        onClick={handleNextQuestion}
                        className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2"
                      >
                        <span>Advance to Next Question</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* 3. THEORY / SCENARIO / ARCHITECTURE MODE */}
              {activeQuestion.question_type !== 'MCQ' && activeQuestion.question_type !== 'Coding' && (
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-300">
                      Your Technical Explanation / Architecture
                    </label>
                    <button
                      onClick={() => setShowSampleAnswer(!showSampleAnswer)}
                      className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
                    >
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>{showSampleAnswer ? 'Hide Sample' : 'Peek Model Answer'}</span>
                    </button>
                  </div>

                  <textarea
                    rows={6}
                    value={theoryAnswer}
                    onChange={(e) => setTheoryAnswer(e.target.value)}
                    placeholder="Outline your architecture, edge cases, trade-offs, and technical rationale..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                  />

                  {showSampleAnswer && (
                    <div className="p-4 rounded-2xl bg-slate-950 border border-emerald-500/30 space-y-1">
                      <div className="text-xs font-bold text-emerald-400 uppercase">Ideal Solution:</div>
                      <p className="text-xs text-slate-300 leading-relaxed">{activeQuestion.sample_answer}</p>
                    </div>
                  )}

                  {!stepEvaluation ? (
                    <button
                      onClick={handleSubmitSessionAnswer}
                      disabled={isSubmittingAnswer || !theoryAnswer.trim()}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 transition-all"
                    >
                      {isSubmittingAnswer ? (
                        <span className="flex items-center gap-2">
                          <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Evaluating with AI Judge...
                        </span>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>Submit Solution for Evaluation</span>
                        </>
                      )}
                    </button>
                  ) : (
                    <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-xs font-bold text-slate-200">AI Evaluation Feedback</div>
                          <div className="text-[10px] text-slate-400">Score: {stepEvaluation.score} / 100</div>
                        </div>
                        <span className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                          stepEvaluation.score >= 70 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                        }`}>
                          {stepEvaluation.score >= 70 ? 'Passed' : 'Needs Work'}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                        {stepEvaluation.feedback}
                      </p>

                      <button
                        onClick={handleNextQuestion}
                        className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2"
                      >
                        <span>Advance to Next Question</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* FINAL EXECUTIVE PERFORMANCE REPORT */}
          {finalReport && (
            <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-6 animate-fadeIn">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <div className="flex items-center gap-2">
                    <Award className="w-6 h-6 text-amber-400" />
                    <h2 className="text-xl font-black text-slate-100">Practice Session Performance Report</h2>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Role: <span className="text-slate-200 font-semibold">{finalReport.job_role}</span> • Subject:{' '}
                    <span className="text-slate-200 font-semibold">{finalReport.subject}</span> • Difficulty:{' '}
                    <span className="text-slate-200 font-semibold">{finalReport.difficulty}</span>
                  </p>
                </div>

                <button
                  onClick={() => {
                    setSessionId(null);
                    setFinalReport(null);
                    setIsSessionCompleted(false);
                  }}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 flex items-center gap-2 border border-slate-700 transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Start New Session</span>
                </button>
              </div>

              {/* Metric Highlights */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-slate-400 uppercase">Total Questions</div>
                  <div className="text-2xl font-black text-slate-100">{finalReport.total_questions}</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-slate-400 uppercase">Correct Answers</div>
                  <div className="text-2xl font-black text-emerald-400">{finalReport.correct_count}</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-slate-400 uppercase">Incorrect / Partial</div>
                  <div className="text-2xl font-black text-rose-400">{finalReport.incorrect_count}</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[11px] font-bold text-slate-400 uppercase">Session Accuracy</div>
                  <div className="text-2xl font-black text-cyan-400">{finalReport.accuracy}%</div>
                </div>
              </div>

              {/* Topic-wise Performance Breakdown */}
              <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  <span>Topic-Wise Performance Breakdown</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(finalReport.topic_performance || {}).map(([subj, perf]) => (
                    <div key={subj} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-slate-200">{subj}</span>
                        <span className="font-mono text-cyan-400">{perf.average_score}% avg</span>
                      </div>
                      <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${perf.average_score}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {perf.correct} of {perf.total} problems solved correctly
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Weak Areas & Recommendations */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Weak Areas */}
                <div className="p-5 rounded-2xl bg-slate-950 border border-amber-500/20 space-y-3">
                  <div className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4" />
                    <span>Identified Weak Areas</span>
                  </div>
                  {finalReport.weak_areas.length > 0 ? (
                    <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1.5">
                      {finalReport.weak_areas.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-emerald-400">
                      Exceptional performance! Zero critical knowledge gaps identified.
                    </p>
                  )}
                </div>

                {/* Recommended Next Topics */}
                <div className="p-5 rounded-2xl bg-slate-950 border border-indigo-500/20 space-y-3">
                  <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4" />
                    <span>Recommended Next Topics</span>
                  </div>
                  <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1.5">
                    {finalReport.recommended_topics.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: QUESTION BANK BROWSER */}
      {activeTab === 'bank' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="p-5 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Subject Filter */}
              <select
                value={bankSubject}
                onChange={(e) => setBankSubject(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="All">All 14 Subjects</option>
                {SUPPORTED_SUBJECTS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>

              {/* Difficulty Filter */}
              <select
                value={bankDifficulty}
                onChange={(e) => setBankDifficulty(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="All">All Difficulties</option>
                {SUPPORTED_DIFFICULTIES.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>

              {/* Question Type Filter */}
              <select
                value={bankType}
                onChange={(e) => setBankType(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="All">All Question Types</option>
                <option value="MCQ">MCQ</option>
                <option value="Coding">Coding Challenge</option>
                <option value="Theory">Theory & Architecture</option>
                <option value="Scenario">Scenario & Scaling</option>
              </select>

              {/* Search Bar */}
              <div className="relative">
                <input
                  type="text"
                  value={bankSearch}
                  onChange={(e) => setBankSearch(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchBankQuestions()}
                  placeholder="Search problem title, keywords..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              </div>
            </div>
          </div>

          {/* Two-Column Explorer Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column: Questions List */}
            <div className="lg:col-span-5 space-y-3 max-h-[750px] overflow-y-auto pr-1">
              {bankQuestions.map((q) => (
                <div
                  key={q.id}
                  onClick={() => {
                    setBankSelectedQ(q);
                    setBankUserAns('');
                    setBankEval(null);
                  }}
                  className={`p-4 rounded-2xl cursor-pointer border transition-all ${
                    bankSelectedQ?.id === q.id
                      ? 'bg-indigo-950/40 border-indigo-500/50 shadow-lg shadow-indigo-950/50'
                      : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{q.subject || q.category}</span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[9px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-bold">
                        {q.question_type || 'Theory'}
                      </span>
                      <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold border ${getDifficultyBadge(q.difficulty)}`}>
                        {q.difficulty}
                      </span>
                    </div>
                  </div>
                  <h3 className="text-sm font-bold text-slate-200 leading-snug">{q.title}</h3>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">{q.question_text}</p>
                </div>
              ))}
              {bankQuestions.length === 0 && (
                <div className="p-8 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-2xl">
                  No questions match your current filters.
                </div>
              )}
            </div>

            {/* Right Column: Detail & Individual Practice */}
            <div className="lg:col-span-7 space-y-5">
              {bankSelectedQ ? (
                <div className="space-y-5">
                  <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                          {bankSelectedQ.subject || bankSelectedQ.category}
                        </span>
                        <span className="text-slate-600">•</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${getDifficultyBadge(bankSelectedQ.difficulty)}`}>
                          {bankSelectedQ.difficulty}
                        </span>
                      </div>

                      {bankSelectedQ.source_url && (
                        <a
                          href={bankSelectedQ.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold"
                        >
                          <span>{bankSelectedQ.source_name || 'Official Source'}</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>

                    <h2 className="text-lg font-bold text-slate-100">{bankSelectedQ.title}</h2>
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                      <p className="text-sm text-slate-200 leading-relaxed font-sans">{bankSelectedQ.question_text}</p>
                    </div>

                    {bankSelectedQ.hints && bankSelectedQ.hints.length > 0 && (
                      <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-1.5">
                        <div className="text-xs font-bold text-amber-400 uppercase">Hints:</div>
                        <ul className="list-disc pl-4 text-xs text-slate-300 space-y-1">
                          {bankSelectedQ.hints.map((h, i) => (
                            <li key={i}>{h}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Free Practice Workspace */}
                  <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-300">
                      Your Technical Answer
                    </label>
                    <textarea
                      rows={6}
                      value={bankUserAns}
                      onChange={(e) => setBankUserAns(e.target.value)}
                      placeholder="Draft your solution, explanation, or code approach..."
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                    />

                    <button
                      onClick={handleBankSubmit}
                      disabled={isBankSubmitting || !bankUserAns.trim()}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 transition-all"
                    >
                      {isBankSubmitting ? (
                        <span className="flex items-center gap-2">
                          <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Evaluating Solution...
                        </span>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>Submit for Instant AI Review</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Bank Evaluation Result */}
                  {bankEval && (
                    <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-bold text-slate-100 text-base">Grading Assessment</h3>
                          <span className="text-[10px] text-slate-400">
                            {bankEval.is_fallback ? 'Rule-Based Heuristic Evaluation' : 'AI Verified Evaluation'}
                          </span>
                        </div>
                        <div
                          className={`text-lg font-black px-3 py-1 rounded-xl border ${
                            bankEval.score >= 70
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          }`}
                        >
                          {bankEval.score} / 100
                        </div>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                        {bankEval.feedback}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-64 rounded-3xl bg-slate-900/40 border border-dashed border-slate-800 flex items-center justify-center text-slate-500 text-xs">
                  Select a question from the left column to view details and practice.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog to Abandon Active Session */}
      <ConfirmationModal
        isOpen={showExitModal}
        title="Exit Practice Session?"
        message="Are you sure you want to exit this active practice session? Any unsubmitted responses will be lost."
        confirmText="Exit Session"
        cancelText="Continue Practice"
        isDestructive={true}
        icon="danger"
        onConfirm={() => {
          setShowExitModal(false);
          setSessionId(null);
          setActiveQuestion(null);
          setStepEvaluation(null);
          setIsSessionCompleted(false);
          setFinalReport(null);
          toast.info('Practice session exited.');
        }}
        onCancel={() => setShowExitModal(false)}
      />
    </div>
  );
};
