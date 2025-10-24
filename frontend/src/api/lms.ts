import { apiClient } from "./client";

export interface ClassroomConnectionResponse {
  id: string;
  provider: string;
  created_at: string;
  expires_at?: string | null;
  profile?: Record<string, string> | null;
}

export interface ClassroomPushResponse {
  id: string;
  status: string;
  external_assignment_id?: string | null;
  created_at: string;
}

export const connectGoogleClassroom = async () => {
  const { data } = await apiClient.post<ClassroomConnectionResponse>(
    "/lms/google-classroom/connect",
    {
      access_token: "stub-access-token",
      refresh_token: "stub-refresh-token",
      expires_in: 3600,
      profile: { teacher: "You" }
    }
  );
  return data;
};

export const pushGoogleClassroomAssignment = async (
  lessonId: string,
  params: { courseId: string; topicId?: string; dueDate?: string }
) => {
  const { data } = await apiClient.post<ClassroomPushResponse>(
    "/lms/google-classroom/push",
    {
      lesson_id: lessonId,
      course_id: params.courseId,
      topic_id: params.topicId,
      due_date: params.dueDate
    }
  );
  return data;
};
