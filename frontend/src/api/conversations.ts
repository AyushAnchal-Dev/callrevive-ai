import apiClient from "./client";
import type { Conversation, PaginatedResponse, PaginationParams } from "@/types";

export const mapConversation = (c: any): Conversation => ({
  id: c.id,
  callId: c.call_id || "",
  customerId: c.customer_id,
  customerName: c.customer_name || "Unknown",
  messages: (c.messages || []).map((m: any, idx: number) => ({
    id: m.id || String(idx),
    role: m.role === "customer" ? "customer" : "ai",
    content: m.content || "",
    timestamp: m.timestamp || new Date().toISOString(),
  })),
  sentiment: "neutral",
  summary: c.ai_summary || "",
  createdAt: c.created_at || "",
  duration: c.ended_at && c.started_at ? Math.round((new Date(c.ended_at).getTime() - new Date(c.started_at).getTime()) / 1000) : 0,
  channel: c.channel || "voice",
});

export const conversationsApi = {
  getConversations: async (
    params: PaginationParams
  ): Promise<PaginatedResponse<Conversation>> => {
    const response = await apiClient.get<any>("/conversations", {
      params: {
        page: params.page,
        page_size: params.limit,
      }
    });
    return {
      data: (response.data.items || []).map(mapConversation),
      total: response.data.total || 0,
      page: response.data.page || 1,
      limit: response.data.page_size || 20,
      totalPages: response.data.pages || 1,
    };
  },

  getConversation: async (id: string): Promise<Conversation> => {
    const response = await apiClient.get<any>(`/conversations/${id}`);
    return mapConversation(response.data);
  },
};
