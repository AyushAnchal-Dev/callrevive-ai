import { useQuery } from "@tanstack/react-query";
import { conversationsApi } from "@/api/conversations";
import type { PaginationParams } from "@/types";

export function useConversations(params: PaginationParams) {
  return useQuery({
    queryKey: ["conversations", params],
    queryFn: () => conversationsApi.getConversations(params),
    staleTime: 30 * 1000,
  });
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: ["conversation", id],
    queryFn: () => conversationsApi.getConversation(id),
    enabled: !!id,
  });
}
