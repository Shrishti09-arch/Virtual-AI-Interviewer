import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import {
  Milestone,
  CheckCircle2,
  Circle,
  FolderGit2,
  BookOpen,
  Sparkles,
  Calendar,
  Layers,
  ArrowRight,
  Clock,
  Target,
  GraduationCap,
  CheckSquare,
  Square,
  ExternalLink,
  Code2,
  Plus,
  Trash2,
  HelpCircle,
  TrendingUp,
  Award,
  Zap,
  Sliders,
  Check,
  ChevronDown,
  ChevronUp,
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
  'Cloud Engineer',
  'DevOps Engineer',
  'Cybersecurity Engineer',
];

const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced'];

const EDUCATION_OPTIONS = [
  'Computer Science Degree',
  'STEM Degree (Engineering / Math)',
  'Bootcamp Graduate',
  'Self-Taught Developer',
  'Non-Tech Degree / Career Changer',
  "Master's / PhD",
];

const STUDY_HOURS_OPTIONS = [
  { value: 1.0, label: '1 hour/day (~7 hrs/week • Relaxed)' },
  { value: 2.0, label: '2 hours/day (~14 hrs/week • Steady Standard)' },
  { value: 3.0, label: '3 hours/day (~21 hrs/week • Intensive)' },
  { value: 4.0, label: '4 hours/day (~28 hrs/week • Accelerated Bootcamp)' },
  { value: 6.0, label: '6+ hours/day (~42+ hrs/week • Full-Time Immersion)' },
];

const CAREER_GOALS = [
  'Land First Professional Software Role',
  'Mid-Level to Senior Promotion',
  'Transition into Applied AI / Machine Learning',
  'FAANG / Tier-1 Tech Switch',
  'Transition from Non-Tech / Support to Engineering',
];

const COMMON_SKILL_TAGS = [
  'Python',
  'JavaScript',
  'TypeScript',
  'React',
  'FastAPI',
  'Node.js',
  'SQL / PostgreSQL',
  'Git / GitHub',
  'Docker',
  'Data Structures & Algorithms',
  'System Design',
  'AWS',
];

interface ChecklistItem {
  id: string;
  task: string;
  is_done: boolean;
}

interface MilestonePhase {
  id: number;
  roadmap_id: number;
  phase_number: number;
  title: string;
  duration: string;
  estimated_hours: number;
  objectives: string[];
  topics: string[];
  practice_tasks: string[];
  recommended_projects: Array<{
    name: string;
    description: string;
    tech_stack: string[];
  }>;
  learning_resources: Array<{
    title: string;
    type: string;
    link: string;
  }>;
  interview_questions: string[];
  checklist: ChecklistItem[];
  phase_progress: number;
  is_completed: boolean;
}

interface CareerRoadmapData {
  id: number;
  target_role: string;
  current_level: string;
  education: string;
  existing_skills: string[];
  daily_study_hours: number;
  career_goal: string;
  timeline_months: number;
  overview: string;
  key_focus_areas: string[];
  daily_study_plan: {
    total_daily_minutes?: number;
    routine?: Array<{ block: string; duration: string; activity: string }>;
    recommendation?: string;
  };
  weekly_targets: string[];
  overall_progress: number;
  total_tasks: number;
  completed_tasks: number;
  milestones: MilestonePhase[];
  created_at: string;
}

