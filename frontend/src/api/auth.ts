import { apiClient } from "./client";
import type { AuthSessionResponse, User } from "../types/api";

export const fetchSession = async (): Promise<User | null> => {
  const { data } = await apiClient.get<AuthSessionResponse>("/auth/session");
  return data.authenticated ? data.user : null;
};

export const requestLoginUrl = async (): Promise<string> => {
  const { data } = await apiClient.get<{ authorization_url: string }>("/auth/login");
  return data.authorization_url;
};

export const logout = async (): Promise<void> => {
  await apiClient.post("/auth/logout");
};
