// ==================== Auth Types ====================
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: "owner" | "admin" | "member";
  businessId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Business {
  id: string;
  name: string;
  category: string;
  phone: string;
  email: string;
  address?: string;
  logo?: string;
  timezone: string;
  currency: CurrencyCode;
  plan: "free" | "starter" | "pro" | "enterprise";
  createdAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  businessName: string;
  businessCategory: string;
  phone: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}

// ==================== Currency Types ====================
export type CurrencyCode = "INR" | "USD" | "EUR" | "GBP";

export interface CurrencyConfig {
  code: CurrencyCode;
  symbol: string;
  locale: string;
  label: string;
}

// ==================== Customer Types ====================
export interface Customer {
  id: string;
  name: string;
  phone: string;
  email?: string;
  avatar?: string;
  category: "new" | "returning" | "vip";
  totalCalls: number;
  totalRevenue: number;
  lastContactDate: string;
  tags: string[];
  notes?: string;
  createdAt: string;
}

// ==================== Call Types ====================
export interface Call {
  id: string;
  customerId: string;
  customerName: string;
  customerPhone: string;
  direction: "inbound" | "outbound";
  status: "missed" | "answered" | "callback" | "voicemail";
  duration: number;
  startTime: string;
  endTime?: string;
  recording?: CallRecording;
  hasRecording?: boolean;
  conversationId?: string;
  leadId?: string;
  notes?: string;
}

export interface CallRecording {
  id: string;
  callId: string;
  url: string;
  duration: number;
  fileSize: number;
  transcription?: string;
}

export interface Conversation {
  id: string;
  callId: string;
  customerId: string;
  customerName: string;
  messages: ConversationMessage[];
  sentiment: "positive" | "neutral" | "negative";
  summary?: string;
  createdAt: string;
  duration: number;
  channel: "voice" | "whatsapp" | "sms";
}

export interface ConversationMessage {
  id: string;
  role: "customer" | "ai";
  content: string;
  timestamp: string;
  sentiment?: "positive" | "neutral" | "negative";
}

// ==================== Lead Types ====================
export interface Lead {
  id: string;
  customerId: string;
  customerName: string;
  customerPhone: string;
  service: string;
  category: "hot" | "warm" | "cold";
  score: number;
  revenueEstimate: number;
  urgency: "critical" | "high" | "medium" | "low";
  status: "new" | "contacted" | "qualified" | "converted" | "lost";
  source: "missed_call" | "voicemail" | "callback" | "referral";
  notes?: string;
  nextFollowUp?: string;
  createdAt: string;
  updatedAt: string;
}

export interface RevenueScore {
  score: number;
  potential: number;
  recovered: number;
  recommendation: string;
}

// ==================== Appointment Types ====================
export interface Appointment {
  id: string;
  customerId: string;
  customerName: string;
  title: string;
  description?: string;
  date: string;
  startTime: string;
  endTime: string;
  duration: number;
  status: "scheduled" | "confirmed" | "completed" | "cancelled" | "no_show";
  location?: string;
  notes?: string;
  createdAt: string;
}

export interface CreateAppointmentRequest {
  lead_id?: string;
  customer_id: string;
  business_id: string;
  title: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
}

export interface TimeSlot {
  time: string;
  available: boolean;
}

// ==================== Notification Types ====================
export interface Notification {
  id: string;
  type: "lead" | "call" | "appointment" | "insight" | "system";
  title: string;
  message: string;
  read: boolean;
  actionUrl?: string;
  metadata?: Record<string, string>;
  createdAt: string;
}

// ==================== Analytics Types ====================
export interface OverviewStats {
  totalLeads: number;
  totalLeadsTrend: number;
  hotLeads: number;
  hotLeadsTrend: number;
  revenueRecovered: number;
  revenueRecoveredTrend: number;
  recoveryRate: number;
  recoveryRateTrend: number;
  totalCalls: number;
  missedCalls: number;
  totalCustomers: number;
  appointmentsToday: number;
}

export interface RevenuePrediction {
  date: string;
  predicted: number;
  actual: number;
  potential: number;
}

export interface TrendData {
  date: string;
  leads: number;
  conversions: number;
  revenue: number;
  calls: number;
}

export interface FunnelStage {
  stage: string;
  count: number;
  percentage: number;
  dropOff: number;
}

export interface LeadDistribution {
  category: string;
  count: number;
  percentage: number;
  color: string;
}

export interface AnalyticsEvent {
  id: string;
  type: string;
  description: string;
  value?: number;
  metadata?: Record<string, string>;
  createdAt: string;
}

export interface AIInsight {
  id: string;
  type: "recommendation" | "warning" | "opportunity" | "trend";
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  actionLabel?: string;
  actionUrl?: string;
  metadata?: Record<string, string | number>;
  createdAt: string;
}

// ==================== Pagination Types ====================
export interface PaginationParams {
  page: number;
  limit: number;
  search?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// ==================== Team Types ====================
export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: "owner" | "admin" | "member";
  avatar?: string;
  status: "active" | "invited" | "disabled";
  joinedAt: string;
}

// ==================== Settings Types ====================
export interface BusinessSettings {
  business: Business;
  notifications: NotificationPreferences;
  apiConfig: APIConfig;
}

export interface NotificationPreferences {
  emailLeads: boolean;
  emailCalls: boolean;
  emailAppointments: boolean;
  pushLeads: boolean;
  pushCalls: boolean;
  pushAppointments: boolean;
  dailyDigest: boolean;
  weeklyReport: boolean;
}

export interface APIConfig {
  webhookUrl?: string;
  apiKey?: string;
  calendarIntegration?: "google" | "outlook" | "none";
  crmIntegration?: "salesforce" | "hubspot" | "none";
}