export const RoadmapPage: React.FC = () => {
  const { user } = useAuth();
  const toast = useToast();
  const [roadmaps, setRoadmaps] = useState<CareerRoadmapData[]>([]);
  const [activeRoadmap, setActiveRoadmap] = useState<CareerRoadmapData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showConfigModal, setShowConfigModal] = useState<boolean>(false);

  // Roadmap Setup Form State
  const [formRole, setFormRole] = useState<string>(user?.role_target || 'Full Stack Developer');
  const [formLevel, setFormLevel] = useState<string>('Beginner');
  const [formEducation, setFormEducation] = useState<string>('Computer Science Degree');
  const [formExistingSkills, setFormExistingSkills] = useState<string[]>(['JavaScript', 'HTML/CSS']);
  const [formDailyHours, setFormDailyHours] = useState<number>(2.0);
  const [formGoal, setFormGoal] = useState<string>('Land First Professional Software Role');
  const [formTimelineMonths, setFormTimelineMonths] = useState<number>(6);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  // Accordion Expand/Collapse for Phases
  const [expandedPhases, setExpandedPhases] = useState<Record<number, boolean>>({});

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  const fetchRoadmaps = async () => {
    try {
      const res = await apiClient.get('/roadmaps/');
      setRoadmaps(res.data);
      if (res.data.length > 0) {
        setActiveRoadmap(res.data[0]);
        // Expand phase 1 by default
        setExpandedPhases({ 1: true });
      } else {
        setShowConfigModal(true);
      }
    } catch (err) {
      console.error('Failed to load roadmaps:', err);
    } finally {
      setLoading(false);
    }
  };

  // Generate New Roadmap
  const handleGenerateRoadmap = async () => {
    setIsGenerating(true);
    try {
      const res = await apiClient.post('/roadmaps/generate', {
        target_role: formRole,
        current_level: formLevel,
        education: formEducation,
        existing_skills: formExistingSkills,
        daily_study_hours: formDailyHours,
        career_goal: formGoal,
        timeline_months: formTimelineMonths,
      });

      setRoadmaps([res.data, ...roadmaps]);
      setActiveRoadmap(res.data);
      setShowConfigModal(false);
      setExpandedPhases({ 1: true, 2: false, 3: false, 4: false });
      toast.success('Dynamic career roadmap generated!');
    } catch (err) {
      console.error('Failed to generate roadmap:', err);
      toast.error('Error generating career roadmap. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Toggle Interactive Checklist Task
  const handleToggleTask = async (milestoneId: number, taskId: string, currentStatus: boolean) => {
    if (!activeRoadmap) return;

    try {
      const res = await apiClient.put(`/roadmaps/${activeRoadmap.id}/milestones/${milestoneId}/task`, {
        task_id: taskId,
        is_done: !currentStatus,
      });

      // Update active roadmap in local state with recalculated progress
      setActiveRoadmap((prev) => {
        if (!prev) return null;
        const updatedMilestones = prev.milestones.map((m) => {
          if (m.id === milestoneId) {
            const updatedChecklist = m.checklist.map((item) =>
              item.id === taskId ? { ...item, is_done: !currentStatus } : item
            );
            return {
              ...m,
              checklist: updatedChecklist,
              phase_progress: res.data.phase_progress,
              is_completed: res.data.milestone_completed,
            };
          }
          return m;
        });

        return {
          ...prev,
          overall_progress: res.data.overall_progress,
          completed_tasks: res.data.completed_tasks,
          total_tasks: res.data.total_tasks,
          milestones: updatedMilestones,
        };
      });

      // Also update in list
      setRoadmaps((prevList) =>
        prevList.map((r) =>
          r.id === activeRoadmap.id
            ? {
                ...r,
                overall_progress: res.data.overall_progress,
                completed_tasks: res.data.completed_tasks,
              }
            : r
        )
      );
    } catch (err) {
      console.error('Failed to toggle task:', err);
    }
  };

  // Toggle Phase Accordion
  const togglePhaseExpansion = (phaseNumber: number) => {
    setExpandedPhases((prev) => ({
      ...prev,
      [phaseNumber]: !prev[phaseNumber],
    }));
  };

  // Toggle skill tag in form
  const toggleSkillTag = (skill: string) => {
    if (formExistingSkills.includes(skill)) {
      setFormExistingSkills(formExistingSkills.filter((s) => s !== skill));
    } else {
      setFormExistingSkills([...formExistingSkills, skill]);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-black text-slate-100 flex items-center gap-2.5">
            <Target className="w-7 h-7 text-cyan-400" />
            <span>AI Dynamic Career Roadmap & Study Architect</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Personalized milestones, daily routines, curated free resources, portfolio capstones, and interactive progress tracking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {roadmaps.length > 0 && (
            <select
              value={activeRoadmap?.id || ''}
              onChange={(e) => {
                const found = roadmaps.find((r) => r.id === Number(e.target.value));
                if (found) {
                  setActiveRoadmap(found);
                  setExpandedPhases({ 1: true });
                }
              }}
              className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              {roadmaps.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.target_role} ({r.overall_progress}% Done)
                </option>
              ))}
            </select>
          )}

          <button
            onClick={() => setShowConfigModal(true)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg transition-all hover:scale-[1.01]"
          >
            <Plus className="w-4 h-4" />
            <span>New Custom Roadmap</span>
          </button>
        </div>
      </div>

      {/* ROADMAP CONFIGURATION MODAL / DRAWER */}
      {showConfigModal && (
        <div className="p-6 md:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-lg font-black text-slate-100 flex items-center gap-2">
                <Sliders className="w-5 h-5 text-cyan-400" />
                <span>Architect Your Career Blueprint</span>
              </h2>
              <p className="text-xs text-slate-400">
                Input your daily hours and background to calculate tailored study durations and skip redundant topics.
              </p>
            </div>
            {roadmaps.length > 0 && (
              <button
                onClick={() => setShowConfigModal(false)}
                className="text-xs text-slate-400 hover:text-slate-200 font-bold"
              >
                Cancel
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Target Role */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Target Job Role</label>
              <select
                value={formRole}
                onChange={(e) => setFormRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {SUPPORTED_ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            {/* Current Level */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Current Skill Level</label>
              <select
                value={formLevel}
                onChange={(e) => setFormLevel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {SKILL_LEVELS.map((lvl) => (
                  <option key={lvl} value={lvl}>{lvl}</option>
                ))}
              </select>
            </div>

            {/* Education Background */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Education</label>
              <select
                value={formEducation}
                onChange={(e) => setFormEducation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {EDUCATION_OPTIONS.map((edu) => (
                  <option key={edu} value={edu}>{edu}</option>
                ))}
              </select>
            </div>

            {/* Daily Study Hours */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>Daily Study Commitment</span>
              </label>
              <select
                value={formDailyHours}
                onChange={(e) => setFormDailyHours(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {STUDY_HOURS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* Primary Career Goal */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Career Milestone Goal</label>
              <select
                value={formGoal}
                onChange={(e) => setFormGoal(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {CAREER_GOALS.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>

            {/* Timeline Horizon */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Timeline Horizon</label>
              <select
                value={formTimelineMonths}
                onChange={(e) => setFormTimelineMonths(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value={3}>3 Months (Rapid Sprint)</option>
                <option value={6}>6 Months (Standard Transition)</option>
                <option value={9}>9 Months (Deep Mastery)</option>
                <option value={12}>12 Months (Comprehensive Zero-to-Hire)</option>
              </select>
            </div>
          </div>

          {/* Existing Skills Selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Existing Skills You Already Know (Roadmap will bypass fundamentals):
            </label>
            <div className="flex flex-wrap gap-2">
              {COMMON_SKILL_TAGS.map((skill) => {
                const isSelected = formExistingSkills.includes(skill);
                return (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => toggleSkillTag(skill)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
                      isSelected
                        ? 'bg-cyan-600/20 text-cyan-300 border-cyan-500/50 shadow-sm'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {skill} {isSelected && '✓'}
                  </button>
                );
              })}
            </div>
          </div>

          <button
            onClick={handleGenerateRoadmap}
            disabled={isGenerating}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-black text-sm flex items-center justify-center gap-2.5 shadow-xl shadow-cyan-600/20 disabled:opacity-50 transition-all hover:scale-[1.01]"
          >
            {isGenerating ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Synthesizing Dynamic Roadmap & Weekly Targets...
              </span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Dynamic AI Career Roadmap</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* ACTIVE ROADMAP DASHBOARD */}
      {activeRoadmap && !showConfigModal && (
        <div className="space-y-6">
          {/* Executive Overview & Progress Card */}
          <div className="p-6 md:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-bold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    {activeRoadmap.target_role}
                  </span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs text-slate-300 font-semibold">{activeRoadmap.current_level}</span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs text-slate-400">{activeRoadmap.daily_study_hours} hrs/day commitment</span>
                </div>
                <h2 className="text-xl font-black text-slate-100 mt-2">{activeRoadmap.career_goal}</h2>
                <p className="text-xs text-slate-300 mt-1.5 leading-relaxed max-w-3xl">
                  {activeRoadmap.overview}
                </p>
              </div>

              {/* Overall Progress Gauge */}
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-right min-w-[200px]">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Overall Roadmap Progress</div>
                <div className="text-3xl font-black text-cyan-400 mt-1">{activeRoadmap.overall_progress}%</div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  {activeRoadmap.completed_tasks} of {activeRoadmap.total_tasks} Action Items Done
                </div>
              </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
              <div
                className="bg-gradient-to-r from-cyan-500 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${activeRoadmap.overall_progress}%` }}
              />
            </div>

            {/* Daily Routine Schedule & Weekly Targets (Side-by-Side) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 pt-2">
              {/* Daily Study Routine */}
              <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-slate-200 uppercase tracking-wider">
                  <span className="flex items-center gap-1.5 text-cyan-400">
                    <Clock className="w-4 h-4" />
                    <span>Daily Study Schedule ({activeRoadmap.daily_study_plan?.total_daily_minutes || 120} mins)</span>
                  </span>
                </div>

                <div className="space-y-2">
                  {activeRoadmap.daily_study_plan?.routine?.map((block, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-slate-200">
                        <span>{block.block}</span>
                        <span className="text-cyan-400 font-mono text-[11px]">{block.duration}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed">{block.activity}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Weekly Targets & Milestones */}
              <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 text-indigo-400">
                  <Calendar className="w-4 h-4" />
                  <span>Key Weekly Checkpoints & Milestones</span>
                </div>

                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {activeRoadmap.weekly_targets?.map((target, idx) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 leading-relaxed flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                      <span>{target}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 4 PHASES CURRICULUM WITH ACCORDIONS */}
          <div className="space-y-5">
            <h3 className="text-sm font-black text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>Phased Milestone Curriculum & Completion Checklists</span>
            </h3>

            {activeRoadmap.milestones?.map((phase) => {
              const isExpanded = expandedPhases[phase.phase_number] ?? false;

              return (
                <div
                  key={phase.id}
                  className={`rounded-3xl border transition-all duration-300 overflow-hidden ${
                    phase.is_completed
                      ? 'bg-slate-900/90 border-emerald-500/40 shadow-lg shadow-emerald-950/20'
                      : 'bg-slate-900 border-slate-800 shadow-xl'
                  }`}
                >
                  {/* Phase Header Banner (Click to toggle accordion) */}
                  <div
                    onClick={() => togglePhaseExpansion(phase.phase_number)}
                    className="p-5 md:p-6 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-9 h-9 rounded-2xl flex items-center justify-center font-black text-sm border ${
                          phase.is_completed
                            ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                            : 'bg-slate-800 border-slate-700 text-cyan-400'
                        }`}
                      >
                        {phase.is_completed ? <Check className="w-5 h-5" /> : `P${phase.phase_number}`}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-base font-bold text-slate-100">{phase.title}</h4>
                          {phase.is_completed && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                              Phase Completed
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5 font-mono">
                          <span>{phase.duration}</span>
                          <span>•</span>
                          <span>{phase.estimated_hours} Estimated Hours</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      {/* Mini Phase Progress */}
                      <div className="w-32 text-right">
                        <div className="text-[11px] font-bold text-slate-300">{phase.phase_progress}%</div>
                        <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800 mt-1">
                          <div
                            className="bg-cyan-500 h-full rounded-full transition-all"
                            style={{ width: `${phase.phase_progress}%` }}
                          />
                        </div>
                      </div>

                      <div className="text-slate-400">
                        {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Accordion Body */}
                  {isExpanded && (
                    <div className="p-6 md:p-8 pt-0 border-t border-slate-800/60 space-y-6">
                      {/* 1. Topics Tags */}
                      <div className="space-y-2 pt-4">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Curriculum Topics to Master:</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {phase.topics?.map((topic, i) => (
                            <span
                              key={i}
                              className="px-3 py-1 rounded-xl text-xs font-medium bg-slate-950 text-slate-200 border border-slate-800"
                            >
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* 2. Portfolio Project Card & Hands-On Practice Tasks */}
                      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                        {/* Recommended Project */}
                        <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                          <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                            <FolderGit2 className="w-4 h-4" />
                            <span>Recommended Portfolio Project</span>
                          </div>

                          {phase.recommended_projects?.map((proj, pIdx) => (
                            <div key={pIdx} className="space-y-2">
                              <h5 className="text-sm font-bold text-slate-100">{proj.name}</h5>
                              <p className="text-xs text-slate-300 leading-relaxed">{proj.description}</p>
                              <div className="flex flex-wrap gap-1.5 pt-1">
                                {proj.tech_stack?.map((tech, tIdx) => (
                                  <span
                                    key={tIdx}
                                    className="text-[10px] px-2 py-0.5 rounded-lg bg-indigo-950/60 text-indigo-300 border border-indigo-800"
                                  >
                                    {tech}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Hands-On Practice Tasks */}
                        <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                          <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                            <Zap className="w-4 h-4" />
                            <span>Hands-On Implementation Tasks</span>
                          </div>

                          <ul className="space-y-2 text-xs text-slate-300">
                            {phase.practice_tasks?.map((task, tIdx) => (
                              <li key={tIdx} className="flex items-start gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                                <span>{task}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* 3. Verified Free Educational Resources & Interview Questions */}
                      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                        {/* Free Educational Resources */}
                        <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                          <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                            <BookOpen className="w-4 h-4" />
                            <span>Verified Free Learning Resources</span>
                          </div>

                          <div className="space-y-2">
                            {phase.learning_resources?.map((res, rIdx) => (
                              <a
                                key={rIdx}
                                href={res.link}
                                target="_blank"
                                rel="noreferrer"
                                className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/60 flex items-center justify-between text-xs transition-all group"
                              >
                                <div>
                                  <div className="font-bold text-slate-200 group-hover:text-cyan-300">{res.title}</div>
                                  <span className="text-[10px] text-slate-400 font-mono">{res.type}</span>
                                </div>
                                <ExternalLink className="w-4 h-4 text-slate-500 group-hover:text-cyan-400" />
                              </a>
                            ))}
                          </div>
                        </div>

                        {/* Top Interview Questions */}
                        <div className="lg:col-span-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                          <div className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                            <HelpCircle className="w-4 h-4" />
                            <span>Core Phase Interview Questions</span>
                          </div>

                          <div className="space-y-2">
                            {phase.interview_questions?.map((q, qIdx) => (
                              <div
                                key={qIdx}
                                className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans"
                              >
                                <strong>Q{qIdx + 1}: </strong> {q}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* 4. Actionable Interactive Checklist */}
                      <div className="p-6 rounded-2xl bg-slate-950 border border-cyan-500/30 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                            <CheckSquare className="w-4 h-4 text-cyan-400" />
                            <span>Actionable Completion Checklist (Click to check off tasks)</span>
                          </div>
                          <span className="text-[11px] font-mono text-cyan-400">
                            {phase.checklist?.filter((c) => c.is_done).length} of {phase.checklist?.length} Completed
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-1">
                          {phase.checklist?.map((item) => (
                            <button
                              key={item.id}
                              onClick={() => handleToggleTask(phase.id, item.id, item.is_done)}
                              className={`p-3 rounded-xl border text-left text-xs font-medium flex items-center gap-3 transition-all ${
                                item.is_done
                                  ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200 line-through'
                                  : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/60'
                              }`}
                            >
                              <div
                                className={`w-5 h-5 rounded-lg border flex items-center justify-center shrink-0 ${
                                  item.is_done
                                    ? 'bg-emerald-500 border-emerald-400 text-black'
                                    : 'border-slate-600 bg-slate-950'
                                }`}
                              >
                                {item.is_done && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                              </div>
                              <span className="leading-snug">{item.task}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
