import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leadsApi } from "@/api/leads";
import type { PaginationParams } from "@/types";

export function useLeads(params: PaginationParams & { category?: string; status?: string }) {
  return useQuery({
    queryKey: ["leads", params],
    queryFn: () => leadsApi.getLeads(params),
    staleTime: 30 * 1000,
  });
}

export function useLead(id: string) {
  return useQuery({
    queryKey: ["lead", id],
    queryFn: () => leadsApi.getLead(id),
    enabled: !!id,
  });
}

export function useHotLeads() {
  return useQuery({
    queryKey: ["hotLeads"],
    queryFn: leadsApi.getHotLeads,
    staleTime: 60 * 1000,
  });
}

export function useUpdateLeadStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      leadsApi.updateLeadStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["hotLeads"] });
    },
  });
}

export function useLeadRevenueScore(id: string) {
  return useQuery({
    queryKey: ["leadRevenueScore", id],
    queryFn: () => leadsApi.getLeadRevenueScore(id),
    enabled: !!id,
  });
}
