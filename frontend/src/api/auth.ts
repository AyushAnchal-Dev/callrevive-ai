import apiClient from "./client";
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  User,
  TokenResponse,
} from "@/types";

const mapUser = (backendUser: any): User => {
  return {
    id: backendUser.id,
    email: backendUser.email,
    name: backendUser.full_name || "",
    role: backendUser.role,
    businessId: backendUser.business_id || "",
    createdAt: backendUser.created_at || "",
    updatedAt: backendUser.updated_at || "",
  };
};

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const tokenResponse = await apiClient.post<any>("/auth/login", data);
    const { access_token, refresh_token, expires_in } = tokenResponse.data;

    localStorage.setItem("accessToken", access_token);
    localStorage.setItem("refreshToken", refresh_token);

    const userResponse = await apiClient.get<any>("/auth/me");
    return {
      user: mapUser(userResponse.data),
      tokens: {
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresIn: expires_in || 1800,
      },
    };
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const tokenResponse = await apiClient.post<any>("/auth/register", data);
    const { access_token, refresh_token, expires_in } = tokenResponse.data;

    localStorage.setItem("accessToken", access_token);
    localStorage.setItem("refreshToken", refresh_token);

    const userResponse = await apiClient.get<any>("/auth/me");
    return {
      user: mapUser(userResponse.data),
      tokens: {
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresIn: expires_in || 1800,
      },
    };
  },

  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<any>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    const { access_token, refresh_token: new_refresh, expires_in } = response.data;
    return {
      accessToken: access_token,
      refreshToken: new_refresh,
      expiresIn: expires_in || 1800,
    };
  },

  forgotPassword: async (
    data: ForgotPasswordRequest
  ): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      "/auth/forgot-password",
      data
    );
    return response.data;
  },

  resetPassword: async (
    data: ResetPasswordRequest
  ): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      "/auth/reset-password",
      data
    );
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<any>("/auth/me");
    return mapUser(response.data);
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout");
  },
};
