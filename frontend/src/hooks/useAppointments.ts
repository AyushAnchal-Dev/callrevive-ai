import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { appointmentsApi } from "@/api/appointments";
import type { CreateAppointmentRequest } from "@/types";

export function useAppointments(params?: { status?: string; date?: string; page?: number; limit?: number }) {
  return useQuery({
    queryKey: ["appointments", params],
    queryFn: () => appointmentsApi.getAppointments({ page: params?.page || 1, limit: params?.limit || 50, ...params }),
    staleTime: 30 * 1000,
  });
}

export function useCreateAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateAppointmentRequest) => appointmentsApi.createAppointment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
  });
}

export function useUpdateAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<any> }) => appointmentsApi.updateAppointment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
  });
}

export function useDeleteAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => appointmentsApi.deleteAppointment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
  });
}

export function useAvailableSlots(date: string | undefined) {
  return useQuery({
    queryKey: ["availableSlots", date],
    queryFn: () => appointmentsApi.getAvailableSlots(date!),
    enabled: !!date,
  });
}
