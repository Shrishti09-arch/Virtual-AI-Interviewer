export interface MilestoneChecklistItem {
  id: string;
  task: string;
  is_done: boolean;
  category?: string;
}

export interface MilestonePhaseItem {
  id: number;
  phase_number: number;
  title: string;
  duration: string;
  estimated_hours: number;
  phase_progress: number;
  is_completed: boolean;
  topics: string[];
  free_resources: Array<{ title: string; url: string; type: string }>;
  practice_tasks: string[];
  recommended_project: {
    title: string;
    description: string;
    stack: string[];
  };
  interview_prep_questions: string[];
  checklist: MilestoneChecklistItem[];
}

export interface CareerRoadmapData {
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
  milestones: MilestonePhaseItem[];
  created_at: string;
}
