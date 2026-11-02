import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Link } from 'react-router-dom';
import {
  Video,
  Award,
  Calendar,
  Clock,
  Download,
  Eye,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Search,
  Filter,
  ShieldCheck,
  Sparkles,
  ChevronRight,
  X,
  FileText,
  Volume2,
} from 'lucide-react';
import { TableSkeleton } from '../components/Skeleton';
import { useToast } from '../context/ToastContext';

interface QuestionFeedback {
  id: number;
  question_order: number;
  question_text: string;
  candidate_answer: string;
  score: number;
  technical_accuracy: number;
  feedback: string;
  wpm?: number;
  filler_words?: Record<string, number>;
}

interface InterviewSessionItem {
  id: number;
  session_number?: string;
  role: string;
  role_title?: string;
  interview_type: string;
  difficulty: string;
  date: string;
  created_at?: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  verdict: string;
  duration_seconds: number;
  total_questions: number;
  overall_summary?: string;
  key_strengths?: string[];
  areas_to_improve?: string[];
  improvement_plan?: string[];
  questions?: QuestionFeedback[];
}

export const InterviewHistoryPage: React.FC = () => {
  const [sessions, setSessions] = useState<InterviewSessionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [verdictFilter, setVerdictFilter] = useState<string>('All');
  const [selectedSession, setSelectedSession] = useState<InterviewSessionItem | null>(null);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const toast = useToast();

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/analytics/dashboard');
      const interviewHistory: InterviewSessionItem[] = res.data.interview_history || [];
      setSessions(interviewHistory);
    } catch (err) {
      console.error('Failed to load interview history:', err);
      toast.error('Could not load interview history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDownloadPdf = async (sessionId: number, role: string) => {
    try {
      setDownloadingId(sessionId);
      const res = await apiClient.get(`/interviews/${sessionId}/report-pdf`, {
        responseType: 'blob',
      });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Interview_Scorecard_${role.replace(/\s+/g, '_')}_#${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('Official PDF scorecard downloaded successfully!');
    } catch (err) {
      console.error('PDF download failed:', err);
      toast.error('Failed to download PDF scorecard. Please ensure the session is completed.');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleOpenScorecard = async (session: InterviewSessionItem) => {
    setSelectedSession(session);
    try {
      // Fetch full detailed scorecard if available
      const res = await apiClient.get(`/interviews/${session.id}`);
      setSelectedSession((prev) => ({
        ...prev,
        ...res.data,
        role: res.data.role_title || session.role,
      }));
    } catch {
      // Keep basic info
    }
  };

  const filteredSessions = sessions.filter((s) => {
    const matchesSearch =
      s.role.toLowerCase().includes(search.toLowerCase()) ||
      s.interview_type.toLowerCase().includes(search.toLowerCase()) ||
      (s.verdict && s.verdict.toLowerCase().includes(search.toLowerCase()));

    const matchesVerdict =
      verdictFilter === 'All' ||
      (verdictFilter === 'Strong Hire' && s.verdict === 'Strong Hire') ||
      (verdictFilter === 'Hire' && s.verdict === 'Hire') ||
      (verdictFilter === 'Needs Improvement' && (s.verdict === 'Needs Improvement' || s.verdict === 'Lean Hire'));

    return matchesSearch && matchesVerdict;
  });

  const totalSessions = sessions.length;
  const avgOverall =
    totalSessions > 0
      ? Math.round(sessions.reduce((acc, s) => acc + (s.overall_score || 0), 0) / totalSessions)
      : 0;
  const avgTech =
    totalSessions > 0
      ? Math.round(sessions.reduce((acc, s) => acc + (s.technical_score || 0), 0) / totalSessions)
      : 0;
  const avgComm =
    totalSessions > 0
      ? Math.round(sessions.reduce((acc, s) => acc + (s.communication_score || 0), 0) / totalSessions)
      : 0;

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* 1. Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
            <Video className="w-3.5 h-3.5 text-indigo-400" />
            <span>Interview Records & Scorecards</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Interview History
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Review detailed multi-dimensional interview feedback, STAR method responses, speech metrics, and download official PDF scorecards.
          </p>
        </div>

        <Link
          to="/mock-interview"
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/20 flex items-center gap-2 shrink-0 self-start md:self-auto"
        >
          <Sparkles className="w-4 h-4" />
          <span>Start New Interview</span>
        </Link>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Mock Sessions</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{totalSessions}</span>
            <span className="text-slate-500 text-xs">Evaluated</span>
          </div>
          <div className="text-[11px] text-slate-400">Audio & Video speech metrics logged</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Overall Score</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-indigo-400">{avgOverall}%</span>
            <span className="text-slate-500 text-xs">Target: 85%+</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${avgOverall}%` }} />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Technical Score</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-cyan-400">{avgTech}%</span>
            <span className="text-slate-500 text-xs">Engineering</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-cyan-500 h-full rounded-full" style={{ width: `${avgTech}%` }} />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Communication</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-emerald-400">{avgComm}%</span>
            <span className="text-slate-500 text-xs">Pacing & Clarity</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${avgComm}%` }} />
          </div>
        </div>
      </div>

      {/* 3. Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by role, verdict, or type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 shrink-0">
            <Filter className="w-3.5 h-3.5" />
            Verdict:
          </span>
          {['All', 'Strong Hire', 'Hire', 'Needs Improvement'].map((v) => (
            <button
              key={v}
              onClick={() => setVerdictFilter(v)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold shrink-0 transition-all ${
                verdictFilter === v
                  ? 'bg-indigo-600 text-white shadow'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {/* 4. Sessions History Table */}
      {loading ? (
        <TableSkeleton rows={5} />
      ) : filteredSessions.length > 0 ? (
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3.5 rounded-l-xl">Role & Focus Track</th>
                <th className="p-3.5">Date</th>
                <th className="p-3.5">Difficulty</th>
                <th className="p-3.5">Technical</th>
                <th className="p-3.5">Communication</th>
                <th className="p-3.5">Overall</th>
                <th className="p-3.5">Verdict</th>
                <th className="p-3.5 rounded-r-xl text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredSessions.map((session) => (
                <tr key={session.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-semibold text-slate-100">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
                        <Video className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-bold text-slate-200">{session.role}</div>
                        <div className="text-[10px] text-slate-400 font-normal">
                          {session.interview_type} • {session.total_questions} Questions
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="p-3.5 text-slate-400">{session.date}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                      {session.difficulty}
                    </span>
                  </td>
                  <td className="p-3.5 font-bold text-cyan-300">{session.technical_score}%</td>
                  <td className="p-3.5 font-bold text-emerald-300">{session.communication_score}%</td>
                  <td className="p-3.5 font-extrabold text-indigo-400 text-sm">
                    {session.overall_score}%
                  </td>
                  <td className="p-3.5">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        session.verdict === 'Strong Hire'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                          : session.verdict === 'Hire'
                          ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/25'
                          : 'bg-amber-500/15 text-amber-400 border border-amber-500/25'
                      }`}
                    >
                      {session.verdict}
                    </span>
                  </td>
                  <td className="p-3.5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleOpenScorecard(session)}
                        className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-semibold flex items-center gap-1 transition-colors"
                        title="View Full Scorecard"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Review</span>
                      </button>

                      <button
                        onClick={() => handleDownloadPdf(session.id, session.role)}
                        disabled={downloadingId === session.id}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        title="Download PDF Scorecard"
                      >
                        <Download className={`w-3.5 h-3.5 ${downloadingId === session.id ? 'animate-spin' : ''}`} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-12 text-center rounded-3xl bg-slate-900/60 border border-dashed border-slate-800 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <Video className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">No Mock Interviews Found</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Simulate realistic technical and behavioral interviews with dynamic follow-ups, recording analytics, and speech metrics.
            </p>
          </div>
          <Link
            to="/mock-interview"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch First Mock Interview</span>
          </Link>
        </div>
      )}

      {/* 5. Detailed Scorecard Modal */}
      {selectedSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-3xl max-h-[85vh] overflow-y-auto p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-6 animate-scaleUp">
            <button
              onClick={() => setSelectedSession(null)}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Modal Header */}
            <div className="space-y-1 pr-8">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                  Session #{selectedSession.id} Evaluation Report
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    selectedSession.verdict === 'Strong Hire'
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                      : selectedSession.verdict === 'Hire'
                      ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/25'
                      : 'bg-amber-500/15 text-amber-400 border border-amber-500/25'
                  }`}
                >
                  {selectedSession.verdict}
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-white">{selectedSession.role}</h2>
              <p className="text-xs text-slate-400">
                Conducted on {selectedSession.date} • Duration: {Math.round(selectedSession.duration_seconds / 60)} mins
              </p>
            </div>

            {/* Score Grid */}
            <div className="grid grid-cols-3 gap-3 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-center">
              <div>
                <span className="text-[11px] text-slate-400 uppercase font-semibold">Technical</span>
                <div className="text-2xl font-black text-cyan-400 mt-1">{selectedSession.technical_score}%</div>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 uppercase font-semibold">Communication</span>
                <div className="text-2xl font-black text-emerald-400 mt-1">{selectedSession.communication_score}%</div>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 uppercase font-semibold">Overall Composite</span>
                <div className="text-2xl font-black text-indigo-400 mt-1">{selectedSession.overall_score}%</div>
              </div>
            </div>

            {/* Qualitative Executive Summary */}
            {selectedSession.overall_summary && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Executive Interviewer Assessment
                </h4>
                <p className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                  {selectedSession.overall_summary}
                </p>
              </div>
            )}

            {/* Improvement Plan */}
            {selectedSession.improvement_plan && selectedSession.improvement_plan.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  4-Step Candidate Improvement Plan
                </h4>
                <div className="space-y-2">
                  {selectedSession.improvement_plan.map((step, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300"
                    >
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions at bottom */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <button
                onClick={() => handleDownloadPdf(selectedSession.id, selectedSession.role)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Download PDF Report</span>
              </button>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setSelectedSession(null)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Close
                </button>
                <Link
                  to="/mock-interview"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md"
                >
                  Retake Interview
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewHistoryPage;
