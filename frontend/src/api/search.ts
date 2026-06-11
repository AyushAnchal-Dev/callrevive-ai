import apiClient from "./client";

export interface SearchResults {
  customers: Array<{ id: string; name: string; phone: string; type: string }>;
  leads: Array<{ id: string; name: string; service: string; category: string; type: string }>;
  conversations: Array<{ id: string; summary: string; channel: string; customer_name: string; type: string }>;
}

export const searchApi = {
  globalSearch: async (query: string): Promise<SearchResults> => {
    const response = await apiClient.get<SearchResults>("/search", {
      params: { q: query },
    });
    return response.data;
  },
};
