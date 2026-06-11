import apiClient from "./client";
import type {
  OverviewStats,
  TrendData,
  FunnelStage,
  RevenuePrediction,
  LeadDistribution,
} from "@/types";

export const analyticsApi = {
  getOverview: async (): Promise<OverviewStats> => {
    const response = await apiClient.get<any>("/analytics/overview");
    const d = response.data;
    return {
      totalLeads: d.total_leads || 0,
      totalLeadsTrend: d.total_leads_trend ?? 0,
      hotLeads: d.hot_leads || 0,
      hotLeadsTrend: d.hot_leads_trend ?? 0,
      revenueRecovered: Number(d.total_revenue_recovered || 0),
      revenueRecoveredTrend: d.revenue_recovered_trend ?? 0,
      recoveryRate: d.recovery_rate || 0,
      recoveryRateTrend: d.recovery_rate_trend ?? 0,
      totalCalls: d.total_calls || 0,
      missedCalls: d.missed_calls || 0,
      totalCustomers: d.total_leads || 0,
      appointmentsToday: d.active_conversations || 0,
    };
  },

  getLeadAnalytics: async (): Promise<LeadDistribution[]> => {
    const response = await apiClient.get<any>("/analytics/leads");
    const catMap = response.data.leads_by_category || {};
    const total = (Object.values(catMap).reduce((a: any, b: any) => a + b, 0) as number) || 1;
    return [
      { category: "hot", count: catMap.hot || 0, percentage: Math.round(((catMap.hot || 0) / total) * 100), color: "bg-rose-500" },
      { category: "warm", count: catMap.warm || 0, percentage: Math.round(((catMap.warm || 0) / total) * 100), color: "bg-amber-500" },
      { category: "cold", count: catMap.cold || 0, percentage: Math.round(((catMap.cold || 0) / total) * 100), color: "bg-slate-500" },
    ];
  },

  getRevenueAnalytics: async (
    period?: string
  ): Promise<RevenuePrediction[]> => {
    const response = await apiClient.get<any>("/analytics/revenue", {
      params: { period },
    });
    return response.data.monthly_data || [];
  },

  getTrends: async (
    period?: string
  ): Promise<TrendData[]> => {
    const response = await apiClient.get<any[]>("/analytics/trends", {
      params: { period },
    });
    return (response.data || []).map((t: any) => ({
      date: t.date,
      leads: t.leads,
      conversions: t.conversions,
      revenue: Number(t.revenue || 0),
      calls: t.calls,
    }));
  },

  getConversionFunnel: async (): Promise<FunnelStage[]> => {
    const response = await apiClient.get<any>("/analytics/conversion-funnel");
    const d = response.data;
    return [
      { stage: "Missed Calls", count: d.missed_calls || 0, percentage: 100, dropOff: 0 },
      { stage: "Contacted", count: d.contacted || 0, percentage: d.contact_rate || 0, dropOff: 100 - (d.contact_rate || 0) },
      { stage: "Qualified", count: d.qualified || 0, percentage: d.qualification_rate || 0, dropOff: 100 - (d.qualification_rate || 0) },
      { stage: "Converted", count: d.converted || 0, percentage: d.conversion_rate || 0, dropOff: 100 - (d.conversion_rate || 0) },
    ];
  },

  getAIInsights: async (): Promise<any> => {
    const response = await apiClient.post<any>("/analytics/ai-insights");
    return response.data;
  },
};
