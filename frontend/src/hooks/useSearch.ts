import { useQuery } from "@tanstack/react-query";
import { searchApi } from "@/api/search";

export function useGlobalSearch(query: string) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: () => searchApi.globalSearch(query),
    enabled: query.length >= 2,
    staleTime: 10 * 1000,
  });
}
