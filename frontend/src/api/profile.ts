import { apiClient } from "./client";
import type { UpdateProfilePayload, User } from "../types/api";

export const updateProfile = async (payload: UpdateProfilePayload): Promise<User> => {
  const { data } = await apiClient.put<User>("/me", payload);
  return data;
};
