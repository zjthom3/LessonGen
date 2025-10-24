export interface UserRole {
  role: string;
  scope: Record<string, unknown>;
}

export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  avatar_url?: string | null;
  locale: string;
  preferred_subjects: string[];
  preferred_grade_levels: string[];
  is_active: boolean;
  is_superuser: boolean;
  roles: UserRole[];
}

export interface AuthSessionResponse {
  authenticated: boolean;
  user: User | null;
}

export interface UpdateProfilePayload {
  full_name?: string | null;
  preferred_subjects: string[];
  preferred_grade_levels: string[];
  locale?: string | null;
}

export interface LessonVersion {
  id: string;
  lesson_id: string;
  version_no: number;
  objective?: string | null;
  duration_minutes?: number | null;
  teacher_script_md?: string | null;
  materials: Record<string, unknown>[];
  flow: Record<string, unknown>[];
  differentiation: Record<string, unknown>[];
  assessments: Record<string, unknown>[];
  accommodations: Record<string, unknown>[];
  source: Record<string, unknown>;
  created_at: string;
  created_by_user_id?: string | null;
}

export interface LessonSummary {
  id: string;
  title: string;
  subject: string;
  grade_level: string;
  language: string;
  status: string;
  tags: string[];
  visibility: string;
  current_version_id?: string | null;
  updated_at: string;
}

export interface LessonDetail extends LessonSummary {
  owner_user_id: string;
  versions: LessonVersion[];
}

export interface CreateLessonPayload {
  title: string;
  subject: string;
  grade_level: string;
  language?: string;
  tags?: string[];
  objective?: string;
  duration_minutes?: number;
  teacher_script_md?: string;
}

export interface CreateLessonVersionPayload {
  objective?: string;
  duration_minutes?: number;
  teacher_script_md?: string;
  materials?: Record<string, unknown>[];
  flow?: Record<string, unknown>[];
  differentiation?: Record<string, unknown>[];
  assessments?: Record<string, unknown>[];
  accommodations?: Record<string, unknown>[];
  status?: string;
}

export type DifferentiationAudience = "ELL" | "IEP" | "GIFTED";

export interface LessonDifferentiatePayload {
  audience: DifferentiationAudience;
  notes?: string;
}

export interface ShareCreateRequest {
  expires_in_hours?: number | null;
}

export interface ShareCreateResponse {
  token: string;
  url: string;
  expires_at?: string | null;
}

export interface AnalyticsSummary {
  lessons_created: number;
  lessons_generated: number;
  lessons_differentiated: number;
  exports: number;
  lms_pushes: number;
  total_lessons: number;
  estimated_time_saved_minutes: number;
}
