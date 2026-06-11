export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const CURRENCY_OPTIONS = [
  { value: "INR", label: "₹ INR", symbol: "₹", locale: "en-IN" },
  { value: "USD", label: "$ USD", symbol: "$", locale: "en-US" },
  { value: "EUR", label: "€ EUR", symbol: "€", locale: "de-DE" },
  { value: "GBP", label: "£ GBP", symbol: "£", locale: "en-GB" },
] as const;

export const LEAD_CATEGORIES = [
  { value: "hot", label: "Hot", color: "text-rose-400", bg: "bg-rose-400/10" },
  {
    value: "warm",
    label: "Warm",
    color: "text-amber-400",
    bg: "bg-amber-400/10",
  },
  {
    value: "cold",
    label: "Cold",
    color: "text-blue-400",
    bg: "bg-blue-400/10",
  },
] as const;

export const CALL_STATUSES = [
  {
    value: "missed",
    label: "Missed",
    color: "text-rose-400",
    bg: "bg-rose-400/10",
  },
  {
    value: "answered",
    label: "Answered",
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
  },
  {
    value: "callback",
    label: "Callback",
    color: "text-amber-400",
    bg: "bg-amber-400/10",
  },
  {
    value: "voicemail",
    label: "Voicemail",
    color: "text-blue-400",
    bg: "bg-blue-400/10",
  },
] as const;

export const APPOINTMENT_STATUSES = [
  { value: "scheduled", label: "Scheduled", color: "text-blue-400" },
  { value: "confirmed", label: "Confirmed", color: "text-emerald-400" },
  { value: "completed", label: "Completed", color: "text-violet-400" },
  { value: "cancelled", label: "Cancelled", color: "text-rose-400" },
  { value: "no_show", label: "No Show", color: "text-amber-400" },
] as const;

export const NOTIFICATION_TYPES = [
  { value: "lead", label: "New Lead", icon: "UserPlus" },
  { value: "call", label: "Missed Call", icon: "PhoneMissed" },
  { value: "appointment", label: "Appointment", icon: "Calendar" },
  { value: "insight", label: "AI Insight", icon: "Sparkles" },
  { value: "system", label: "System", icon: "Settings" },
] as const;

export const BUSINESS_CATEGORIES = [
  "Healthcare",
  "Dental",
  "Legal",
  "Real Estate",
  "Automotive",
  "Home Services",
  "Beauty & Wellness",
  "Financial Services",
  "Education",
  "Hospitality",
  "Retail",
  "Other",
] as const;

export const NAV_ITEMS = [
  { path: "/dashboard", label: "Dashboard", icon: "LayoutDashboard" },
  { path: "/leads", label: "Leads", icon: "Target" },
  { path: "/customers", label: "Customers", icon: "Users" },
  { path: "/calls", label: "Calls", icon: "Phone" },
  { path: "/conversations", label: "Conversations", icon: "MessageSquare" },
  { path: "/appointments", label: "Appointments", icon: "Calendar" },
  { path: "/analytics", label: "Analytics", icon: "BarChart3" },
  { path: "/ai-insights", label: "AI Insights", icon: "Sparkles" },
  { path: "/notifications", label: "Notifications", icon: "Bell" },
  { path: "/settings", label: "Settings", icon: "Settings" },
] as const;

export const DEFAULT_CURRENCY = "INR";

export const ITEMS_PER_PAGE = 10;
