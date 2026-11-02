import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import {
  FileCheck,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
  Target,
  Copy,
  Check,
  ExternalLink,
  Layers,
  Briefcase,
  Sliders,
  RefreshCw,
  HelpCircle,
  FileSearch,
} from 'lucide-react';

interface RelevantExperienceItem {
  resume_snippet: string;
  matched_jd_requirement: string;
  relevance_score: number;
}

interface TechnicalSkillGap {
  category: string;
  missing_skills: string[];
  impact: 'Critical' | 'Important' | 'Nice-to-Have';
  recommendation: string;
}

interface JobMatchResult {
  keyword_match_percentage: number;
  overall_fit_score: number;
  matching_skills: string[];
  missing_skills: string[];
  relevant_experience: RelevantExperienceItem[];
  technical_skill_gaps: TechnicalSkillGap[];
  recommendations: string[];
  summary_verdict: string;
  top_keywords_in_jd: string[];
  candidate_strengths: string[];
  disclaimer: string;
}

interface SavedResume {
  id: number;
  title: string;
  target_role?: string;
  created_at: string;
}

const SAMPLE_JOB_DESCRIPTIONS: Record<string, string> = {
  'Senior Backend / Distributed Systems': `We are seeking a Senior Backend Engineer to design, scale, and optimize our core cloud microservices platform.

Key Responsibilities:
• Architect, build, and maintain high-throughput RESTful APIs and distributed microservices using Python, FastAPI, and Docker.
• Design scalable data pipelines and distributed caching layers utilizing Redis and PostgreSQL.
• Collaborate cross-functionally to deploy cloud native services on AWS with CI/CD automation and containerization.
• Ensure 99.99% high availability, system design reliability, and perform unit testing with PyTest.

Requirements:
• 4+ years of professional software engineering experience.
• Strong proficiency in Python, PostgreSQL indexing, Redis caching, and Docker.
• Hands-on experience with Kafka, Kubernetes, and AWS ECS is strongly preferred.
• Passion for clean code, concurrency, and automated test coverage.`,

  'Full Stack Software Engineer': `Looking for a Full Stack Engineer to lead user-facing product features and resilient backend services.

Responsibilities:
• Develop responsive client web applications using React 19, TypeScript, Next.js, and Tailwind CSS.
• Engineer high-performance REST APIs using Node.js or FastAPI with PostgreSQL and Prisma/SQLAlchemy.
• Optimize Core Web Vitals, page latency, state management, and accessibility.
• Participate in code reviews, automated CI/CD deployments with GitHub Actions, and unit testing.

Qualifications:
• 3+ years full stack web engineering experience.
• Proficiency in React, TypeScript, modern CSS frameworks, and relational databases.
• Experience building authenticated RESTful APIs with JWT authentication.`,

  'DevOps & Cloud Infrastructure': `Join our Platform Engineering team as a DevOps Engineer responsible for zero-downtime infrastructure.

Responsibilities:
• Architect automated CI/CD pipelines utilizing GitHub Actions, Docker, and Kubernetes clusters.
• Write Infrastructure as Code (IaC) using Terraform to manage AWS and GCP cloud environments.
• Implement monitoring, telemetry, and alerting with Prometheus, Grafana, and Datadog.
• Enforce zero-trust security policies, container scanning, and network isolation.

Qualifications:
• 3+ years DevOps or Site Reliability experience.
• In-depth Linux systems administration, bash scripting, and Python automation.
• Production experience with Terraform, Kubernetes, Helm, and AWS VPC networking.`,
};

