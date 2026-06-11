import { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Search, Moon, Sun, Bell, User2, Phone, MessageSquare, Loader2 } from "lucide-react";
import { useTheme } from "next-themes";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuthStore } from "@/store/auth-store";
import { CURRENCY_OPTIONS } from "@/lib/constants";
import { getInitials } from "@/lib/utils";
import type { CurrencyCode } from "@/types";
import { useGlobalSearch } from "@/hooks/useSearch";
import { useUnreadCount } from "@/hooks/useNotifications";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/leads": "Leads",
  "/customers": "Customers",
  "/calls": "Calls",
  "/conversations": "Conversations",
  "/appointments": "Appointments",
  "/analytics": "Analytics",
  "/ai-insights": "AI Insights",
  "/notifications": "Notifications",
  "/settings": "Settings",
};

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  const { user, currency, setCurrency, logout } = useAuthStore();

  const pageTitle = pageTitles[location.pathname] || "Dashboard";
  const displayName = user?.name || "Admin User";

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [showResults, setShowResults] = useState(false);
  const { data: searchResults, isLoading: searchLoading } = useGlobalSearch(searchQuery);
  const searchRef = useRef<HTMLDivElement>(null);

  // Notification badge
  const { data: unreadData } = useUnreadCount();
  const unreadCount = unreadData?.count ?? 0;

  // Close search on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowResults(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearchSelect = (type: string, id: string) => {
    setShowResults(false);
    setSearchQuery("");
    const routes: Record<string, string> = {
      customer: `/customers`,
      lead: `/leads`,
      conversation: `/conversations`,
    };
    navigate(routes[type] || "/dashboard");
  };

  const hasResults = searchResults && (
    searchResults.customers?.length > 0 ||
    searchResults.leads?.length > 0 ||
    searchResults.conversations?.length > 0
  );

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-2 md:gap-4 border-b border-white/[0.06] bg-background/80 backdrop-blur-xl px-4 md:px-6">
      {/* Page Title */}
      <div className="flex-1 min-w-0">
        <h1 className="text-sm sm:text-base md:text-lg font-semibold text-foreground truncate">{pageTitle}</h1>
      </div>

      {/* Search */}
      <div ref={searchRef} className="hidden md:flex relative max-w-xs flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search leads, customers..."
          className="pl-9 bg-white/[0.03] border-white/[0.08] h-9 text-sm"
          aria-label="Search leads and customers"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setShowResults(true);
          }}
          onFocus={() => searchQuery.length >= 2 && setShowResults(true)}
        />

        {/* Search Dropdown */}
        {showResults && searchQuery.length >= 2 && (
          <div className="absolute top-full mt-1 left-0 right-0 rounded-xl border border-white/10 bg-[#12121e] backdrop-blur-xl shadow-2xl shadow-black/50 overflow-hidden z-50">
            {searchLoading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="w-4 h-4 text-violet-400 animate-spin" />
              </div>
            ) : !hasResults ? (
              <div className="py-6 text-center text-xs text-white/40">No results found</div>
            ) : (
              <div className="max-h-80 overflow-y-auto">
                {searchResults?.customers?.length > 0 && (
                  <div>
                    <div className="px-3 py-1.5 text-[10px] font-semibold text-white/30 uppercase tracking-wider">Customers</div>
                    {searchResults.customers.map((c: any) => (
                      <button key={c.id} onClick={() => handleSearchSelect("customer", c.id)}
                        className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/5 transition-colors text-left">
                        <User2 className="w-4 h-4 text-violet-400 flex-shrink-0" />
                        <div className="min-w-0">
                          <p className="text-sm text-white truncate">{c.name}</p>
                          <p className="text-[10px] text-white/40">{c.phone}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
                {searchResults?.leads?.length > 0 && (
                  <div>
                    <div className="px-3 py-1.5 text-[10px] font-semibold text-white/30 uppercase tracking-wider border-t border-white/5">Leads</div>
                    {searchResults.leads.map((l: any) => (
                      <button key={l.id} onClick={() => handleSearchSelect("lead", l.id)}
                        className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/5 transition-colors text-left">
                        <Phone className="w-4 h-4 text-rose-400 flex-shrink-0" />
                        <div className="min-w-0">
                          <p className="text-sm text-white truncate">{l.name}</p>
                          <p className="text-[10px] text-white/40">{l.service} · {l.category}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
                {searchResults?.conversations?.length > 0 && (
                  <div>
                    <div className="px-3 py-1.5 text-[10px] font-semibold text-white/30 uppercase tracking-wider border-t border-white/5">Conversations</div>
                    {searchResults.conversations.map((c: any) => (
                      <button key={c.id} onClick={() => handleSearchSelect("conversation", c.id)}
                        className="w-full flex items-center gap-3 px-3 py-2 hover:bg-white/5 transition-colors text-left">
                        <MessageSquare className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                        <div className="min-w-0">
                          <p className="text-sm text-white truncate">{c.customer_name}</p>
                          <p className="text-[10px] text-white/40 truncate">{c.summary || c.channel}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Currency Selector */}
      <Select
        value={currency}
        onValueChange={(val) => setCurrency(val as CurrencyCode)}
      >
        <SelectTrigger className="w-[100px] h-9 bg-white/[0.03] border-white/[0.08] text-xs">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {CURRENCY_OPTIONS.map((curr) => (
            <SelectItem key={curr.value} value={curr.value} className="text-xs">
              {curr.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Theme Toggle */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        className="h-9 w-9 text-muted-foreground hover:text-foreground"
        aria-label="Toggle light and dark theme"
      >
        {theme === "dark" ? (
          <Sun className="h-4 w-4" />
        ) : (
          <Moon className="h-4 w-4" />
        )}
      </Button>

      {/* Notifications */}
      <Button
        variant="ghost"
        size="icon"
        className="relative h-9 w-9 text-muted-foreground hover:text-foreground"
        onClick={() => navigate("/notifications")}
        aria-label="View notifications"
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[9px] font-bold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </Button>

      {/* User Menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="relative h-9 w-9 rounded-full p-0"
            aria-label="User profile menu"
          >
            <Avatar className="h-9 w-9 border border-violet-500/30">
              <AvatarFallback className="bg-violet-500/15 text-violet-300 text-xs font-bold">
                {getInitials(displayName)}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">{displayName}</p>
              <p className="text-xs leading-none text-muted-foreground">
                {user?.email || "admin@callrevive.ai"}
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => navigate("/settings")}>
            Profile & Settings
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="text-rose-400 focus:text-rose-400"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
