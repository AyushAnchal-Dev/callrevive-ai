import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import type { LoginRequest, RegisterRequest } from "@/types";

export function useAuth() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { login: storeLogin, logout: storeLogout, isAuthenticated } = useAuthStore();

  const currentUserQuery = useQuery({
    queryKey: ["currentUser"],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      storeLogin(
        response.user,
        response.tokens.accessToken,
        response.tokens.refreshToken
      );
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      navigate("/dashboard");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      storeLogin(
        response.user,
        response.tokens.accessToken,
        response.tokens.refreshToken
      );
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      navigate("/dashboard");
    },
  });

  const forgotPasswordMutation = useMutation({
    mutationFn: (email: string) => authApi.forgotPassword({ email }),
  });

  const logout = () => {
    storeLogout();
    queryClient.clear();
    navigate("/login");
  };

  return {
    user: currentUserQuery.data,
    isAuthenticated,
    isLoading: currentUserQuery.isLoading,
    loginMutation,
    registerMutation,
    forgotPasswordMutation,
    logout,
  };
}
