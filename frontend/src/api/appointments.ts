import apiClient from "./client";
import type {
  Appointment,
  CreateAppointmentRequest,
  PaginatedResponse,
  PaginationParams,
  TimeSlot,
} from "@/types";

export const appointmentsApi = {
  getAppointments: async (
    params: PaginationParams & { status?: string; date?: string }
  ): Promise<PaginatedResponse<Appointment>> => {
    const response = await apiClient.get<PaginatedResponse<Appointment>>("/appointments", { params });
    return response.data;
  },

  createAppointment: async (data: CreateAppointmentRequest): Promise<Appointment> => {
    const response = await apiClient.post<Appointment>("/appointments", data);
    return response.data;
  },

  updateAppointment: async (id: string, data: Partial<Appointment>): Promise<Appointment> => {
    const response = await apiClient.put<Appointment>(`/appointments/${id}`, data);
    return response.data;
  },

  deleteAppointment: async (id: string): Promise<void> => {
    await apiClient.delete(`/appointments/${id}`);
  },

  getAvailableSlots: async (date: string): Promise<TimeSlot[]> => {
    const response = await apiClient.get<TimeSlot[]>("/appointments/available-slots", {
      params: { date },
    });
    return response.data;
  },
};
