import apiClient from "./client";
import type { Lead, PaginatedResponse, PaginationParams, RevenueScore } from "@/types";

export const mapLead = (l: any): Lead => ({
  id: l.id,
  customerId: l.customer_id,
  customerName: l.customer_name || "Unknown Customer",
  customerPhone: l.customer_phone || "",
  service: l.service_requested || "General Inquiry",
  category: (l.category || "warm") as "hot" | "warm" | "cold",
  score: l.lead_score || 50,
  revenueEstimate: Number(l.estimated_revenue || 0),
  urgency: (l.urgency ? l.urgency.charAt(0).toUpperCase() + l.urgency.slice(1).toLowerCase() : "Medium") as any,
  status: (l.status || "new") as any,
  source: "missed_call",
  notes: l.qualification_notes || "",
  createdAt: l.created_at || "",
  updatedAt: l.updated_at || "",
});

export const leadsApi = {
  getLeads: async (params: PaginationParams & { category?: string; status?: string }): Promise<PaginatedResponse<Lead>> => {
    const response = await apiClient.get<any>("/leads", {
      params: {
        page: params.page,
        page_size: params.limit,
        category: params.category,
        status: params.status,
      }
    });
    return {
      data: (response.data.items || []).map(mapLead),
      total: response.data.total || 0,
      page: response.data.page || 1,
      limit: response.data.page_size || 20,
      totalPages: response.data.pages || 1,
    };
  },

  getLead: async (id: string): Promise<Lead> => {
    const response = await apiClient.get<any>(`/leads/${id}`);
    return mapLead(response.data);
  },

  updateLeadStatus: async (id: string, status: string): Promise<Lead> => {
    const response = await apiClient.put<any>(`/leads/${id}/status`, { status });
    return mapLead(response.data);
  },

  getHotLeads: async (): Promise<Lead[]> => {
    const response = await apiClient.get<any[]>("/leads/hot");
    return (response.data || []).map(mapLead);
  },

  getLeadRevenueScore: async (id: string): Promise<RevenueScore> => {
    const response = await apiClient.get<any>(`/leads/${id}/revenue-score`);
    return {
      score: response.data.revenue_score || 50,
      potential: Number(response.data.estimated_revenue || 0),
      recovered: response.data.status === "converted" ? Number(response.data.estimated_revenue || 0) : 0,
      recommendation: response.data.recommendation || "",
    };
  },
};
