import { createContext, ReactNode, useContext, useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchSession, logout as logoutRequest } from "../api/auth";
import type { User } from "../types/api";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  status: AuthStatus;
  user: User | null;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const queryClient = useQueryClient();
  const sessionQuery = useQuery({
    queryKey: ["auth", "session"],
    queryFn: fetchSession,
    retry: false
  });

  const logoutMutation = useMutation({
    mutationFn: logoutRequest,
    onSuccess: async () => {
      queryClient.setQueryData(["auth", "session"], null);
      await queryClient.invalidateQueries({ queryKey: ["auth", "session"] });
    }
  });

  const value = useMemo<AuthContextValue>(() => {
    if (sessionQuery.isLoading) {
      return {
        status: "loading",
        user: null,
        refresh: () => sessionQuery.refetch(),
        logout: () => logoutMutation.mutateAsync()
      };
    }

    if (sessionQuery.isError) {
      return {
        status: "unauthenticated",
        user: null,
        refresh: () => sessionQuery.refetch(),
        logout: () => logoutMutation.mutateAsync()
      };
    }

    const user = sessionQuery.data ?? null;

    return {
      status: user ? "authenticated" : "unauthenticated",
      user,
      refresh: () => sessionQuery.refetch(),
      logout: () => logoutMutation.mutateAsync()
    };
  }, [logoutMutation, sessionQuery]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};
