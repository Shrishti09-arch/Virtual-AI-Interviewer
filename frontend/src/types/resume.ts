export interface ResumeCorrectionItem {
  id: string;
  original_text: string;
  corrected_text: string;
  category: string;
  explanation: string;
  action_verb_used?: string;
  status: 'pending' | 'accepted' | 'rejected';
}

export interface ExtractedResumeData {
  full_name: string;
  email: string;
  phone: string;
  education: Array<{ institution: string; degree: string; year: string; grade?: string }>;
  technical_skills: Record<string, string[]>;
  work_experience: Array<{ company: string; role: string; duration: string; highlights: string[] }>;
  internships: Array<{ company: string; role: string; duration: string; highlights: string[] }>;
  projects: Array<{ name: string; description: string; technologies: string[]; link?: string }>;
  certifications: string[];
  achievements: string[];
  summary?: string;
}

export interface ResumeAnalysisData {
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
  grammar_errors: string[];
  weak_sentences: string[];
  formatting_issues: string[];
  action_verb_suggestions: string[];
  improvement_recommendations: string[];
  corrections: ResumeCorrectionItem[];
  section_breakdown: Record<string, any>;
  readability_metrics: Record<string, any>;
  extracted_data?: ExtractedResumeData;
  disclaimer: string;
  detailed_feedback: string;
  created_at: string;
}
