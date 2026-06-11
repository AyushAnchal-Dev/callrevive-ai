import apiClient from "./client";
import type { Customer, Call, Lead, PaginatedResponse, PaginationParams } from "@/types";
import { mapCall } from "./calls";
import { mapLead } from "./leads";

export const mapCustomer = (c: any): Customer => ({
  id: c.id,
  name: c.name || "Unknown Customer",
  phone: c.phone_number || "",
  email: c.email || undefined,
  category: (c.category || "new") as "new" | "returning" | "vip",
  totalCalls: c.total_calls || 0,
  totalRevenue: Number(c.total_revenue || 0),
  lastContactDate: c.last_contact_at || c.created_at || "",
  tags: c.category ? [c.category.toUpperCase()] : [],
  notes: c.metadata?.notes || "",
  createdAt: c.created_at || "",
});

export const customersApi = {
  getCustomers: async (params: PaginationParams & { category?: string }): Promise<PaginatedResponse<Customer>> => {
    const response = await apiClient.get<any>("/customers", {
      params: {
        page: params.page,
        page_size: params.limit,
        search: params.search,
        category: params.category === "all" ? undefined : params.category,
      }
    });
    return {
      data: (response.data.items || []).map(mapCustomer),
      total: response.data.total || 0,
      page: response.data.page || 1,
      limit: response.data.page_size || 20,
      totalPages: response.data.pages || 1,
    };
  },

  getCustomer: async (id: string): Promise<Customer> => {
    const response = await apiClient.get<any>(`/customers/${id}`);
    return mapCustomer(response.data);
  },

  getCustomerCalls: async (customerId: string): Promise<Call[]> => {
    const response = await apiClient.get<any[]>(`/customers/${customerId}/calls`);
    return (response.data || []).map(mapCall);
  },

  getCustomerLeads: async (customerId: string): Promise<Lead[]> => {
    const response = await apiClient.get<any[]>(`/customers/${customerId}/leads`);
    return (response.data || []).map(mapLead);
  },
};
