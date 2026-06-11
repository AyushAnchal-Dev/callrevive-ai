import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Target,
  Users,
  Phone,
  MessageSquare,
  Calendar,
  BarChart3,
  Sparkles,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  Phone as PhoneIcon,
  LogOut,
  Github,
  Linkedin,
  Mail,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { useUnreadCount } from "@/hooks/useNotifications";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { getInitials } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/leads", label: "Leads", icon: Target },
  { path: "/customers", label: "Customers", icon: Users },
  { path: "/calls", label: "Calls", icon: Phone },
  { path: "/conversations", label: "Conversations", icon: MessageSquare },
  { path: "/appointments", label: "Appointments", icon: Calendar },
  { path: "/analytics", label: "Analytics", icon: BarChart3 },
  { path: "/ai-insights", label: "AI Insights", icon: Sparkles },
  { path: "/notifications", label: "Notifications", icon: Bell },
  { path: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { sidebarCollapsed, toggleSidebar, user, logout } = useAuthStore();
  const { data: unreadData } = useUnreadCount();
  const unreadCount = unreadData?.count ?? 0;

  const displayName = user?.name || "Admin User";
  const displayRole = user?.role || "owner";

  return (
    <TooltipProvider delayDuration={0}>
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 72 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="fixed left-0 top-0 z-40 h-screen flex flex-col border-r border-white/[0.06] bg-[#0d0d1a]/95 backdrop-blur-xl"
      >
        {/* Brand */}
        <div className="flex h-16 items-center gap-3 px-4 border-b border-white/[0.06]">
          <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/25">
            <PhoneIcon className="h-4 w-4 text-white" />
            <Sparkles className="absolute -right-1 -top-1 h-3 w-3 text-amber-400" />
          </div>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="flex flex-col overflow-hidden"
              >
                <span className="text-sm font-bold gradient-text">
                  CallRevive
                </span>
                <span className="text-[10px] text-muted-foreground font-medium tracking-wider uppercase">
                  AI Platform
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
          {navItems.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/dashboard" &&
                location.pathname.startsWith(item.path));

            const linkContent = (
              <NavLink
                key={item.path}
                to={item.path}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-violet-500/10 text-white"
                    : "text-muted-foreground hover:bg-white/[0.04] hover:text-foreground"
                )}
              >
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-[3px] rounded-r-full bg-violet-500 shadow-[0_0_12px_rgba(139,92,246,0.6)]"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}

                <item.icon
                  className={cn(
                    "h-[18px] w-[18px] shrink-0 transition-colors",
                    isActive
                      ? "text-violet-400"
                      : "text-muted-foreground group-hover:text-foreground"
                  )}
                />

                <AnimatePresence>
                  {!sidebarCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      transition={{ duration: 0.15 }}
                      className="truncate"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>

                {/* Notification badge for Notifications */}
                {item.path === "/notifications" && unreadCount > 0 && (
                  <span
                    className={cn(
                      "flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white",
                      sidebarCollapsed
                        ? "absolute right-1 top-1 h-4 min-w-4 text-[8px]"
                        : "ml-auto"
                    )}
                  >
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </NavLink>
            );

            if (sidebarCollapsed) {
              return (
                <Tooltip key={item.path}>
                  <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                  <TooltipContent side="right" className="font-medium">
                    {item.label}
                  </TooltipContent>
                </Tooltip>
              );
            }

            return linkContent;
          })}
        </nav>

        <Separator className="mx-3" />

        {/* User info */}
        <div className="p-3">
          <div
            className={cn(
              "flex items-center gap-3 rounded-lg p-2 transition-colors hover:bg-white/[0.04]",
              sidebarCollapsed && "justify-center"
            )}
          >
            <Avatar className="h-8 w-8 shrink-0 border border-violet-500/30">
              <AvatarFallback className="bg-violet-500/15 text-violet-300 text-xs font-bold">
                {getInitials(displayName)}
              </AvatarFallback>
            </Avatar>
            <AnimatePresence>
              {!sidebarCollapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 overflow-hidden"
                >
                  <p className="truncate text-sm font-medium text-foreground">
                    {displayName}
                  </p>
                  <p className="truncate text-xs text-muted-foreground capitalize">
                    {displayRole}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
            {!sidebarCollapsed && (
              <button
                onClick={() => {
                  logout();
                  navigate("/login");
                }}
                className="rounded-md p-1.5 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                aria-label="Log out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Creator Branding */}
        {!sidebarCollapsed ? (
          <div className="px-4 py-3 border-t border-white/[0.04] text-center bg-[#0a0a14]/40">
            <p className="text-[10px] text-muted-foreground/80 font-medium">
              Platform Creator: <span className="font-semibold text-violet-400">Ayush Anchal</span>
            </p>
            <div className="flex justify-center gap-3 mt-1.5 text-muted-foreground">
              <a
                href="https://github.com/AyushAnchal-Dev"
                target="_blank"
                rel="noopener noreferrer"
                title="GitHub"
                className="hover:text-white transition-colors"
              >
                <Github className="h-3.5 w-3.5" />
              </a>
              <a
                href="https://www.linkedin.com/in/ayush-anchal-04117028a"
                target="_blank"
                rel="noopener noreferrer"
                title="LinkedIn"
                className="hover:text-white transition-colors"
              >
                <Linkedin className="h-3.5 w-3.5" />
              </a>
              <a
                href="mailto:abhardwaj8507@gmail.com"
                title="Email"
                className="hover:text-white transition-colors"
              >
                <Mail className="h-3.5 w-3.5" />
              </a>
            </div>
          </div>
        ) : (
          <div className="py-2.5 border-t border-white/[0.04] flex flex-col items-center gap-2.5 bg-[#0a0a14]/40">
            <Tooltip>
              <TooltipTrigger asChild>
                <a
                  href="https://github.com/AyushAnchal-Dev"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  <Github className="h-4 w-4" />
                </a>
              </TooltipTrigger>
              <TooltipContent side="right">GitHub: AyushAnchal-Dev</TooltipContent>
            </Tooltip>
          </div>
        )}

        {/* Collapse Toggle */}
        <div className="p-3 pt-0">
          <button
            onClick={toggleSidebar}
            className="flex w-full items-center justify-center rounded-lg border border-white/[0.06] bg-white/[0.02] p-2 text-muted-foreground transition-all hover:bg-white/[0.05] hover:text-foreground"
            aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        </div>
      </motion.aside>
    </TooltipProvider>
  );
}
