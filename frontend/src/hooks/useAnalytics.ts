import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/api/analytics";

export function useOverview() {
  return useQuery({
    queryKey: ["analyticsOverview"],
    queryFn: analyticsApi.getOverview,
    staleTime: 60 * 1000,
  });
}

export function useLeadAnalytics() {
  return useQuery({
    queryKey: ["leadAnalytics"],
    queryFn: analyticsApi.getLeadAnalytics,
    staleTime: 60 * 1000,
  });
}

export function useRevenueAnalytics(period?: string) {
  return useQuery({
    queryKey: ["revenueAnalytics", period],
    queryFn: () => analyticsApi.getRevenueAnalytics(period),
    staleTime: 60 * 1000,
  });
}

export function useTrends(period?: string) {
  return useQuery({
    queryKey: ["trends", period],
    queryFn: () => analyticsApi.getTrends(period),
    staleTime: 60 * 1000,
  });
}

export function useConversionFunnel() {
  return useQuery({
    queryKey: ["conversionFunnel"],
    queryFn: analyticsApi.getConversionFunnel,
    staleTime: 60 * 1000,
  });
}
