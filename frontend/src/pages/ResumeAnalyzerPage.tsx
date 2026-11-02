import React, { useState } from 'react';
import apiClient from '../api/client';
import { useToast } from '../context/ToastContext';
import {
  FileSearch,
  UploadCloud,
  FileText,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Sparkles,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
  Edit3,
  Save,
  Check,
  X,
  RefreshCw,
  Download,
  Info,
  CheckCheck,
  Award,
  GraduationCap,
  Briefcase,
  Code,
  BookmarkCheck,
  ExternalLink,
  HelpCircle,
  Layers,
  Sliders,
} from 'lucide-react';

interface ExtractedData {
  full_name: string;
  email: string;
  phone: string;
  location?: string;
  linkedin?: string;
  github?: string;
  summary?: string;
  education: Array<{
    institution: string;
    degree: string;
    year?: string;
    grade?: string;
  }>;
  technical_skills: Record<string, string[]>;
  work_experience: Array<{
    company: string;
    role: string;
    duration: string;
    location?: string;
    highlights: string[];
  }>;
  internships: Array<{
    company: string;
    role: string;
    duration: string;
    highlights: string[];
  }>;
  projects: Array<{
    name: string;
    technologies: string[];
    description: string;
    link?: string;
  }>;
  certifications: string[];
  achievements: string[];
}

interface CorrectionItem {
  id: string;
  category: string;
  original: string;
  corrected: string;
  explanation: string;
  status: 'pending' | 'accepted' | 'rejected';
}

interface ATSAnalysis {
  id: number;
  resume_id: number;
  target_role: string;
  overall_ats_score: number;
  keyword_match_score: number;
  structure_score: number;
  impact_score: number;
  readability_score: number;
  section_scores: Record<string, number>;
  matched_skills: string[];
  missing_skills: string[];
  missing_keywords: string[];
  grammar_errors: Array<{ snippet: string; issue: string; suggestion: string }>;
  weak_sentences: Array<{ original: string; issue: string; suggestion: string }>;
  formatting_issues: string[];
  action_verb_suggestions: string[];
  improvement_recommendations: string[];
  corrections: CorrectionItem[];
  section_breakdown: Record<string, { found: boolean; status: string }>;
  readability_metrics: {
    score?: number;
    reading_ease?: string;
    estimated_grade_level?: number;
    total_words?: number;
    total_sentences?: number;
    avg_words_per_sentence?: number;
  };
  extracted_data?: ExtractedData;
  disclaimer: string;
  detailed_feedback: string;
}