export const JobMatcherPage: React.FC = () => {
  const toast = useToast();
  const [resumeMode, setResumeMode] = useState<'saved' | 'paste'>('saved');
  const [savedResumes, setSavedResumes] = useState<SavedResume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [resumeText, setResumeText] = useState<string>('');
  const [jobDescription, setJobDescription] = useState<string>('');
  const [targetRole, setTargetRole] = useState<string>('Senior Backend Engineer');

  const [isLoadingResumes, setIsLoadingResumes] = useState<boolean>(true);
  const [isMatching, setIsMatching] = useState<boolean>(false);
  const [matchResult, setMatchResult] = useState<JobMatchResult | null>(null);
  const [copiedReport, setCopiedReport] = useState<boolean>(false);

  // Load candidate saved resumes
  useEffect(() => {
    const fetchResumes = async () => {
      try {
        const res = await apiClient.get('/resumes/');
        setSavedResumes(res.data);
        if (res.data.length > 0) {
          setSelectedResumeId(res.data[0].id);
        } else {
          setResumeMode('paste');
        }
      } catch (err) {
        console.error('Failed to fetch resumes:', err);
        setResumeMode('paste');
      } finally {
        setIsLoadingResumes(false);
      }
    };
    fetchResumes();
  }, []);

  // Pre-fill sample JD
  const handleLoadSampleJD = (key: string) => {
    setJobDescription(SAMPLE_JOB_DESCRIPTIONS[key]);
    setTargetRole(key);
    toast.info(`Loaded sample job description: ${key}`);
  };

  // Run Job Matcher
  const handleMatch = async () => {
    if (!jobDescription.trim()) {
      toast.warning('Please paste a job description to compare against your resume.');
      return;
    }
    if (resumeMode === 'paste' && !resumeText.trim()) {
      toast.warning('Please paste your resume content or select a saved resume.');
      return;
    }

    setIsMatching(true);
    try {
      const payload: any = {
        job_description: jobDescription.trim(),
        target_role: targetRole.trim() || 'Software Engineer',
      };

      if (resumeMode === 'saved' && selectedResumeId) {
        payload.resume_id = selectedResumeId;
      } else {
        payload.resume_text = resumeText.trim();
      }

      const res = await apiClient.post('/resumes/match-job-description', payload);
      setMatchResult(res.data);
      toast.success('Job description comparison complete! Gaps analyzed.');
    } catch (err: any) {
      console.error('Job match failed:', err);
      toast.error(err.response?.data?.detail || 'Failed to match job description. Please check your inputs.');
    } finally {
      setIsMatching(false);
    }
  };

  // Copy full Markdown report to clipboard
  const handleCopyReport = () => {
    if (!matchResult) return;
    const report = `# Job Description Match Report: ${targetRole}
**Keyword Match Percentage:** ${matchResult.keyword_match_percentage}%
**Overall Fit Score:** ${matchResult.overall_fit_score}%
**Verdict:** ${matchResult.summary_verdict}

## Matching Skills (${matchResult.matching_skills.length})
${matchResult.matching_skills.join(', ')}

## Missing Skills (${matchResult.missing_skills.length})
${matchResult.missing_skills.join(', ')}

## Technical Skill Gaps
${matchResult.technical_skill_gaps.map((g) => `- [${g.impact}] **${g.category}:** ${g.missing_skills.join(', ')} -> ${g.recommendation}`).join('\n')}

## Relevant Experience Mapped
${matchResult.relevant_experience.map((e) => `### Match Score: ${e.relevance_score}%\n- **Resume Accomplishment:** ${e.resume_snippet}\n- **Satisfies Requirement:** ${e.matched_jd_requirement}\n`).join('\n')}

## Actionable Recommendations
${matchResult.recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n')}
`;
    navigator.clipboard.writeText(report);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 65) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* 1. Page Header */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold mb-2">
              <Target className="w-3.5 h-3.5 text-cyan-400" />
              <span>Module 3: Job Description Matcher</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <FileCheck className="w-7 h-7 text-cyan-400" />
              <span>Job Description Matcher & Gap Auditor</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Paste any external job description to compare it against your resume. Calculate exact keyword match
              percentages, map relevant accomplishment bullets, detect skill gaps, and get prioritized advice.
            </p>
          </div>

          {matchResult && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyReport}
                className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold transition-all flex items-center gap-2 shadow"
              >
                {copiedReport ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied Report!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Copy Full Report</span>
                  </>
                )}
              </button>

              <Link
                to="/resume-builder"
                className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-cyan-600/20"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>Tailor in Builder</span>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* 2. Input Configuration Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Resume Selection & Target Role (5 Cols) */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              1. Candidate Resume Source
            </span>
            <div className="flex rounded-lg bg-slate-950 p-0.5 border border-slate-800 text-[11px]">
              <button
                onClick={() => setResumeMode('saved')}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  resumeMode === 'saved' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Saved Resumes
              </button>
              <button
                onClick={() => setResumeMode('paste')}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  resumeMode === 'paste' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Paste Text
              </button>
            </div>
          </div>

          {resumeMode === 'saved' ? (
            <div className="space-y-2">
              <label className="text-[11px] text-slate-400 block font-medium">Select Saved Resume</label>
              {isLoadingResumes ? (
                <div className="p-4 text-center text-xs text-slate-500 animate-pulse">Loading candidate resumes...</div>
              ) : savedResumes.length > 0 ? (
                <select
                  value={selectedResumeId || ''}
                  onChange={(e) => setSelectedResumeId(Number(e.target.value))}
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  {savedResumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.title} ({r.target_role || 'General'})
                    </option>
                  ))}
                </select>
              ) : (
                <div className="p-4 text-center border border-dashed border-slate-800 rounded-xl text-xs text-slate-400">
                  No saved resumes found. Switch to "Paste Text" or upload one via{' '}
                  <Link to="/resume-analyzer" className="text-cyan-400 underline">
                    Resume Analyzer
                  </Link>
                  .
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-1.5">
              <label className="text-[11px] text-slate-400 block font-medium">Paste Candidate Resume Content</label>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste plain text resume (including experience, skills, projects)..."
                rows={6}
                className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          )}

          <div>
            <label className="text-[11px] text-slate-400 block mb-1 font-medium">Target Job Title</label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Senior Backend Engineer"
              className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Quick Pre-fill Sample JD */}
          <div className="space-y-2 pt-2 border-t border-slate-800/80">
            <span className="text-[11px] font-bold text-slate-400 block">Sample Job Descriptions:</span>
            <div className="flex flex-wrap gap-1.5">
              {Object.keys(SAMPLE_JOB_DESCRIPTIONS).map((key) => (
                <button
                  key={key}
                  onClick={() => handleLoadSampleJD(key)}
                  className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-300 font-medium transition-colors"
                >
                  {key}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Job Description Paste Area & Compare CTA (7 Cols) */}
        <div className="lg:col-span-7 p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              2. Target Job Description
            </span>
            <span className="text-[11px] text-slate-500 font-mono">
              {jobDescription.length} characters • {jobDescription.split(/\s+/).filter(Boolean).length} words
            </span>
          </div>

          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste complete job description, key responsibilities, and requirements here..."
            rows={10}
            className="w-full rounded-2xl bg-slate-950 border border-slate-800 p-4 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed font-sans"
          />

          <button
            onClick={handleMatch}
            disabled={isMatching}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-cyan-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isMatching ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Comparing Resume with Job Description...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-200" />
                <span>Compare Resume & Generate Gap Report</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 3. Comprehensive Match Report Section */}
      {matchResult && (
        <div className="space-y-6">
          {/* Executive Overview Banner */}
          <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 border border-cyan-500/20 shadow-2xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
              <div className="space-y-2">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold">
                  <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Executive Comparison Report</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-black text-white">
                  Match Analysis for {targetRole}
                </h2>
                <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                  {matchResult.summary_verdict}
                </p>
              </div>

              {/* Dual Match Gauges */}
              <div className="flex items-center gap-4 bg-slate-950/80 border border-slate-800 p-4 rounded-2xl shrink-0 shadow-inner">
                <div className="text-center px-3">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    Keyword Match
                  </span>
                  <div className="text-3xl font-black text-cyan-400">
                    {matchResult.keyword_match_percentage}%
                  </div>
                </div>
                <div className="w-px h-10 bg-slate-800" />
                <div className="text-center px-3">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    Overall Fit
                  </span>
                  <div className="text-3xl font-black text-emerald-400">
                    {matchResult.overall_fit_score}%
                  </div>
                </div>
              </div>
            </div>

            {/* Candidate Strengths & Top JD Keywords */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Candidate Verified Strengths</span>
                </h4>
                <ul className="space-y-1 text-xs text-slate-300">
                  {matchResult.candidate_strengths.map((s, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5" />
                  <span>Top Job Description Terms</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {matchResult.top_keywords_in_jd.map((kw, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-medium"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 4. Skills Match & Missing Skills Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Matching Skills */}
            <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span>Matching Skills ({matchResult.matching_skills.length})</span>
                </h3>
                <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  Found in Resume
                </span>
              </div>
              <p className="text-xs text-slate-400">
                These requested skills from the job description are explicitly present in your resume:
              </p>
              <div className="flex flex-wrap gap-2">
                {matchResult.matching_skills.length > 0 ? (
                  matchResult.matching_skills.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{s}</span>
                    </span>
                  ))
                ) : (
                  <div className="text-xs text-slate-500">No direct technical skill matches identified.</div>
                )}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-rose-400" />
                  <span>Missing Skills ({matchResult.missing_skills.length})</span>
                </h3>
                <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
                  Required in JD
                </span>
              </div>
              <p className="text-xs text-slate-400">
                These requirements appear in the job posting but were not detected in your resume:
              </p>
              <div className="flex flex-wrap gap-2">
                {matchResult.missing_skills.length > 0 ? (
                  matchResult.missing_skills.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs font-semibold"
                    >
                      + {s}
                    </span>
                  ))
                ) : (
                  <div className="text-xs text-emerald-400">All target skills detected in your resume!</div>
                )}
              </div>
            </div>
          </div>

          {/* 5. Categorized Technical Skill Gaps */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="w-5 h-5 text-amber-400" />
                <span>Technical Skill Gaps by Category</span>
              </h3>
              <span className="text-xs text-slate-400">Prioritized for preparation</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {matchResult.technical_skill_gaps.map((gap, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 space-y-2 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200">{gap.category}</span>
                    <span
                      className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                        gap.impact === 'Critical'
                          ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                          : gap.impact === 'Important'
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30'
                      }`}
                    >
                      {gap.impact}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1.5">
                    {gap.missing_skills.map((s, sIdx) => (
                      <span
                        key={sIdx}
                        className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono"
                      >
                        {s}
                      </span>
                    ))}
                  </div>

                  <p className="text-[11px] text-slate-400 leading-relaxed pt-1 border-t border-slate-800/60">
                    <span className="font-semibold text-slate-300">Action: </span>
                    {gap.recommendation}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* 6. Relevant Experience Mapping (Side-by-Side Snippets) */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-indigo-400" />
                  <span>Relevant Experience Mapping</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Direct alignment between your actual resume accomplishments and the employer's requirements:
                </p>
              </div>
              <span className="text-xs text-indigo-400 font-semibold hidden sm:block">
                ATS Semantic Pairing
              </span>
            </div>

            <div className="space-y-3">
              {matchResult.relevant_experience.map((item, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 space-y-3"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-300">Mapping #{idx + 1}</span>
                    <span
                      className={`font-black px-2 py-0.5 rounded-md text-[11px] ${getScoreColor(
                        item.relevance_score
                      )}`}
                    >
                      {item.relevance_score}% Relevance Match
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    {/* JD Requirement */}
                    <div className="p-3 rounded-xl bg-slate-900/90 border border-cyan-500/20 space-y-1">
                      <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block">
                        Employer Job Requirement
                      </span>
                      <p className="text-slate-200 leading-relaxed">{item.matched_jd_requirement}</p>
                    </div>

                    {/* Resume Accomplishment */}
                    <div className="p-3 rounded-xl bg-slate-900/90 border border-emerald-500/20 space-y-1">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">
                        Candidate Verified Accomplishment
                      </span>
                      <p className="text-emerald-100 leading-relaxed">{item.resume_snippet}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 7. Actionable Strategic Recommendations */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span>Personalized Recommendations to Win the Interview</span>
            </h3>

            <div className="space-y-2.5">
              {matchResult.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-3"
                >
                  <span className="w-5 h-5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{rec}</span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
              <span>{matchResult.disclaimer}</span>
              <button
                onClick={handleCopyReport}
                className="text-cyan-400 hover:text-cyan-300 font-semibold transition-colors shrink-0 ml-4"
              >
                Copy Full Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobMatcherPage;
