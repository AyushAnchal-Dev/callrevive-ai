import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { MobileNav } from "./MobileNav";
import { useAuthStore } from "@/store/auth-store";

import { cn } from "@/lib/utils";

export function DashboardLayout() {
  const { sidebarCollapsed } = useAuthStore();

  return (
    <div className="min-h-screen gradient-mesh">
      {/* Desktop sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Main content area */}
      <div
        className={cn(
          "flex flex-col min-h-screen transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]",
          sidebarCollapsed ? "lg:pl-[72px]" : "lg:pl-[280px]"
        )}
      >
        {/* Header with mobile nav toggle */}
        <div className="flex items-center gap-2 lg:gap-0">
          <div className="lg:hidden pl-4">
            <MobileNav />
          </div>
          <div className="flex-1">
            <Header />
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <motion.div
            key={location?.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
