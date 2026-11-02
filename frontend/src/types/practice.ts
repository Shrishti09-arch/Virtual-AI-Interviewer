export interface QuestionBankItem {
  id: number;
  title: string;
  category: string;
  subject: string;
  programming_language?: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  question_type: 'MCQ' | 'Theory' | 'Coding' | 'Scenario';
  question_text: string;
  mcq_options?: string[];
  correct_option_index?: number;
  explanation?: string;
  code_template?: string;
  test_cases?: Array<{ input: string; expected_output: string; hidden?: boolean }>;
  hints?: string[];
  sample_answer?: string;
  source_type: 'ai_generated' | 'curated_standard';
  source_name: string;
  source_url?: string;
}

export interface PracticeEvaluationResult {
  session_id?: number;
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
  passed_tests?: number;
  total_tests?: number;
  error?: string;
  is_fallback?: boolean;
}

export interface PracticeFinalReport {
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
}
