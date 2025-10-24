import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  connectGoogleClassroom,
  pushGoogleClassroomAssignment
} from "../api/lms";

export const useConnectGoogleClassroom = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: connectGoogleClassroom,
    onSuccess: (data) => {
      queryClient.setQueryData(["lms", "classroom", "connection"], data);
    }
  });
};

export const usePushGoogleClassroom = (lessonId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: { courseId: string; topicId?: string; dueDate?: string }) =>
      pushGoogleClassroomAssignment(lessonId, params),
    onSuccess: (data) => {
      const key = ["lms", "classroom", "pushes", lessonId];
      const current = (queryClient.getQueryData(key) as typeof data[] | undefined) ?? [];
      queryClient.setQueryData(key, [data, ...current]);
    }
  });
};
