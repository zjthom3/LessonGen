import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createLesson,
  createLessonShare,
  createLessonVersion,
  differentiateLesson,
  fetchLesson,
  fetchLessons,
  restoreLessonVersion,
  type LessonQueryParams
} from "../api/lessons";
import type {
  CreateLessonPayload,
  CreateLessonVersionPayload,
  LessonDetail,
  LessonSummary,
  LessonDifferentiatePayload,
  ShareCreateRequest
} from "../types/api";

const lessonsKey = (filters: LessonQueryParams) => ["lessons", filters];
const lessonDetailKey = (lessonId: string) => ["lessons", lessonId];

export const useLessons = (filters: LessonQueryParams) => {
  return useQuery({
    queryKey: lessonsKey(filters),
    queryFn: () => fetchLessons(filters)
  });
};

export const useLesson = (lessonId: string) => {
  return useQuery({
    queryKey: lessonDetailKey(lessonId),
    queryFn: () => fetchLesson(lessonId),
    enabled: Boolean(lessonId)
  });
};

export const useCreateLesson = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateLessonPayload) => createLesson(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lessons"] });
    }
  });
};

export const useCreateLessonVersion = (lessonId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateLessonVersionPayload) =>
      createLessonVersion(lessonId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: lessonDetailKey(lessonId) });
      queryClient.invalidateQueries({ queryKey: ["lessons"] });
    }
  });
};

export const useRestoreLessonVersion = (lessonId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (versionNo: number) => restoreLessonVersion(lessonId, versionNo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: lessonDetailKey(lessonId) });
      queryClient.invalidateQueries({ queryKey: ["lessons"] });
    }
  });
};

export const useDifferentiateLesson = (lessonId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LessonDifferentiatePayload) =>
      differentiateLesson(lessonId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: lessonDetailKey(lessonId) });
      queryClient.invalidateQueries({ queryKey: ["lessons"] });
    }
  });
};

export const useCreateLessonShare = (lessonId: string) => {
  return useMutation({
    mutationFn: (payload: ShareCreateRequest) => createLessonShare(lessonId, payload)
  });
};
