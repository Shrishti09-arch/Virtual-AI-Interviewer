import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import { Link, useLocation } from 'react-router-dom';
import { MetricSkeleton, ChartSkeleton, TableSkeleton, Shimmer } from '../components/Skeleton';
import {
  Video,
  FileSearch,
  Code2,
  Milestone,
  TrendingUp,
  Award,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  BarChart3,
  Activity,
  Target,
  Zap,
  Layers,
  ChevronRight,
  BookOpen,
  RefreshCw,
  FileText,
  FileCheck,
  Check,
  ListChecks,
  ExternalLink,
  ShieldCheck,
  Compass,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from 'recharts';

interface ResumeScanItem {
  id: number;
  date: string;
  target_role: string;
  ats_score: number;
  keyword_match: number;
  structure: number;
  impact: number;
}

interface SubjectItem {
  subject: string;
  accuracy: number;
  questions_attempted: number;
  correct_answers?: number;
  sessions_count?: number;
  status: 'Strong' | 'Weak' | 'Developing';
  badge: string;
  recommendation?: string;
}

interface SkillImprovementItem {
  skill: string;
  frequency: number;
  priority: 'High' | 'Medium' | 'Low';
  recommendation: string;
}

interface ActivityItem {
  type: 'interview' | 'practice' | 'resume';
  title: string;
  description: string;
  score: number;
  date: string;
  link: string;
}

interface WeeklyActivityItem {
  day: string;
  date: string;
  interviews_count: number;
  practice_count: number;
  resumes_analyzed: number;
  roadmap_tasks_completed: number;
  total_activities: number;
  score: number;
}

interface InterviewHistoryItem {
  id: number;
  session_number: string;
  role: string;
  interview_type: string;
  difficulty: string;
  date: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  verdict: string;
  duration_seconds: number;
  total_questions: number;
}

interface PracticeHistoryItem {
  id: number;
  job_role: string;
  subject: string;
  difficulty: string;
  interview_type: string;
  total_questions: number;
  correct_count: number;
  accuracy: number;
  date: string;
  is_completed: boolean;
}

interface RoadmapMilestoneHistoryItem {
  id: number;
  phase_number: number;
  title: string;
  duration: string;
  estimated_hours: number;
  phase_progress: number;
  is_completed: boolean;
  completed_tasks: number;
  total_tasks: number;
}

interface RadarItem {
  subject: string;
  score: number;
  fullMark: number;
}

interface AnalyticsData {
  readiness_score: number;
  total_interviews: number;
  interview_count: number;
  average_interview_score: number;
  average_technical_score: number;
  average_communication_score: number;
  latest_ats_score: number;
  ats_improvement: {
    initial_score: number;
    latest_score: number;
    delta: number;
    percent_change: number;
    total_scans: number;
    history: ResumeScanItem[];
  };
  resume_improvement: {
    initial_score: number;
    latest_score: number;
    delta: number;
    total_scans: number;
    history: ResumeScanItem[];
  };
  technical_practice_accuracy: number;
  total_practice_sessions: number;
  total_practice_questions: number;
  practice_count: number;
  weak_subjects: SubjectItem[];
  strong_subjects: SubjectItem[];
  developing_subjects: SubjectItem[];
  completed_roadmap_tasks: number;
  total_roadmap_tasks: number;
  roadmap_progress: {
    total_tasks: number;
    completed_tasks: number;
    total_milestones: number;
    completed_milestones: number;
    progress_pct: number;
    active_phase_title: string;
    active_objectives: string[];
    milestones: RoadmapMilestoneHistoryItem[];
  };
  weekly_learning_activity: WeeklyActivityItem[];
  weekly_performance: WeeklyActivityItem[];
  recent_activities: ActivityItem[];
  skills_needing_improvement: SkillImprovementItem[];
  interview_trends: any[];
  interview_history: InterviewHistoryItem[];
  practice_history: PracticeHistoryItem[];
  resume_history: ResumeScanItem[];
  radar_data: RadarItem[];
}

interface DashboardPageProps {
  initialTab?: 'overview' | 'progress';
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ initialTab = 'overview' }) => {
  const { user } = useAuth();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<'overview' | 'progress'>(
    location.pathname === '/progress' || initialTab === 'progress' ? 'progress' : 'overview'
  );
  const [activeHistoryTab, setActiveHistoryTab] = useState<'interviews' | 'practice' | 'resumes' | 'roadmap'>('interviews');
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchAnalytics = async () => {
    try {
      setRefreshing(true);
      const res = await apiClient.get('/analytics/dashboard');
      setAnalytics(res.data);
    } catch (err) {
      console.error('Failed to load dashboard analytics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  useEffect(() => {
    if (location.pathname === '/progress') {
      setActiveTab('progress');
    }
  }, [location.pathname]);

  if (loading) {
    return (
      <div className="space-y-8 p-6 max-w-7xl mx-auto animate-fadeIn">
        {/* Header Skeleton */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
          <div className="space-y-2">
            <Shimmer className="h-5 w-48 rounded-full" />
            <Shimmer className="h-8 w-72 rounded-xl" />
            <Shimmer className="h-4 w-96 rounded-lg" />
          </div>
          <Shimmer className="h-10 w-52 rounded-2xl" />
        </div>

        {/* 4 Metric Cards Skeletons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <MetricSkeleton />
          <MetricSkeleton />
          <MetricSkeleton />
          <MetricSkeleton />
        </div>

        {/* 2 Chart Skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>

        {/* Table Skeleton */}
        <TableSkeleton rows={4} />
      </div>
    );
  }

  // Values from backend with resilient fallbacks
  const readiness = analytics?.readiness_score ?? 76;
  const totalInterviews = analytics?.total_interviews ?? analytics?.interview_count ?? 0;
  const avgInterviewScore = analytics?.average_interview_score ?? 75;
  const avgTech = analytics?.average_technical_score ?? 72;
  const avgComm = analytics?.average_communication_score ?? 75;

  const atsScore = analytics?.latest_ats_score ?? 68;
  const initialAts = analytics?.ats_improvement?.initial_score ?? 60;
  const atsDelta = analytics?.ats_improvement?.delta ?? 0;
  const atsPct = analytics?.ats_improvement?.percent_change ?? 0;
  const totalScans = analytics?.ats_improvement?.total_scans ?? 0;

  const practiceAccuracy = analytics?.technical_practice_accuracy ?? 78;
  const practiceSessionsCount = analytics?.total_practice_sessions ?? 0;
  const practiceQuestionsCount = analytics?.total_practice_questions ?? 0;

  const completedRoadmapTasks = analytics?.completed_roadmap_tasks ?? 0;
  const totalRoadmapTasks = analytics?.total_roadmap_tasks ?? 16;
  const roadmapPct = analytics?.roadmap_progress?.progress_pct ?? 25;
  const completedMilestones = analytics?.roadmap_progress?.completed_milestones ?? 1;
  const totalMilestones = analytics?.roadmap_progress?.total_milestones ?? 4;
  const activePhase = analytics?.roadmap_progress?.active_phase_title ?? 'Phase 1: Advanced Core Competencies';
  const activeObjectives = analytics?.roadmap_progress?.active_objectives ?? [
    'Master asynchronous patterns & memory lifecycle',
    'Deep-dive into REST, caching layers, and database normalization',
  ];

  const strongSubjects = analytics?.strong_subjects ?? [];
  const weakSubjects = analytics?.weak_subjects ?? [];
  const weeklyData = analytics?.weekly_learning_activity ?? analytics?.weekly_performance ?? [];

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* 1. Header with Tab Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI Career Command Center</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {activeTab === 'progress' ? 'My Learning Progress & Analytics' : `Welcome back, ${user?.full_name || 'Candidate'}!`}
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Targeting <span className="text-indigo-400 font-semibold">{user?.role_target || 'Full Stack Software Engineer'}</span>.
            Track your interview progression, ATS score gains, practice accuracy, and roadmap milestones.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-2xl border border-slate-800 shrink-0 self-start md:self-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'overview'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Dashboard Overview</span>
          </button>
          <button
            onClick={() => setActiveTab('progress')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'progress'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>My Progress</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-400/20 text-indigo-200 font-extrabold">
              Module 7
            </span>
          </button>
          <button
            onClick={fetchAnalytics}
            disabled={refreshing}
            title="Sync Metrics"
            className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* 2. Top Metric Cards (Core Tracked Progress Dimensions) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Total Mock Interviews & Avg Score */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-lg flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Total Mock Interviews
              </span>
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Video className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white">{totalInterviews}</span>
              <span className="text-slate-500 text-sm font-semibold">Sessions</span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-300">
                <span>Avg Score: <strong className="text-indigo-400">{avgInterviewScore}%</strong></span>
                <span className="text-emerald-400 text-[11px] font-semibold">
                  {avgInterviewScore >= 80 ? 'Strong Hire' : avgInterviewScore >= 70 ? 'Hire' : 'Needs Practice'}
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, avgInterviewScore))}%` }}
                />
              </div>
            </div>
          </div>
          <Link
            to="/mock-interview"
            className="mt-4 flex items-center justify-between text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors pt-3 border-t border-slate-800/80"
          >
            <span>Launch Mock Interview</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Card 2: ATS Improvement (Initial vs Latest) */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-purple-500/40 transition-all shadow-lg flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                ATS Improvement
              </span>
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <FileSearch className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white">{atsScore}</span>
              <span className="text-slate-500 text-sm font-semibold">/ 100</span>
              {atsDelta !== 0 && (
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                    atsDelta > 0
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
                  }`}
                >
                  {atsDelta > 0 ? `+${atsDelta} pts` : `${atsDelta} pts`}
                </span>
              )}
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Initial: {initialAts}</span>
                <span className="text-purple-300 font-semibold">{totalScans} Scans Run</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-purple-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, atsScore))}%` }}
                />
              </div>
            </div>
          </div>
          <Link
            to="/resume-analyzer"
            className="mt-4 flex items-center justify-between text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors pt-3 border-t border-slate-800/80"
          >
            <span>Scan & Optimize Resume</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Card 3: Technical Practice Accuracy */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 transition-all shadow-lg flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Practice Accuracy
              </span>
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Code2 className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white">{practiceAccuracy}%</span>
              <span className="text-slate-500 text-sm font-semibold">Overall</span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>{practiceQuestionsCount} Questions</span>
                <span className="text-cyan-300 font-semibold">{practiceSessionsCount} Sessions</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-cyan-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, practiceAccuracy))}%` }}
                />
              </div>
            </div>
          </div>
          <Link
            to="/practice"
            className="mt-4 flex items-center justify-between text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors pt-3 border-t border-slate-800/80"
          >
            <span>Practice Technical Problems</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Card 4: Completed Roadmap Tasks */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-emerald-500/40 transition-all shadow-lg flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Roadmap Tasks
              </span>
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Milestone className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white">{completedRoadmapTasks}</span>
              <span className="text-slate-500 text-sm font-semibold">/ {totalRoadmapTasks} Done</span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                {roadmapPct}%
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Milestones: {completedMilestones}/{totalMilestones}</span>
                <span className="text-emerald-300 font-semibold truncate max-w-[120px]">{activePhase.split(':')[0]}</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, roadmapPct))}%` }}
                />
              </div>
            </div>
          </div>
          <Link
            to="/roadmap"
            className="mt-4 flex items-center justify-between text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors pt-3 border-t border-slate-800/80"
          >
            <span>View Roadmap Milestones</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* 3. Dedicated PROGRESS & ANALYTICS VIEW (Module 7 Focus) */}
      {activeTab === 'progress' && (
        <div className="space-y-8 animate-fadeIn">
          {/* Section: Weekly Learning Activity Distribution */}
          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-lg font-bold text-white">Weekly Learning Activity (Past 7 Days)</h2>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Multi-dimensional distribution across mock interviews, practice questions, roadmap milestones, and resume scans.
                </p>
              </div>

              {/* Chart Legend */}
              <div className="flex flex-wrap items-center gap-4 text-xs font-medium">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm bg-cyan-500" />
                  <span className="text-slate-300">Practice</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm bg-indigo-500" />
                  <span className="text-slate-300">Interviews</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm bg-emerald-500" />
                  <span className="text-slate-300">Roadmap Tasks</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm bg-purple-500" />
                  <span className="text-slate-300">Resumes</span>
                </div>
              </div>
            </div>

            <div className="h-72 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="practice_count" name="Practice Questions" stackId="a" fill="#06b6d4" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="interviews_count" name="Mock Interviews" stackId="a" fill="#6366f1" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="roadmap_tasks_completed" name="Roadmap Tasks" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="resumes_analyzed" name="Resumes Scanned" stackId="a" fill="#a855f7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Section: Strong Subjects vs Weak Subjects */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Strong Subjects (>= 80% accuracy) */}
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  <h2 className="text-base font-bold text-white">Strong Subjects (≥ 80% Accuracy)</h2>
                </div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
                  {strongSubjects.length} Mastered
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Technical topics where your accuracy, problem-solving, and theoretical understanding are high:
              </p>

              <div className="space-y-3">
                {strongSubjects.length > 0 ? (
                  strongSubjects.map((sub, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl bg-slate-950/70 border border-emerald-500/20 hover:border-emerald-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-slate-200">{sub.subject}</h4>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">
                            {sub.badge}
                          </span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${sub.accuracy}%` }}
                          />
                        </div>
                        <div className="flex items-center justify-between text-[11px] text-slate-400">
                          <span>{sub.questions_attempted} Questions attempted</span>
                          <span className="font-bold text-emerald-400">{sub.accuracy}% Accuracy</span>
                        </div>
                      </div>
                      <Link
                        to={`/practice?subject=${encodeURIComponent(sub.subject)}`}
                        className="shrink-0 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors text-center"
                      >
                        Keep Sharp
                      </Link>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
                    Complete practice sessions with ≥80% accuracy to log your verified strong subjects.
                  </div>
                )}
              </div>
            </div>

            {/* Weak Subjects (< 70% accuracy) */}
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                  <h2 className="text-base font-bold text-white">Weak Subjects (&lt; 70% Accuracy)</h2>
                </div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/25">
                  {weakSubjects.length} Target Areas
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Identified knowledge gaps requiring review and focused problem drilling before upcoming interviews:
              </p>

              <div className="space-y-3">
                {weakSubjects.length > 0 ? (
                  weakSubjects.map((sub, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl bg-slate-950/70 border border-amber-500/20 hover:border-amber-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-slate-200">{sub.subject}</h4>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300">
                            {sub.badge}
                          </span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-amber-500 h-full rounded-full"
                            style={{ width: `${sub.accuracy}%` }}
                          />
                        </div>
                        <div className="flex items-center justify-between text-[11px] text-slate-400">
                          <span className="text-amber-300/90 leading-tight">
                            {sub.recommendation || 'Drill 5 questions to strengthen mastery.'}
                          </span>
                          <span className="font-bold text-amber-400 ml-2">{sub.accuracy}%</span>
                        </div>
                      </div>
                      <Link
                        to={`/practice?subject=${encodeURIComponent(sub.subject)}`}
                        className="shrink-0 px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-300 text-xs font-semibold transition-colors text-center"
                      >
                        Drill Subject
                      </Link>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
                    No critical weak subjects detected. Excellent work maintaining consistent accuracy!
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Section: Interactive Comprehensive History Logs */}
          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-lg font-bold text-white">Historical Logs & Records</h2>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Detailed timeline of past mock interviews, technical practice runs, resume audits, and milestone tasks.
                </p>
              </div>

              {/* Sub-Tabs for History */}
              <div className="flex flex-wrap items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
                <button
                  onClick={() => setActiveHistoryTab('interviews')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeHistoryTab === 'interviews'
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Mock Interviews ({analytics?.interview_history?.length ?? 0})
                </button>
                <button
                  onClick={() => setActiveHistoryTab('practice')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeHistoryTab === 'practice'
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Technical Practice ({analytics?.practice_history?.length ?? 0})
                </button>
                <button
                  onClick={() => setActiveHistoryTab('resumes')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeHistoryTab === 'resumes'
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  ATS Scans ({analytics?.resume_history?.length ?? 0})
                </button>
                <button
                  onClick={() => setActiveHistoryTab('roadmap')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeHistoryTab === 'roadmap'
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Roadmap Milestones ({analytics?.roadmap_progress?.milestones?.length ?? 0})
                </button>
              </div>
            </div>

            {/* History Table Container */}
            <div className="overflow-x-auto">
              {/* Tab 1: Mock Interview History */}
              {activeHistoryTab === 'interviews' && (
                <div className="space-y-3">
                  {analytics?.interview_history && analytics.interview_history.length > 0 ? (
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] font-semibold border-b border-slate-800">
                        <tr>
                          <th className="p-3.5 rounded-l-xl">Role & Session</th>
                          <th className="p-3.5">Date</th>
                          <th className="p-3.5">Technical</th>
                          <th className="p-3.5">Communication</th>
                          <th className="p-3.5">Overall</th>
                          <th className="p-3.5">Verdict</th>
                          <th className="p-3.5 rounded-r-xl text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {analytics.interview_history.map((it) => (
                          <tr key={it.id} className="hover:bg-slate-800/40 transition-colors">
                            <td className="p-3.5 font-semibold text-slate-100">
                              <div className="flex items-center gap-2">
                                <Video className="w-4 h-4 text-indigo-400 shrink-0" />
                                <div>
                                  <div>{it.role}</div>
                                  <div className="text-[10px] text-slate-500 font-normal">
                                    {it.difficulty} • {it.total_questions} Questions
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="p-3.5 text-slate-400">{it.date}</td>
                            <td className="p-3.5 font-bold text-slate-200">{it.technical_score}%</td>
                            <td className="p-3.5 font-bold text-slate-200">{it.communication_score}%</td>
                            <td className="p-3.5 font-extrabold text-indigo-300">{it.overall_score}%</td>
                            <td className="p-3.5">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                  it.verdict === 'Strong Hire'
                                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                                    : it.verdict === 'Hire'
                                    ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/25'
                                    : 'bg-amber-500/15 text-amber-400 border border-amber-500/25'
                                }`}
                              >
                                {it.verdict}
                              </span>
                            </td>
                            <td className="p-3.5 text-right">
                              <Link
                                to="/mock-interview"
                                className="text-indigo-400 hover:text-indigo-300 font-semibold"
                              >
                                View / Retake →
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="p-8 text-center text-slate-500 text-xs">
                      No mock interviews logged yet. Start a session to generate your scorecard!
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Technical Practice History */}
              {activeHistoryTab === 'practice' && (
                <div className="space-y-3">
                  {analytics?.practice_history && analytics.practice_history.length > 0 ? (
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] font-semibold border-b border-slate-800">
                        <tr>
                          <th className="p-3.5 rounded-l-xl">Subject & Role</th>
                          <th className="p-3.5">Difficulty</th>
                          <th className="p-3.5">Questions</th>
                          <th className="p-3.5">Correct</th>
                          <th className="p-3.5">Accuracy</th>
                          <th className="p-3.5">Date</th>
                          <th className="p-3.5 rounded-r-xl text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {analytics.practice_history.map((ps) => (
                          <tr key={ps.id} className="hover:bg-slate-800/40 transition-colors">
                            <td className="p-3.5 font-semibold text-slate-100">
                              <div className="flex items-center gap-2">
                                <Code2 className="w-4 h-4 text-cyan-400 shrink-0" />
                                <div>
                                  <div>{ps.subject}</div>
                                  <div className="text-[10px] text-slate-500 font-normal">{ps.job_role}</div>
                                </div>
                              </div>
                            </td>
                            <td className="p-3.5 text-slate-400">{ps.difficulty}</td>
                            <td className="p-3.5 text-slate-300">{ps.total_questions}</td>
                            <td className="p-3.5 text-slate-300 font-semibold">{ps.correct_count}</td>
                            <td className="p-3.5 font-extrabold text-cyan-300">{ps.accuracy}%</td>
                            <td className="p-3.5 text-slate-400">{ps.date}</td>
                            <td className="p-3.5 text-right">
                              <Link
                                to={`/practice?subject=${encodeURIComponent(ps.subject)}`}
                                className="text-cyan-400 hover:text-cyan-300 font-semibold"
                              >
                                Drill Subject →
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="p-8 text-center text-slate-500 text-xs">
                      No practice sessions logged yet. Start practicing questions in the Question Bank!
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Resume History */}
              {activeHistoryTab === 'resumes' && (
                <div className="space-y-3">
                  {analytics?.resume_history && analytics.resume_history.length > 0 ? (
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] font-semibold border-b border-slate-800">
                        <tr>
                          <th className="p-3.5 rounded-l-xl">Target Job Role</th>
                          <th className="p-3.5">Date</th>
                          <th className="p-3.5">Overall ATS</th>
                          <th className="p-3.5">Keyword Match</th>
                          <th className="p-3.5">Structure</th>
                          <th className="p-3.5">Impact</th>
                          <th className="p-3.5 rounded-r-xl text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {analytics.resume_history.map((r) => (
                          <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                            <td className="p-3.5 font-semibold text-slate-100">
                              <div className="flex items-center gap-2">
                                <FileSearch className="w-4 h-4 text-purple-400 shrink-0" />
                                <span>{r.target_role}</span>
                              </div>
                            </td>
                            <td className="p-3.5 text-slate-400">{r.date}</td>
                            <td className="p-3.5 font-extrabold text-purple-300">{r.ats_score}/100</td>
                            <td className="p-3.5 text-slate-300">{r.keyword_match}%</td>
                            <td className="p-3.5 text-slate-300">{r.structure}%</td>
                            <td className="p-3.5 text-slate-300">{r.impact}%</td>
                            <td className="p-3.5 text-right">
                              <Link
                                to="/resume-analyzer"
                                className="text-purple-400 hover:text-purple-300 font-semibold"
                              >
                                Re-analyze →
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="p-8 text-center text-slate-500 text-xs">
                      No resume scans logged yet. Upload your PDF or DOCX to run an ATS check!
                    </div>
                  )}
                </div>
              )}

              {/* Tab 4: Roadmap Milestones */}
              {activeHistoryTab === 'roadmap' && (
                <div className="space-y-3">
                  {analytics?.roadmap_progress?.milestones && analytics.roadmap_progress.milestones.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {analytics.roadmap_progress.milestones.map((m) => (
                        <div
                          key={m.id}
                          className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3"
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                                Phase {m.phase_number} • {m.duration}
                              </div>
                              <h4 className="text-sm font-bold text-white mt-0.5">{m.title}</h4>
                            </div>
                            <span
                              className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                                m.is_completed
                                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                                  : 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/25'
                              }`}
                            >
                              {m.is_completed ? 'Completed' : 'In Progress'}
                            </span>
                          </div>
                          <div className="space-y-1">
                            <div className="flex justify-between text-xs text-slate-400">
                              <span>Checklist: {m.completed_tasks} / {m.total_tasks} Tasks</span>
                              <span className="font-bold text-emerald-400">{m.phase_progress}%</span>
                            </div>
                            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                              <div
                                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${m.phase_progress}%` }}
                              />
                            </div>
                          </div>
                          <Link
                            to="/roadmap"
                            className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 hover:text-emerald-300"
                          >
                            <span>Open in Roadmap</span>
                            <ChevronRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-500 text-xs">
                      No roadmap milestones generated yet. Generate a personalized roadmap for your career track!
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 4. OVERVIEW DASHBOARD VIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8 animate-fadeIn">
          {/* Quick Action Feature Launchpad */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <Link
              to="/mock-interview"
              className="group p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-indigo-500/40 hover:bg-slate-900/80 transition-all flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0 group-hover:scale-105 transition-transform">
                <Video className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200 group-hover:text-indigo-300 transition-colors">
                  Mock Interview
                </h4>
                <p className="text-xs text-slate-400">Live speech & STAR</p>
              </div>
            </Link>

            <Link
              to="/resume-analyzer"
              className="group p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-purple-500/40 hover:bg-slate-900/80 transition-all flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0 group-hover:scale-105 transition-transform">
                <FileSearch className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200 group-hover:text-purple-300 transition-colors">
                  ATS Analyzer
                </h4>
                <p className="text-xs text-slate-400">Audit keywords</p>
              </div>
            </Link>

            <Link
              to="/resume-builder"
              className="group p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-emerald-500/40 hover:bg-slate-900/80 transition-all flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0 group-hover:scale-105 transition-transform">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200 group-hover:text-emerald-300 transition-colors">
                  Resume Builder
                </h4>
                <p className="text-xs text-slate-400">PDF & DOCX export</p>
              </div>
            </Link>

            <Link
              to="/jd-matcher"
              className="group p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900/80 transition-all flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0 group-hover:scale-105 transition-transform">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200 group-hover:text-cyan-300 transition-colors">
                  JD Matcher
                </h4>
                <p className="text-xs text-slate-400">Compare & gaps</p>
              </div>
            </Link>

            <Link
              to="/roadmap"
              className="group p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-indigo-500/40 hover:bg-slate-900/80 transition-all flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0 group-hover:scale-105 transition-transform">
                <Milestone className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200 group-hover:text-indigo-300 transition-colors">
                  Career Roadmap
                </h4>
                <p className="text-xs text-slate-400">Milestone tasks</p>
              </div>
            </Link>
          </div>

          {/* Weekly Performance Progression & Competency Radar */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-indigo-400" />
                    <h2 className="text-lg font-bold text-slate-100">Weekly Performance Progression</h2>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Sessions logged and score trend over the past 7 days
                  </p>
                </div>
                <div className="flex items-center gap-4 text-xs font-medium">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-indigo-500" />
                    <span className="text-slate-300">Activities</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-emerald-400" />
                    <span className="text-slate-300">Score %</span>
                  </div>
                </div>
              </div>

              <div className="h-64 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={weeklyData}>
                    <defs>
                      <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="sessionGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                    <YAxis yAxisId="left" domain={[0, 100]} stroke="#64748b" fontSize={11} />
                    <YAxis yAxisId="right" orientation="right" domain={[0, 10]} stroke="#64748b" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        borderRadius: '12px',
                        fontSize: '12px',
                      }}
                    />
                    <Area
                      yAxisId="left"
                      type="monotone"
                      dataKey="score"
                      name="Score %"
                      stroke="#10b981"
                      strokeWidth={2.5}
                      fillOpacity={1}
                      fill="url(#scoreGrad)"
                    />
                    <Area
                      yAxisId="right"
                      type="monotone"
                      dataKey="total_activities"
                      name="Activities"
                      stroke="#6366f1"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#sessionGrad)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Radar Chart (Competency Dimensions) */}
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-lg font-bold text-slate-100">Skill Competency Radar</h2>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Live proficiency profile across key software engineering dimensions
                </p>
              </div>

              <div className="h-64 w-full flex items-center justify-center">
                {analytics?.radar_data ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={analytics.radar_data}>
                      <PolarGrid stroke="#334155" />
                      <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={10} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={9} />
                      <Radar
                        name="Candidate Mastery"
                        dataKey="score"
                        stroke="#818cf8"
                        fill="#6366f1"
                        fillOpacity={0.4}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-slate-500 text-xs">Loading competency radar...</div>
                )}
              </div>
            </div>
          </div>

          {/* Skills Needing Improvement & Recent Activities Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Skills Needing Improvement */}
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                  <h2 className="text-base font-bold text-slate-100">Skills That Need Improvement</h2>
                </div>
                <Link
                  to="/practice"
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
                >
                  Drill Concepts →
                </Link>
              </div>

              <p className="text-xs text-slate-400">
                Aggregated by cross-referencing missing resume keywords, question gaps, and interview speech analysis:
              </p>

              <div className="space-y-3">
                {analytics?.skills_needing_improvement && analytics.skills_needing_improvement.length > 0 ? (
                  analytics.skills_needing_improvement.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-slate-700 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-slate-200">{item.skill}</span>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                              item.priority === 'High'
                                ? 'bg-rose-500/15 text-rose-400 border border-rose-500/25'
                                : 'bg-amber-500/15 text-amber-400 border border-amber-500/25'
                            }`}
                          >
                            {item.priority} Priority
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{item.recommendation}</p>
                      </div>
                      <Link
                        to="/practice"
                        className="shrink-0 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold text-center transition-colors"
                      >
                        Practice
                      </Link>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center border border-dashed border-slate-800 rounded-xl text-slate-400 text-xs">
                    No critical gaps identified yet. Great job!
                  </div>
                )}
              </div>
            </div>

            {/* Recent Activities Feed */}
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-base font-bold text-slate-100">Recent Activities</h2>
                </div>
                <span className="text-xs text-slate-500">Live Chronological Feed</span>
              </div>

              <div className="space-y-3">
                {analytics?.recent_activities && analytics.recent_activities.length > 0 ? (
                  analytics.recent_activities.map((act, index) => (
                    <Link
                      key={index}
                      to={act.link}
                      className="group p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 flex items-center justify-between transition-all"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                            act.type === 'interview'
                              ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                              : act.type === 'practice'
                              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                              : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                          }`}
                        >
                          {act.type === 'interview' ? (
                            <Video className="w-4 h-4" />
                          ) : act.type === 'practice' ? (
                            <Code2 className="w-4 h-4" />
                          ) : (
                            <FileSearch className="w-4 h-4" />
                          )}
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors">
                            {act.title}
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5">{act.description}</div>
                        </div>
                      </div>

                      <div className="text-right shrink-0">
                        <div className="text-xs font-bold text-slate-200">{act.score} pts</div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{act.date}</div>
                      </div>
                    </Link>
                  ))
                ) : (
                  <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
                    No recent activity recorded yet. Take an interview or practice a question to start your feed!
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
