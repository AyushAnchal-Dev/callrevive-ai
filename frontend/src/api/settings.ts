import apiClient from "./client";

export const settingsApi = {
  getSettings: async (): Promise<any> => {
    const response = await apiClient.get<any>("/settings");
    return response.data;
  },

  updateSettings: async (data: Record<string, any>): Promise<any> => {
    const response = await apiClient.put<any>("/settings", data);
    return response.data;
  },

  updateNotificationPreferences: async (data: Record<string, any>): Promise<any> => {
    const response = await apiClient.put<any>("/settings/notifications", data);
    return response.data;
  },
};
