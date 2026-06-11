import { useQuery } from "@tanstack/react-query";
import { customersApi } from "@/api/customers";

export function useCustomers(params: { page: number; limit: number; search?: string; category?: string }) {
  return useQuery({
    queryKey: ["customers", params],
    queryFn: () => customersApi.getCustomers(params),
    staleTime: 30 * 1000,
  });
}

export function useCustomer(id: string | undefined) {
  return useQuery({
    queryKey: ["customer", id],
    queryFn: () => customersApi.getCustomer(id!),
    enabled: !!id,
  });
}

export function useCustomerCalls(id: string | undefined) {
  return useQuery({
    queryKey: ["customerCalls", id],
    queryFn: () => customersApi.getCustomerCalls(id!),
    enabled: !!id,
  });
}

export function useCustomerLeads(id: string | undefined) {
  return useQuery({
    queryKey: ["customerLeads", id],
    queryFn: () => customersApi.getCustomerLeads(id!),
    enabled: !!id,
  });
}
