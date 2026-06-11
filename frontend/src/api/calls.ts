import apiClient from "./client";
import type { Call, CallRecording, PaginatedResponse, PaginationParams } from "@/types";

export const mapCall = (c: any): Call => {
  let status: "missed" | "answered" | "callback" | "voicemail" = "missed";
  if (c.status === "answered" || c.status === "callback_completed") {
    status = "answered";
  } else if (c.status === "callback_initiated") {
    status = "callback";
  }

  return {
    id: c.id,
    customerId: c.customer_id,
    customerName: c.customer_name || "Unknown",
    customerPhone: c.direction === "inbound" ? c.from_number : c.to_number,
    direction: c.direction as "inbound" | "outbound",
    status,
    duration: c.duration_seconds || 0,
    startTime: c.started_at || c.created_at || "",
    endTime: c.ended_at || undefined,
    hasRecording: c.has_recording || false,
  };
};

export const callsApi = {
  getCalls: async (params: PaginationParams & { status?: string }): Promise<PaginatedResponse<Call>> => {
    const response = await apiClient.get<any>("/calls", {
      params: {
        page: params.page,
        page_size: params.limit,
        status: params.status === "All" ? undefined : params.status?.toLowerCase(),
      }
    });
    return {
      data: (response.data.items || []).map(mapCall),
      total: response.data.total || 0,
      page: response.data.page || 1,
      limit: response.data.page_size || 20,
      totalPages: response.data.pages || 1,
    };
  },

  getCall: async (id: string): Promise<Call> => {
    const response = await apiClient.get<any>(`/calls/${id}`);
    return mapCall(response.data);
  },

  getCallRecording: async (callId: string): Promise<CallRecording> => {
    const response = await apiClient.get<any>(`/calls/${callId}/recording`);
    return {
      id: response.data.id,
      callId: response.data.call_id,
      url: response.data.storage_url,
      duration: response.data.duration_seconds,
      fileSize: response.data.file_size_bytes,
      transcription: response.data.transcription || "",
    };
  },

  initiateCallback: async (callId: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(`/calls/${callId}/callback`);
    return response.data;
  },
};
