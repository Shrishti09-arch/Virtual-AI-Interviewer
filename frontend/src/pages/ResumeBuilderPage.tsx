import React, { useState } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import {
  FileText,
  Download,
  Plus,
  Trash2,
  Sparkles,
  CheckCircle,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Award,
  Layers,
  ShieldCheck,
  AlertTriangle,
  ChevronDown,
  Info,
  Check,
  FileCode,
  Sliders,
  RefreshCw,
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

const EXPERIENCE_LEVELS = [
  'Student / Intern',
  'Entry Level (0-2 yrs)',
  'Mid-Level (3-5 yrs)',
  'Senior (5-8 yrs)',
  'Lead / Staff (8+ yrs)',
];

const TEMPLATE_STYLES = [
  { id: 'modern', name: 'Modern ATS Clean', desc: 'Single-column with subtle accent rules' },
  { id: 'classic', name: 'Classic Executive', desc: 'Traditional serif header, high corporate readability' },
  { id: 'minimalist', name: 'Minimalist Tech', desc: 'Pure sans-serif, high-density monospace accents' },
];

interface WorkExperienceItem {
  company: string;
  role: string;
  duration: string;
  highlights: string[];
}

interface ProjectItem {
  name: string;
  technologies: string;
  description: string;
  link: string;
}

interface EducationItem {
  degree: string;
  institution: string;
  year: string;
  grade: string;
}

export const ResumeBuilderPage: React.FC = () => {
  const { user } = useAuth();
  const toast = useToast();

  // Role & Experience Meta
  const [targetRole, setTargetRole] = useState<string>('Full Stack Developer');
  const [experienceLevel, setExperienceLevel] = useState<string>('Mid-Level (3-5 yrs)');
  const [templateStyle, setTemplateStyle] = useState<string>('modern');
  const [jobDescription, setJobDescription] = useState<string>('');

  // Personal Contact Info
  const [fullName, setFullName] = useState<string>(user?.full_name || 'Alex Morgan');
  const [email, setEmail] = useState<string>(user?.email || 'alex.morgan@example.com');
  const [phone, setPhone] = useState<string>('+1 (555) 234-5678');
  const [location, setLocation] = useState<string>('San Francisco, CA');
  const [linkedin, setLinkedin] = useState<string>('linkedin.com/in/alexmorgan');
  const [github, setGithub] = useState<string>('github.com/alexmorgan');

  // Professional Summary
  const [summary, setSummary] = useState<string>(
    'Performance-driven Full Stack Developer with 3+ years of experience architecting resilient RESTful APIs, distributed microservices, and reactive SPAs using React, TypeScript, FastAPI, and PostgreSQL. Proven track record of optimizing database queries and reducing p99 latency by 40%.'
  );

  // Technical Skills
  const [skillsLanguages, setSkillsLanguages] = useState<string>('Python, JavaScript, TypeScript, SQL, Go');
  const [skillsFrameworks, setSkillsFrameworks] = useState<string>('React, Next.js, FastAPI, Node.js, Express, Tailwind CSS');
  const [skillsDatabases, setSkillsDatabases] = useState<string>('PostgreSQL, Redis, MongoDB, SQLAlchemy');
  const [skillsTools, setSkillsTools] = useState<string>('Docker, Kubernetes, AWS, CI/CD, GitHub Actions, Linux');

  // Work Experience
  const [experience, setExperience] = useState<WorkExperienceItem[]>([
    {
      company: 'Apex Cloud Solutions',
      role: 'Full Stack Software Engineer',
      duration: '2023 - Present',
      highlights: [
        'Architected real-time analytics microservice using FastAPI and Redis, handling 15,000 requests/second with sub-50ms latency.',
        'Migrated legacy frontend components to React 19 and TypeScript, decreasing bundle size by 35% and improving LCP score to 1.8s.',
        'Engineered automated CI/CD pipeline using GitHub Actions and Docker, reducing deployment cycle time from 45 to 8 minutes.',
      ],
    },
    {
      company: 'Novus Interactive',
      role: 'Software Engineer',
      duration: '2021 - 2023',
      highlights: [
        'Developed modular React UI components using Tailwind CSS across 4 core client-facing products.',
        'Optimized PostgreSQL queries through strategic indexing and query re-writes, slashing slow API execution times by 40%.',
      ],
    },
  ]);

  // Internships
  const [internships, setInternships] = useState<WorkExperienceItem[]>([
    {
      company: 'NextGen Digital Labs',
      role: 'Software Engineering Intern',
      duration: 'Summer 2021',
      highlights: [
        'Built automated integration test suites with PyTest and Jest, boosting test coverage to 88%.',
        'Refactored legacy REST endpoints to async FastAPI routers, decreasing API response overhead.',
      ],
    },
  ]);

  // Projects
  const [projects, setProjects] = useState<ProjectItem[]>([
    {
      name: 'Distributed Rate Limiter Middleware',
      technologies: 'FastAPI, Redis, Docker, Python',
      description:
        'Engineered a token-bucket rate limiter middleware enforcing tenant API quotas with atomic Redis Lua scripts.',
      link: 'https://github.com/alexmorgan/rate-limiter',
    },
    {
      name: 'Real-Time Collaboration Canvas',
      technologies: 'React, TypeScript, WebSockets, Tailwind',
      description:
        'Built interactive whiteboard application supporting 50+ concurrent editors with optimistic UI updates.',
      link: 'https://github.com/alexmorgan/collab-canvas',
    },
  ]);

  // Education
  const [education, setEducation] = useState<EducationItem[]>([
    {
      degree: 'B.S. in Computer Science',
      institution: 'University of California, Berkeley',
      year: '2017 - 2021',
      grade: '3.85 / 4.0',
    },
  ]);

  // Certifications & Achievements
  const [certificationsText, setCertificationsText] = useState<string>(
    'AWS Certified Solutions Architect - Associate\nCertified Kubernetes Administrator (CKA)'
  );
  const [achievementsText, setAchievementsText] = useState<string>(
    '1st Place Winner - Bay Area Cloud Hackathon 2022\nPublished paper on High-Throughput Distributed State Machines'
  );

  // Optimization & ATS State
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [isExportingPDF, setIsExportingPDF] = useState<boolean>(false);
  const [isExportingDOCX, setIsExportingDOCX] = useState<boolean>(false);
  const [estimatedATS, setEstimatedATS] = useState<number>(84.0);
  const [missingKeywords, setMissingKeywords] = useState<string[]>([
    'Microservices',
    'CI/CD',
    'Concurrency',
  ]);
  const [matchedKeywords, setMatchedKeywords] = useState<string[]>([
    'React',
    'TypeScript',
    'FastAPI',
    'Docker',
    'PostgreSQL',
  ]);
  const [sectionOrder, setSectionOrder] = useState<string[]>([
    'summary',
    'skills',
    'experience',
    'internships',
    'projects',
    'education',
    'certifications',
    'achievements',
  ]);
  const [optimizationTips, setOptimizationTips] = useState<string[]>([
    'Resume structured specifically for Full Stack Developer roles.',
    'High action-verb density detected across work experience highlights.',
  ]);

  // 1. Role-Based AI Optimization Trigger
  const handleOptimizeForRole = async () => {
    setIsOptimizing(true);
    try {
      const payload = {
        target_role: targetRole,
        experience_level: experienceLevel,
        full_name: fullName,
        professional_summary: summary,
        skills: {
          Languages: skillsLanguages.split(',').map((s) => s.trim()).filter(Boolean),
          Frameworks: skillsFrameworks.split(',').map((s) => s.trim()).filter(Boolean),
          Databases: skillsDatabases.split(',').map((s) => s.trim()).filter(Boolean),
          'Tools & Cloud': skillsTools.split(',').map((s) => s.trim()).filter(Boolean),
        },
        experience: experience.map((exp) => ({
          company: exp.company,
          role: exp.role,
          duration: exp.duration,
          highlights: exp.highlights,
        })),
        internships: internships.map((i) => ({
          company: i.company,
          role: i.role,
          duration: i.duration,
          highlights: i.highlights,
        })),
        projects: projects.map((p) => ({
          name: p.name,
          technologies: p.technologies.split(',').map((t) => t.trim()).filter(Boolean),
          description: p.description,
          link: p.link,
        })),
        education: education.map((e) => ({
          institution: e.institution,
          degree: e.degree,
          year: e.year,
          grade: e.grade,
        })),
        certifications: certificationsText.split('\n').map((s) => s.trim()).filter(Boolean),
        achievements: achievementsText.split('\n').map((s) => s.trim()).filter(Boolean),
        job_description: jobDescription.trim() || undefined,
      };

      const res = await apiClient.post('/resumes/optimize-role', payload);
      const data = res.data;

      // Update state with role-optimized data
      setSummary(data.optimized_summary);
      setEstimatedATS(data.estimated_ats_score);
      setMissingKeywords(data.missing_keywords || []);
      setMatchedKeywords(data.matched_keywords || []);
      setSectionOrder(data.recommended_section_order || sectionOrder);
      setOptimizationTips(data.tips || []);

      // If recommended skills provided, update inputs
      if (data.recommended_skills) {
        if (data.recommended_skills.Languages) {
          setSkillsLanguages(data.recommended_skills.Languages.join(', '));
        }
        if (data.recommended_skills.Frameworks) {
          setSkillsFrameworks(data.recommended_skills.Frameworks.join(', '));
        }
        if (data.recommended_skills.Databases) {
          setSkillsDatabases(data.recommended_skills.Databases.join(', '));
        }
        if (data.recommended_skills['Tools & Cloud']) {
          setSkillsTools(data.recommended_skills['Tools & Cloud'].join(', '));
        }
      }

      toast.success(`Resume role-optimized for ${data.target_role}! Estimated ATS Score: ${data.estimated_ats_score}%`);
    } catch (err: any) {
      console.error('Failed to optimize resume for role:', err);
      toast.error(err.response?.data?.detail || 'Failed to optimize resume. Please check fields.');
    } finally {
      setIsOptimizing(false);
    }
  };

  // Add missing keyword to skills
  const handleAddKeyword = (kw: string) => {
    setSkillsTools((prev) => (prev ? `${prev}, ${kw}` : kw));
    setMissingKeywords((prev) => prev.filter((k) => k !== kw));
    setMatchedKeywords((prev) => [...prev, kw]);
  };

  // 2. Export PDF
  const handleExportPDF = async () => {
    setIsExportingPDF(true);
    try {
      const payload = {
        full_name: fullName,
        email,
        phone,
        location,
        linkedin,
        github,
        target_role: targetRole,
        experience_level: experienceLevel,
        professional_summary: summary,
        skills: {
          Languages: skillsLanguages.split(',').map((s) => s.trim()).filter(Boolean),
          Frameworks: skillsFrameworks.split(',').map((s) => s.trim()).filter(Boolean),
          Databases: skillsDatabases.split(',').map((s) => s.trim()).filter(Boolean),
          'Tools & Cloud': skillsTools.split(',').map((s) => s.trim()).filter(Boolean),
        },
        experience: experience.map((exp) => ({
          company: exp.company,
          role: exp.role,
          duration: exp.duration,
          highlights: exp.highlights,
        })),
        internships: internships.map((i) => ({
          company: i.company,
          role: i.role,
          duration: i.duration,
          highlights: i.highlights,
        })),
        education: education.map((edu) => ({
          institution: edu.institution,
          degree: edu.degree,
          year: edu.year,
          grade: edu.grade,
        })),
        projects: projects.map((proj) => ({
          name: proj.name,
          technologies: proj.technologies.split(',').map((s) => s.trim()).filter(Boolean),
          description: proj.description,
          link: proj.link,
        })),
        certifications: certificationsText.split('\n').map((s) => s.trim()).filter(Boolean),
        achievements: achievementsText.split('\n').map((s) => s.trim()).filter(Boolean),
        template_style: templateStyle,
        section_order: sectionOrder,
      };

      const res = await apiClient.post('/resumes/generate-pdf', payload, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ATS_Resume_${fullName.replace(/\s+/g, '_')}_${targetRole.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('ATS-friendly PDF successfully compiled and downloaded!');
    } catch (err) {
      console.error('Failed to export PDF:', err);
      toast.error('Failed to generate ATS PDF.');
    } finally {
      setIsExportingPDF(false);
    }
  };

  // 3. Export DOCX
  const handleExportDOCX = async () => {
    setIsExportingDOCX(true);
    try {
      const payload = {
        full_name: fullName,
        email,
        phone,
        location,
        linkedin,
        github,
        target_role: targetRole,
        experience_level: experienceLevel,
        professional_summary: summary,
        skills: {
          Languages: skillsLanguages.split(',').map((s) => s.trim()).filter(Boolean),
          Frameworks: skillsFrameworks.split(',').map((s) => s.trim()).filter(Boolean),
          Databases: skillsDatabases.split(',').map((s) => s.trim()).filter(Boolean),
          'Tools & Cloud': skillsTools.split(',').map((s) => s.trim()).filter(Boolean),
        },
        experience: experience.map((exp) => ({
          company: exp.company,
          role: exp.role,
          duration: exp.duration,
          highlights: exp.highlights,
        })),
        internships: internships.map((i) => ({
          company: i.company,
          role: i.role,
          duration: i.duration,
          highlights: i.highlights,
        })),
        education: education.map((edu) => ({
          institution: edu.institution,
          degree: edu.degree,
          year: edu.year,
          grade: edu.grade,
        })),
        projects: projects.map((proj) => ({
          name: proj.name,
          technologies: proj.technologies.split(',').map((s) => s.trim()).filter(Boolean),
          description: proj.description,
          link: proj.link,
        })),
        certifications: certificationsText.split('\n').map((s) => s.trim()).filter(Boolean),
        achievements: achievementsText.split('\n').map((s) => s.trim()).filter(Boolean),
        template_style: templateStyle,
        section_order: sectionOrder,
      };

      const res = await apiClient.post('/resumes/generate-docx', payload, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(
        new Blob([res.data], {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        })
      );
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ATS_Resume_${fullName.replace(/\s+/g, '_')}_${targetRole.replace(/\s+/g, '_')}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('ATS-friendly DOCX successfully compiled and downloaded!');
    } catch (err) {
      console.error('Failed to export DOCX:', err);
      toast.error('Failed to generate ATS DOCX.');
    } finally {
      setIsExportingDOCX(false);
    }
  };

  // List manipulation helpers
  const addExperience = () => {
    setExperience([
      ...experience,
      {
        company: 'New Tech Company',
        role: targetRole,
        duration: '2023 - Present',
        highlights: ['Architected scalable core service enhancing system throughput by 25%.'],
      },
    ]);
  };

  const removeExperience = (idx: number) => {
    setExperience(experience.filter((_, i) => i !== idx));
  };

  const addInternship = () => {
    setInternships([
      ...internships,
      {
        company: 'Innovate Labs',
        role: 'Software Engineering Intern',
        duration: 'Summer 2022',
        highlights: ['Collaborated on microservice development with automated CI/CD.'],
      },
    ]);
  };

  const removeInternship = (idx: number) => {
    setInternships(internships.filter((_, i) => i !== idx));
  };

  const addProject = () => {
    setProjects([
      ...projects,
      {
        name: 'New Technical Project',
        technologies: 'React, FastAPI, PostgreSQL',
        description: 'Engineered high-throughput application with full test coverage and clean architecture.',
        link: 'https://github.com/username/project',
      },
    ]);
  };

  const removeProject = (idx: number) => {
    setProjects(projects.filter((_, i) => i !== idx));
  };

  const addEducation = () => {
    setEducation([
      ...education,
      {
        degree: 'B.S. in Computer Science',
        institution: 'University / Institute',
        year: '2020 - 2024',
        grade: '3.8 GPA',
      },
    ]);
  };

  const removeEducation = (idx: number) => {
    setEducation(education.filter((_, i) => i !== idx));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* 1. Header & Role Selector Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Module 2: Role-Based AI Resume Builder</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-2">
            <FileText className="w-7 h-7 text-emerald-400" />
            <span>Role-Specific ATS Resume Builder</span>
          </h1>
          <p className="text-xs text-slate-400 max-w-xl">
            Target 12 standardized tech roles with adaptive section ordering, high-velocity action verbs,
            real-time ATS score estimates, and direct PDF and DOCX downloads.
          </p>
        </div>

        {/* Global Action Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleOptimizeForRole}
            disabled={isOptimizing}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {isOptimizing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Optimizing for {targetRole}...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-emerald-200" />
                <span>AI Role-Optimize Resume</span>
              </>
            )}
          </button>

          <button
            onClick={handleExportPDF}
            disabled={isExportingPDF}
            className="px-4 py-2.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-bold flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>{isExportingPDF ? 'Building PDF...' : 'Download PDF'}</span>
          </button>

          <button
            onClick={handleExportDOCX}
            disabled={isExportingDOCX}
            className="px-4 py-2.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 text-cyan-300 text-xs font-bold flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <FileCode className="w-4 h-4" />
            <span>{isExportingDOCX ? 'Building DOCX...' : 'Download DOCX'}</span>
          </button>
        </div>
      </div>

      {/* 2. Role, Experience & Template Config Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
        {/* Role Selector */}
        <div>
          <label className="text-xs font-bold text-slate-400 block mb-1.5">
            1. Target Job Role (12 Roles Supported)
          </label>
          <select
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-100 focus:outline-none focus:border-emerald-500"
          >
            {SUPPORTED_ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        {/* Experience Level Selector */}
        <div>
          <label className="text-xs font-bold text-slate-400 block mb-1.5">
            2. Experience Level
          </label>
          <select
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
            className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-100 focus:outline-none focus:border-emerald-500"
          >
            {EXPERIENCE_LEVELS.map((lvl) => (
              <option key={lvl} value={lvl}>
                {lvl}
              </option>
            ))}
          </select>
        </div>

        {/* Template Style Selector */}
        <div>
          <label className="text-xs font-bold text-slate-400 block mb-1.5">
            3. ATS Resume Template Style
          </label>
          <select
            value={templateStyle}
            onChange={(e) => setTemplateStyle(e.target.value)}
            className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-100 focus:outline-none focus:border-emerald-500"
          >
            {TEMPLATE_STYLES.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 3. Real-Time ATS Score & Keyword Health Widget */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
              <span className="text-lg font-black">{estimatedATS}</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">Estimated ATS Compatibility Score</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  {estimatedATS >= 80 ? 'ATS Optimized' : 'Needs Keywords'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Targeting: <span className="text-indigo-400 font-semibold">{targetRole}</span> •{' '}
                {matchedKeywords.length} matched role keywords
              </p>
            </div>
          </div>

          <div className="text-xs text-slate-500 max-w-sm text-right hidden sm:block">
            ATS scores are simulated heuristic estimates. Always review and customize details before submitting.
          </div>
        </div>

        {/* Missing Keywords Bar with 1-click Add */}
        {missingKeywords.length > 0 && (
          <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              <span>Missing Role Keywords:</span>
            </span>
            {missingKeywords.map((kw) => (
              <button
                key={kw}
                onClick={() => handleAddKeyword(kw)}
                title="Click to add into your technical skills"
                className="px-2 py-0.5 rounded-md bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 text-amber-300 text-[11px] font-semibold transition-colors flex items-center gap-1"
              >
                <span>+ {kw}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 4. Main Two-Column Layout: Left Form Inputs, Right Live Editable Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Form Inputs (6 Cols) */}
        <div className="lg:col-span-6 space-y-6">
          {/* Optional Job Description */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <label className="text-xs font-bold text-slate-300 block">
              Optional Job Description (Paste Job Posting to Target Keywords)
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste specific job posting requirements to align keywords and experience descriptions..."
              rows={2}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Contact Details */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Contact Information
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Phone</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">LinkedIn Profile</label>
                <input
                  type="text"
                  value={linkedin}
                  onChange={(e) => setLinkedin(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">GitHub / Portfolio</label>
                <input
                  type="text"
                  value={github}
                  onChange={(e) => setGithub(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
            </div>
          </div>

          {/* Professional Summary */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                Professional Summary
              </h3>
              <span className="text-[11px] text-indigo-400 font-medium">Role Tailored</span>
            </div>
            <textarea
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              rows={4}
              className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 leading-relaxed"
            />
          </div>

          {/* Technical Skills */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Technical Skills (Categorized)
            </h3>
            <div className="space-y-2.5">
              <div>
                <label className="text-[11px] text-slate-400 block mb-0.5">Languages</label>
                <input
                  type="text"
                  value={skillsLanguages}
                  onChange={(e) => setSkillsLanguages(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-0.5">Frameworks & Libraries</label>
                <input
                  type="text"
                  value={skillsFrameworks}
                  onChange={(e) => setSkillsFrameworks(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-0.5">Databases & Caching</label>
                <input
                  type="text"
                  value={skillsDatabases}
                  onChange={(e) => setSkillsDatabases(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-0.5">DevOps, Cloud & Tools</label>
                <input
                  type="text"
                  value={skillsTools}
                  onChange={(e) => setSkillsTools(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-1.5 text-xs text-slate-200"
                />
              </div>
            </div>
          </div>

          {/* Work Experience */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-emerald-400" />
                <span>Work Experience ({experience.length})</span>
              </h3>
              <button
                onClick={addExperience}
                className="px-2.5 py-1 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-semibold flex items-center gap-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Job</span>
              </button>
            </div>

            <div className="space-y-4">
              {experience.map((exp, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400">Position #{idx + 1}</span>
                    <button
                      onClick={() => removeExperience(idx)}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Company</label>
                      <input
                        type="text"
                        value={exp.company}
                        onChange={(e) => {
                          const updated = [...experience];
                          updated[idx].company = e.target.value;
                          setExperience(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Role Title</label>
                      <input
                        type="text"
                        value={exp.role}
                        onChange={(e) => {
                          const updated = [...experience];
                          updated[idx].role = e.target.value;
                          setExperience(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Dates / Duration</label>
                      <input
                        type="text"
                        value={exp.duration}
                        onChange={(e) => {
                          const updated = [...experience];
                          updated[idx].duration = e.target.value;
                          setExperience(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">
                      Achievement Highlights (One bullet per line)
                    </label>
                    <textarea
                      value={exp.highlights.join('\n')}
                      onChange={(e) => {
                        const updated = [...experience];
                        updated[idx].highlights = e.target.value.split('\n');
                        setExperience(updated);
                      }}
                      rows={3}
                      className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2 text-xs text-slate-200 font-mono"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Internships Details */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-cyan-400" />
                <span>Internships ({internships.length})</span>
              </h3>
              <button
                onClick={addInternship}
                className="px-2.5 py-1 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 text-xs font-semibold flex items-center gap-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Internship</span>
              </button>
            </div>

            <div className="space-y-3">
              {internships.map((intern, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400">Internship #{idx + 1}</span>
                    <button
                      onClick={() => removeInternship(idx)}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Company</label>
                      <input
                        type="text"
                        value={intern.company}
                        onChange={(e) => {
                          const updated = [...internships];
                          updated[idx].company = e.target.value;
                          setInternships(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Role Title</label>
                      <input
                        type="text"
                        value={intern.role}
                        onChange={(e) => {
                          const updated = [...internships];
                          updated[idx].role = e.target.value;
                          setInternships(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Duration</label>
                      <input
                        type="text"
                        value={intern.duration}
                        onChange={(e) => {
                          const updated = [...internships];
                          updated[idx].duration = e.target.value;
                          setInternships(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Internship Highlights</label>
                    <textarea
                      value={intern.highlights.join('\n')}
                      onChange={(e) => {
                        const updated = [...internships];
                        updated[idx].highlights = e.target.value.split('\n');
                        setInternships(updated);
                      }}
                      rows={2}
                      className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2 text-xs text-slate-200 font-mono"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Projects */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-purple-400" />
                <span>Key Projects ({projects.length})</span>
              </h3>
              <button
                onClick={addProject}
                className="px-2.5 py-1 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 text-xs font-semibold flex items-center gap-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Project</span>
              </button>
            </div>

            <div className="space-y-3">
              {projects.map((proj, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400">Project #{idx + 1}</span>
                    <button
                      onClick={() => removeProject(idx)}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Project Name</label>
                      <input
                        type="text"
                        value={proj.name}
                        onChange={(e) => {
                          const updated = [...projects];
                          updated[idx].name = e.target.value;
                          setProjects(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Technologies Used</label>
                      <input
                        type="text"
                        value={proj.technologies}
                        onChange={(e) => {
                          const updated = [...projects];
                          updated[idx].technologies = e.target.value;
                          setProjects(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Project Description & Outcomes</label>
                    <textarea
                      value={proj.description}
                      onChange={(e) => {
                        const updated = [...projects];
                        updated[idx].description = e.target.value;
                        setProjects(updated);
                      }}
                      rows={2}
                      className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2 text-xs text-slate-200"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Education */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-indigo-400" />
                <span>Education ({education.length})</span>
              </h3>
              <button
                onClick={addEducation}
                className="px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs font-semibold flex items-center gap-1 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Education</span>
              </button>
            </div>

            <div className="space-y-3">
              {education.map((edu, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400">Entry #{idx + 1}</span>
                    <button
                      onClick={() => removeEducation(idx)}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Degree</label>
                      <input
                        type="text"
                        value={edu.degree}
                        onChange={(e) => {
                          const updated = [...education];
                          updated[idx].degree = e.target.value;
                          setEducation(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Institution</label>
                      <input
                        type="text"
                        value={edu.institution}
                        onChange={(e) => {
                          const updated = [...education];
                          updated[idx].institution = e.target.value;
                          setEducation(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Graduation Year</label>
                      <input
                        type="text"
                        value={edu.year}
                        onChange={(e) => {
                          const updated = [...education];
                          updated[idx].year = e.target.value;
                          setEducation(updated);
                        }}
                        className="w-full rounded-lg bg-slate-900 border border-slate-800 px-2.5 py-1 text-xs text-slate-200"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications & Achievements */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Certifications & Achievements</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Certifications (One per line)</label>
                <textarea
                  value={certificationsText}
                  onChange={(e) => setCertificationsText(e.target.value)}
                  rows={3}
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Achievements (One per line)</label>
                <textarea
                  value={achievementsText}
                  onChange={(e) => setAchievementsText(e.target.value)}
                  rows={3}
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs text-slate-200"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Live Editable Preview (6 Cols) */}
        <div className="lg:col-span-6 sticky top-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Live ATS Resume Preview
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                Style: {templateStyle}
              </span>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">Real-time sync</span>
          </div>

          {/* Resume Document Paper Container */}
          <div
            className={`p-8 rounded-2xl shadow-2xl space-y-5 text-slate-900 text-xs min-h-[720px] transition-all ${
              templateStyle === 'classic'
                ? 'bg-amber-50/95 font-serif border border-amber-200/50'
                : templateStyle === 'minimalist'
                ? 'bg-slate-100 font-mono border border-slate-300'
                : 'bg-white font-sans border border-slate-200'
            }`}
          >
            {/* Header: Name & Contact */}
            <div className="text-center pb-3 border-b border-slate-300/80 space-y-1">
              <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                {fullName.toUpperCase()}
              </h2>
              <div className="text-[11px] text-slate-600 font-medium flex flex-wrap justify-center gap-x-2 gap-y-0.5">
                <span>{email}</span>
                <span>•</span>
                <span>{phone}</span>
                {location && (
                  <>
                    <span>•</span>
                    <span>{location}</span>
                  </>
                )}
                {linkedin && (
                  <>
                    <span>•</span>
                    <span>{linkedin}</span>
                  </>
                )}
                {github && (
                  <>
                    <span>•</span>
                    <span>{github}</span>
                  </>
                )}
              </div>
            </div>

            {/* Render sections according to dynamic sectionOrder */}
            {sectionOrder.map((secName) => {
              if (secName === 'summary' && summary) {
                return (
                  <div key="summary" className="space-y-1">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Professional Summary
                    </h3>
                    <p className="text-slate-700 leading-relaxed text-[11px]">{summary}</p>
                  </div>
                );
              }

              if (secName === 'skills') {
                return (
                  <div key="skills" className="space-y-1">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Technical Skills
                    </h3>
                    <div className="space-y-0.5 text-[11px] text-slate-700">
                      {skillsLanguages && (
                        <div>
                          <span className="font-bold text-slate-900">Languages: </span>
                          <span>{skillsLanguages}</span>
                        </div>
                      )}
                      {skillsFrameworks && (
                        <div>
                          <span className="font-bold text-slate-900">Frameworks: </span>
                          <span>{skillsFrameworks}</span>
                        </div>
                      )}
                      {skillsDatabases && (
                        <div>
                          <span className="font-bold text-slate-900">Databases: </span>
                          <span>{skillsDatabases}</span>
                        </div>
                      )}
                      {skillsTools && (
                        <div>
                          <span className="font-bold text-slate-900">Tools & Cloud: </span>
                          <span>{skillsTools}</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              }

              if (secName === 'experience' && experience.length > 0) {
                return (
                  <div key="experience" className="space-y-2">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Work Experience
                    </h3>
                    <div className="space-y-2.5">
                      {experience.map((exp, i) => (
                        <div key={i} className="space-y-0.5">
                          <div className="flex items-baseline justify-between">
                            <span className="font-bold text-slate-900 text-[11px]">
                              {exp.role} — <span className="font-semibold text-slate-800">{exp.company}</span>
                            </span>
                            <span className="text-[10px] text-slate-500 italic">{exp.duration}</span>
                          </div>
                          <ul className="list-disc list-outside pl-4 space-y-0.5 text-[10.5px] text-slate-700">
                            {exp.highlights.map((h, hIdx) => (
                              <li key={hIdx} className="leading-snug">
                                {h}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              if (secName === 'internships' && internships.length > 0) {
                return (
                  <div key="internships" className="space-y-2">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Internship Experience
                    </h3>
                    <div className="space-y-2.5">
                      {internships.map((intern, i) => (
                        <div key={i} className="space-y-0.5">
                          <div className="flex items-baseline justify-between">
                            <span className="font-bold text-slate-900 text-[11px]">
                              {intern.role} — <span className="font-semibold text-slate-800">{intern.company}</span>
                            </span>
                            <span className="text-[10px] text-slate-500 italic">{intern.duration}</span>
                          </div>
                          <ul className="list-disc list-outside pl-4 space-y-0.5 text-[10.5px] text-slate-700">
                            {intern.highlights.map((h, hIdx) => (
                              <li key={hIdx} className="leading-snug">
                                {h}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              if (secName === 'projects' && projects.length > 0) {
                return (
                  <div key="projects" className="space-y-2">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Key Technical Projects
                    </h3>
                    <div className="space-y-2">
                      {projects.map((p, i) => (
                        <div key={i} className="space-y-0.5">
                          <div className="font-bold text-slate-900 text-[11px]">
                            {p.name}{' '}
                            {p.technologies && (
                              <span className="font-normal text-slate-600 text-[10px]">
                                ({p.technologies})
                              </span>
                            )}
                          </div>
                          <p className="text-[10.5px] text-slate-700 pl-3 border-l-2 border-slate-200">
                            {p.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              if (secName === 'education' && education.length > 0) {
                return (
                  <div key="education" className="space-y-1">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Education
                    </h3>
                    <div className="space-y-1 text-[11px]">
                      {education.map((edu, i) => (
                        <div key={i} className="flex items-baseline justify-between">
                          <span>
                            <span className="font-bold text-slate-900">{edu.degree}</span> — {edu.institution}
                          </span>
                          <span className="text-[10px] text-slate-500">{edu.year}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              if (secName === 'certifications' && certificationsText.trim()) {
                return (
                  <div key="certifications" className="space-y-1">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Certifications
                    </h3>
                    <ul className="list-disc list-outside pl-4 space-y-0.5 text-[10.5px] text-slate-700">
                      {certificationsText.split('\n').filter(Boolean).map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                );
              }

              if (secName === 'achievements' && achievementsText.trim()) {
                return (
                  <div key="achievements" className="space-y-1">
                    <h3 className="font-black text-slate-900 text-[11px] uppercase tracking-wider border-b border-slate-200 pb-0.5">
                      Achievements & Honors
                    </h3>
                    <ul className="list-disc list-outside pl-4 space-y-0.5 text-[10.5px] text-slate-700">
                      {achievementsText.split('\n').filter(Boolean).map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                );
              }

              return null;
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeBuilderPage;
