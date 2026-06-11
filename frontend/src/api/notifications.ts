import apiClient from "./client";
import type { Notification, PaginatedResponse, PaginationParams } from "@/types";

export const notificationsApi = {
  getNotifications: async (
    params: PaginationParams & { type?: string }
  ): Promise<PaginatedResponse<Notification>> => {
    const response = await apiClient.get<PaginatedResponse<Notification>>("/notifications", { params });
    return response.data;
  },

  markAsRead: async (id: string): Promise<Notification> => {
    const response = await apiClient.put<Notification>(`/notifications/${id}/read`);
    return response.data;
  },

  markAllAsRead: async (): Promise<{ message: string }> => {
    const response = await apiClient.put<{ message: string }>("/notifications/read-all");
    return response.data;
  },

  getUnreadCount: async (): Promise<{ count: number }> => {
    const response = await apiClient.get<{ count: number }>("/notifications/unread-count");
    return response.data;
  },
};
