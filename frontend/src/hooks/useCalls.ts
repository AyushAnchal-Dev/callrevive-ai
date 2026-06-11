import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { callsApi } from "@/api/calls";
import type { PaginationParams } from "@/types";

export function useCalls(params: PaginationParams & { status?: string }) {
  return useQuery({
    queryKey: ["calls", params],
    queryFn: () => callsApi.getCalls(params),
    staleTime: 30 * 1000,
  });
}

export function useCall(id: string) {
  return useQuery({
    queryKey: ["call", id],
    queryFn: () => callsApi.getCall(id),
    enabled: !!id,
  });
}

export function useCallRecording(callId: string) {
  return useQuery({
    queryKey: ["callRecording", callId],
    queryFn: () => callsApi.getCallRecording(callId),
    enabled: !!callId,
  });
}

export function useInitiateCallback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (callId: string) => callsApi.initiateCallback(callId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calls"] });
    },
  });
}