export const ResumeAnalyzerPage: React.FC = () => {
  const toast = useToast();
  const [tab, setTab] = useState<'upload' | 'paste'>('upload');
  const [activeView, setActiveView] = useState<'audit' | 'editor' | 'corrections'>('audit');
  const [file, setFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState<string>('');
  const [targetRole, setTargetRole] = useState<string>('Full Stack Software Engineer');
  const [jobDescription, setJobDescription] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysis, setAnalysis] = useState<ATSAnalysis | null>(null);

  // Edit Extracted Data State
  const [editData, setEditData] = useState<ExtractedData | null>(null);
  const [isSavingEdit, setIsSavingEdit] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      let res;
      if (tab === 'upload') {
        if (!file) {
          toast.warning('Please select a PDF or DOCX resume file.');
          setIsAnalyzing(false);
          return;
        }
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_role', targetRole);
        if (jobDescription.trim()) {
          formData.append('job_description', jobDescription.trim());
        }
        res = await apiClient.post('/resumes/analyze-upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        if (!resumeText.trim()) {
          toast.warning('Please paste your resume text.');
          setIsAnalyzing(false);
          return;
        }
        const formData = new FormData();
        formData.append('resume_text', resumeText);
        formData.append('target_role', targetRole);
        if (jobDescription.trim()) {
          formData.append('job_description', jobDescription.trim());
        }
        res = await apiClient.post('/resumes/analyze-text', formData);
      }

      setAnalysis(res.data);
      if (res.data.extracted_data) {
        setEditData(JSON.parse(JSON.stringify(res.data.extracted_data)));
      }
      setActiveView('audit');
      toast.success('Resume analyzed successfully! Comprehensive ATS audit generated.');
    } catch (err: any) {
      console.error('Failed to analyze resume:', err);
      toast.error(err.response?.data?.detail || 'Failed to analyze resume. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCorrectionAction = async (correctionId: string, action: 'accept' | 'reject') => {
    if (!analysis) return;
    try {
      const res = await apiClient.post(
        `/resumes/${analysis.id}/corrections/${correctionId}`,
        { action }
      );
      setAnalysis((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          corrections: res.data.corrections,
        };
      });
      toast.success(`Correction ${action === 'accept' ? 'accepted' : 'rejected'}.`);
    } catch (err) {
      console.error('Failed to update correction:', err);
      toast.error('Failed to update correction.');
    }
  };

  const handleAcceptAllCorrections = async () => {
    if (!analysis?.corrections) return;
    for (const c of analysis.corrections) {
      if (c.status === 'pending') {
        await handleCorrectionAction(c.id, 'accept');
      }
    }
    toast.success('All suggested professional corrections accepted!');
  };

  const handleSaveExtractedData = async () => {
    if (!analysis || !editData) return;
    setIsSavingEdit(true);
    try {
      const res = await apiClient.put(`/resumes/${analysis.resume_id}/extracted`, {
        extracted_data: editData,
      });
      setAnalysis(res.data);
      toast.success('Extracted resume details updated! Fresh ATS score calculated.');
      setActiveView('audit');
    } catch (err: any) {
      console.error('Failed to save edited resume data:', err);
      toast.error(err.response?.data?.detail || 'Failed to update extracted data.');
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!analysis || !editData) return;
    try {
      const payload = {
        full_name: editData.full_name || 'Candidate',
        email: editData.email || 'candidate@example.com',
        phone: editData.phone || '(555) 000-0000',
        location: editData.location || '',
        linkedin: editData.linkedin || '',
        github: editData.github || '',
        target_role: analysis.target_role,
        professional_summary: editData.summary || '',
        skills: editData.technical_skills || {},
        experience: editData.work_experience.map((w) => ({
          company: w.company,
          role: w.role,
          duration: w.duration,
          highlights: w.highlights,
        })),
        education: editData.education.map((e) => ({
          institution: e.institution,
          degree: e.degree,
          year: e.year || '',
          grade: e.grade || '',
        })),
        projects: editData.projects.map((p) => ({
          name: p.name,
          technologies: p.technologies,
          description: p.description,
          link: p.link || '',
        })),
        certifications: editData.certifications || [],
      };

      const res = await apiClient.post('/resumes/generate-pdf', payload, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ATS_Resume_${editData.full_name.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('ATS-friendly PDF resume generated and downloaded!');
    } catch (err) {
      console.error('Failed to export PDF:', err);
      toast.error('Failed to export PDF.');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 60) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Page Title & Mission */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <FileSearch className="w-7 h-7 text-purple-400" />
              <span>AI Resume Analyzer & ATS Gap Auditor</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Upload PDF or DOCX documents to extract all 10 key sections, evaluate ATS parsing compatibility,
              and apply AI-powered sentence improvements with 100% factual truth preservation.
            </p>
          </div>

          {analysis && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveView('audit')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  activeView === 'audit'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>ATS Audit</span>
              </button>

              <button
                onClick={() => setActiveView('editor')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  activeView === 'editor'
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Review & Edit Data</span>
              </button>

              <button
                onClick={() => setActiveView('corrections')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  activeView === 'corrections'
                    ? 'bg-emerald-600 text-white shadow-lg'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Corrections ({analysis.corrections?.length || 0})</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Prominent ATS Disclaimer Alert */}
      <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/25 flex items-start gap-3">
        <Info className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <span className="font-bold text-amber-300">ATS Estimation Disclaimer: </span>
          ATS compatibility scores generated here are heuristic benchmarks modeling industry-standard parser logic
          (keyword frequency, TF-IDF cosine matching, and structural clarity). They are estimates and do not guarantee
          identical scores across all proprietary commercial ATS systems (e.g., Workday, Taleo, Greenhouse, Lever).
        </div>
      </div>

      {/* Resume Ingestion Form */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Input Controls */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
          <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
            <button
              onClick={() => setTab('upload')}
              className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
                tab === 'upload' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload PDF / DOCX</span>
            </button>
            <button
              onClick={() => setTab('paste')}
              className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
                tab === 'paste' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Paste Text</span>
            </button>
          </div>

          {tab === 'upload' ? (
            <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-6 text-center transition-colors">
              <input
                type="file"
                id="resume-file"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="resume-file" className="cursor-pointer space-y-2 block">
                <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 mx-auto flex items-center justify-center">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div className="text-sm font-semibold text-slate-200">
                  {file ? file.name : 'Select PDF or DOCX resume'}
                </div>
                <p className="text-xs text-slate-500">Supported formats: .pdf, .docx (Max 15MB)</p>
              </label>
            </div>
          ) : (
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">
                Resume Raw Content
              </label>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your plain text resume here..."
                rows={7}
                className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1.5">
              Target Job Role
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Senior Full Stack Software Engineer"
              className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1.5">
              Job Description (Optional for Exact Match)
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste target job posting description to compute precise keyword density match..."
              rows={3}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-purple-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Running Multi-Phase ATS Audit...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Extract Sections & Audit Resume</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Quick Highlights Banner */}
        <div className="lg:col-span-7 flex flex-col justify-between p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Full-Stack Document Intelligence</span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">
              10-Section Extraction & Truth-Preserving AI Correction
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Our analyzer unpacks your resume into structured metadata without fabricating fake credentials.
              Every extracted section can be reviewed and edited directly, updating your ATS match in real-time.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-bold block">Extraction</span>
              <span className="text-xs font-extrabold text-indigo-400">10 Core Sections</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-bold block">Scoring</span>
              <span className="text-xs font-extrabold text-purple-400">11 Section Scores</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-bold block">Readability</span>
              <span className="text-xs font-extrabold text-cyan-400">Flesch / ARI Grade</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-bold block">Guarantee</span>
              <span className="text-xs font-extrabold text-emerald-400">Zero Hallucinations</span>
            </div>
          </div>

          {analysis && (
            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400">Current Candidate Profile</span>
                <div className="text-sm font-bold text-white">
                  {analysis.extracted_data?.full_name || 'Candidate Name'}
                </div>
              </div>
              <button
                onClick={handleDownloadPDF}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export ATS PDF</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Analysis Content Sections */}
      {analysis && (
        <div className="space-y-6">
          {/* VIEW 1: ATS AUDIT OVERVIEW */}
          {activeView === 'audit' && (
            <div className="space-y-6">
              {/* Overall Score & Section Scores Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Overall ATS Score</span>
                  <div className="my-2 flex items-baseline gap-2">
                    <span className="text-4xl font-black text-white">{analysis.overall_ats_score}</span>
                    <span className="text-slate-500 text-sm font-bold">/ 100</span>
                  </div>
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold border w-fit ${getScoreColor(
                      analysis.overall_ats_score
                    )}`}
                  >
                    {analysis.overall_ats_score >= 80
                      ? 'Highly Optimized'
                      : analysis.overall_ats_score >= 60
                      ? 'Competitive Pass'
                      : 'Needs Revision'}
                  </span>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Keywords & Skills</span>
                  <div className="my-2 flex items-baseline gap-2">
                    <span className="text-3xl font-black text-indigo-400">
                      {analysis.keyword_match_score}%
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">
                    {analysis.matched_skills.length} matched • {analysis.missing_skills.length} missing
                  </span>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Structure & Integrity</span>
                  <div className="my-2 flex items-baseline gap-2">
                    <span className="text-3xl font-black text-purple-400">
                      {analysis.structure_score}%
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">Standard sections & headers</span>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
                  <span className="text-xs text-slate-400 font-semibold uppercase">Readability & Metrics</span>
                  <div className="my-2 flex items-baseline gap-2">
                    <span className="text-3xl font-black text-cyan-400">
                      {analysis.readability_score}%
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">
                    Grade {analysis.readability_metrics?.estimated_grade_level || 10} • {analysis.readability_metrics?.avg_words_per_sentence || 14} words/sentence
                  </span>
                </div>
              </div>

              {/* 11 Section-Wise Scores Detailed Matrix */}
              <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-indigo-400" />
                  <span>Section-Wise ATS Compatibility Scores (0 - 100)</span>
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  {Object.entries(analysis.section_scores || {}).map(([sec, score]) => (
                    <div
                      key={sec}
                      className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col justify-between"
                    >
                      <div className="text-[11px] font-semibold text-slate-400 capitalize">
                        {sec.replace(/_/g, ' ')}
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-lg font-black text-white">{Math.round(score)}%</span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                            score >= 80
                              ? 'text-emerald-400 bg-emerald-500/10'
                              : score >= 60
                              ? 'text-amber-400 bg-amber-500/10'
                              : 'text-rose-400 bg-rose-500/10'
                          }`}
                        >
                          {score >= 80 ? 'Pass' : score >= 60 ? 'Fair' : 'Attention'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Matched vs Missing Keywords */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Matched Skills */}
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                      <span>Matched Technical Keywords ({analysis.matched_skills.length})</span>
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.matched_skills.map((s, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold capitalize flex items-center gap-1.5"
                      >
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span>{s}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-amber-400" />
                      <span>Missing Recommended Keywords ({analysis.missing_skills.length})</span>
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {analysis.missing_skills.length > 0 ? (
                      analysis.missing_skills.map((s, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold capitalize"
                        >
                          + {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">All target skills detected!</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Grammar Errors & Weak Sentences Audit */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Grammar & Spelling Errors */}
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                  <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-rose-400" />
                    <span>Grammar & Spelling Diagnostics ({analysis.grammar_errors?.length || 0})</span>
                  </h3>
                  {analysis.grammar_errors && analysis.grammar_errors.length > 0 ? (
                    <div className="space-y-2.5">
                      {analysis.grammar_errors.map((g, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-slate-950/70 border border-rose-500/20 text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-rose-300">"{g.snippet}"</span>
                            <span className="text-slate-400 text-[11px]">{g.issue}</span>
                          </div>
                          <div className="text-slate-300">
                            Suggested replacement: <span className="font-bold text-emerald-400">{g.suggestion}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center border border-dashed border-slate-800 rounded-xl text-xs text-slate-400">
                      No grammatical or spelling flags identified.
                    </div>
                  )}
                </div>

                {/* Weak & Passive Sentences */}
                <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
                  <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    <span>Weak & Passive Sentences Flagged ({analysis.weak_sentences?.length || 0})</span>
                  </h3>
                  {analysis.weak_sentences && analysis.weak_sentences.length > 0 ? (
                    <div className="space-y-2.5">
                      {analysis.weak_sentences.slice(0, 4).map((w, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-slate-950/70 border border-purple-500/20 text-xs space-y-1"
                        >
                          <div className="text-slate-300 font-medium">"{w.original}"</div>
                          <div className="text-amber-400 text-[11px]">{w.issue}</div>
                          <div className="text-slate-400 text-[11px]">{w.suggestion}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center border border-dashed border-slate-800 rounded-xl text-xs text-slate-400">
                      All sentences use proactive voice and action verbs.
                    </div>
                  )}
                </div>
              </div>

              {/* Formatting & Recommendations */}
              <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-3">
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <BookmarkCheck className="w-5 h-5 text-indigo-400" />
                  <span>Actionable Improvement Recommendations</span>
                </h3>
                <div className="space-y-2">
                  {analysis.improvement_recommendations?.map((rec, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5"
                    >
                      <CheckCircle className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* VIEW 2: REVIEW & EDIT EXTRACTED INFORMATION */}
          {activeView === 'editor' && editData && (
            <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                    <Edit3 className="w-5 h-5 text-indigo-400" />
                    <span>Review and Edit Extracted Information</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Verify all 10 extracted resume fields. Any edits you make will recalculate your ATS score immediately.
                  </p>
                </div>

                <button
                  onClick={handleSaveExtractedData}
                  disabled={isSavingEdit}
                  className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition-all disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  <span>{isSavingEdit ? 'Saving...' : 'Save & Recalculate ATS'}</span>
                </button>
              </div>

              {/* 1. Contact Info */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  1. Contact Information
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Full Name</label>
                    <input
                      type="text"
                      value={editData.full_name}
                      onChange={(e) => setEditData({ ...editData, full_name: e.target.value })}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs text-slate-200"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Email</label>
                    <input
                      type="email"
                      value={editData.email}
                      onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs text-slate-200"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Phone</label>
                    <input
                      type="text"
                      value={editData.phone}
                      onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs text-slate-200"
                    />
                  </div>
                </div>
              </div>

              {/* 2. Professional Summary */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  2. Professional Summary
                </h4>
                <textarea
                  value={editData.summary || ''}
                  onChange={(e) => setEditData({ ...editData, summary: e.target.value })}
                  rows={3}
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200"
                />
              </div>

              {/* 3. Education */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  3. Education Background
                </h4>
                {editData.education.map((edu, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Institution</label>
                      <input
                        type="text"
                        value={edu.institution}
                        onChange={(e) => {
                          const updated = [...editData.education];
                          updated[idx].institution = e.target.value;
                          setEditData({ ...editData, education: updated });
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Degree</label>
                      <input
                        type="text"
                        value={edu.degree}
                        onChange={(e) => {
                          const updated = [...editData.education];
                          updated[idx].degree = e.target.value;
                          setEditData({ ...editData, education: updated });
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Year / Dates</label>
                      <input
                        type="text"
                        value={edu.year || ''}
                        onChange={(e) => {
                          const updated = [...editData.education];
                          updated[idx].year = e.target.value;
                          setEditData({ ...editData, education: updated });
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* 4. Work Experience & 5. Internships */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  4. Work Experience & Internships
                </h4>
                {editData.work_experience.map((exp, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div>
                        <label className="text-[11px] text-slate-400 block mb-1">Company</label>
                        <input
                          type="text"
                          value={exp.company}
                          onChange={(e) => {
                            const updated = [...editData.work_experience];
                            updated[idx].company = e.target.value;
                            setEditData({ ...editData, work_experience: updated });
                          }}
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] text-slate-400 block mb-1">Role Title</label>
                        <input
                          type="text"
                          value={exp.role}
                          onChange={(e) => {
                            const updated = [...editData.work_experience];
                            updated[idx].role = e.target.value;
                            setEditData({ ...editData, work_experience: updated });
                          }}
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] text-slate-400 block mb-1">Duration</label>
                        <input
                          type="text"
                          value={exp.duration}
                          onChange={(e) => {
                            const updated = [...editData.work_experience];
                            updated[idx].duration = e.target.value;
                            setEditData({ ...editData, work_experience: updated });
                          }}
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Highlights (One per line)</label>
                      <textarea
                        value={exp.highlights.join('\n')}
                        onChange={(e) => {
                          const updated = [...editData.work_experience];
                          updated[idx].highlights = e.target.value.split('\n');
                          setEditData({ ...editData, work_experience: updated });
                        }}
                        rows={3}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2 text-xs text-slate-200 font-mono"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* 5. Projects */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  5. Projects
                </h4>
                {editData.projects.map((proj, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="text-[11px] text-slate-400 block mb-1">Project Name</label>
                        <input
                          type="text"
                          value={proj.name}
                          onChange={(e) => {
                            const updated = [...editData.projects];
                            updated[idx].name = e.target.value;
                            setEditData({ ...editData, projects: updated });
                          }}
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] text-slate-400 block mb-1">Technologies (Comma separated)</label>
                        <input
                          type="text"
                          value={proj.technologies.join(', ')}
                          onChange={(e) => {
                            const updated = [...editData.projects];
                            updated[idx].technologies = e.target.value.split(',').map((t) => t.trim());
                            setEditData({ ...editData, projects: updated });
                          }}
                          className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Description</label>
                      <textarea
                        value={proj.description}
                        onChange={(e) => {
                          const updated = [...editData.projects];
                          updated[idx].description = e.target.value;
                          setEditData({ ...editData, projects: updated });
                        }}
                        rows={2}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2 text-xs text-slate-200"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* 6. Certifications & Achievements */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    6. Certifications (One per line)
                  </h4>
                  <textarea
                    value={editData.certifications.join('\n')}
                    onChange={(e) => setEditData({ ...editData, certifications: e.target.value.split('\n') })}
                    rows={3}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200"
                  />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    7. Achievements & Awards (One per line)
                  </h4>
                  <textarea
                    value={editData.achievements.join('\n')}
                    onChange={(e) => setEditData({ ...editData, achievements: e.target.value.split('\n') })}
                    rows={3}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200"
                  />
                </div>
              </div>
            </div>
          )}

          {/* VIEW 3: AI RESUME CORRECTION (BEFORE & AFTER COMPARISONS) */}
          {activeView === 'corrections' && (
            <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold mb-2">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Factual Truth Preservation Guard</span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-emerald-400" />
                    <span>AI Resume Corrections & Bullet Point Optimizer</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Upgrade passive voice and weak verbs into high-impact engineering accomplishments.
                    Review each before-and-after comparison and accept or reject individual suggestions.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={handleAcceptAllCorrections}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 flex items-center gap-1.5 transition-all"
                  >
                    <CheckCheck className="w-4 h-4" />
                    <span>Accept All Corrections</span>
                  </button>
                </div>
              </div>

              {/* Correction Cards List */}
              <div className="space-y-4">
                {analysis.corrections && analysis.corrections.length > 0 ? (
                  analysis.corrections.map((corr) => (
                    <div
                      key={corr.id}
                      className={`p-5 rounded-2xl border transition-all ${
                        corr.status === 'accepted'
                          ? 'bg-emerald-950/20 border-emerald-500/30'
                          : corr.status === 'rejected'
                          ? 'bg-slate-950/40 border-slate-800 opacity-60'
                          : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3 mb-3">
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider bg-indigo-500/15 text-indigo-300 border border-indigo-500/25">
                          {corr.category}
                        </span>

                        <div className="flex items-center gap-2">
                          {corr.status === 'accepted' ? (
                            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                              <CheckCircle className="w-4 h-4" />
                              <span>Accepted</span>
                            </span>
                          ) : corr.status === 'rejected' ? (
                            <span className="text-xs font-bold text-slate-500 flex items-center gap-1">
                              <XCircle className="w-4 h-4" />
                              <span>Rejected</span>
                            </span>
                          ) : (
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleCorrectionAction(corr.id, 'reject')}
                                className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1 transition-colors"
                              >
                                <X className="w-3.5 h-3.5" />
                                <span>Reject</span>
                              </button>
                              <button
                                onClick={() => handleCorrectionAction(corr.id, 'accept')}
                                className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1 shadow-md shadow-emerald-600/20 transition-colors"
                              >
                                <Check className="w-3.5 h-3.5" />
                                <span>Accept</span>
                              </button>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Before and After Comparison Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        {/* Original */}
                        <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800/80 space-y-1">
                          <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider block">
                            Before (Original Bullet)
                          </span>
                          <p className="text-slate-300 leading-relaxed font-sans">{corr.original}</p>
                        </div>

                        {/* Corrected */}
                        <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-1">
                          <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">
                            After (AI-Enhanced Impact)
                          </span>
                          <p className="text-emerald-100 font-medium leading-relaxed font-sans">
                            {corr.corrected}
                          </p>
                        </div>
                      </div>

                      <div className="mt-3 text-[11px] text-slate-400 flex items-start gap-1.5">
                        <Info className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        <span>{corr.explanation}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center border border-dashed border-slate-800 rounded-2xl text-xs text-slate-400">
                    No sentence corrections needed. Your resume phrasing is already high-velocity!
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumeAnalyzerPage;
