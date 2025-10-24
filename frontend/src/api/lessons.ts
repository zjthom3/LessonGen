import { apiClient } from "./client";
import type {
  CreateLessonPayload,
  CreateLessonVersionPayload,
  LessonDetail,
  LessonSummary,
  LessonVersion,
  LessonDifferentiatePayload,
  ShareCreateRequest,
  ShareCreateResponse
} from "../types/api";

export interface LessonQueryParams {
  subject?: string;
  grade_level?: string;
  tags?: string[];
}

export const fetchLessons = async (params: LessonQueryParams = {}): Promise<LessonSummary[]> => {
  const { data } = await apiClient.get<LessonSummary[]>("/lessons", { params });
  return data;
};

export const fetchLesson = async (lessonId: string): Promise<LessonDetail> => {
  const { data } = await apiClient.get<LessonDetail>(`/lessons/${lessonId}`);
  return data;
};

export const createLesson = async (payload: CreateLessonPayload): Promise<LessonDetail> => {
  const { data } = await apiClient.post<LessonDetail>("/lessons", payload);
  return data;
};

export const createLessonVersion = async (
  lessonId: string,
  payload: CreateLessonVersionPayload
) => {
  const { data } = await apiClient.post(`/lessons/${lessonId}/versions`, payload);
  return data;
};

export const restoreLessonVersion = async (
  lessonId: string,
  versionNo: number
): Promise<{ lesson_id: string; current_version_id: string; restored_version: number }> => {
  const { data } = await apiClient.post(
    `/lessons/${lessonId}/restore/${versionNo}`
  );
  return data;
};

export const downloadLessonExport = async (
  lessonId: string,
  format: "pdf" | "docx" | "gdoc"
): Promise<Blob> => {
  const response = await apiClient.get(`/lessons/${lessonId}/export`, {
    params: { format },
    responseType: "blob"
  });
  return response.data;
};

export const fetchGDocExport = async (lessonId: string) => {
  const { data } = await apiClient.get(`/lessons/${lessonId}/export`, {
    params: { format: "gdoc" }
  });
  return data;
};

export const differentiateLesson = async (
  lessonId: string,
  payload: LessonDifferentiatePayload
): Promise<LessonVersion> => {
  const { data } = await apiClient.post<LessonVersion>(
    `/lessons/${lessonId}/differentiate`,
    payload
  );
  return data;
};

export const createLessonShare = async (
  lessonId: string,
  payload: ShareCreateRequest
): Promise<ShareCreateResponse> => {
  const { data } = await apiClient.post<ShareCreateResponse>(
    `/lessons/${lessonId}/share`,
    payload
  );
  return data;
};
