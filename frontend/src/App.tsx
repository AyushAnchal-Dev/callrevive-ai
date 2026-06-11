import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { ThemeProvider } from './components/ThemeProvider';
import { useAuthStore } from './store/auth-store';

import { lazy, Suspense } from 'react';
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SignupPage = lazy(() => import('./pages/SignupPage'));
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'));
const DashboardLayout = lazy(() => import('./components/layout/DashboardLayout').then(m => ({ default: m.DashboardLayout })));

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const LeadsPage = lazy(() => import('./pages/LeadsPage'));
const CustomersPage = lazy(() => import('./pages/CustomersPage'));
const CallsPage = lazy(() => import('./pages/CallsPage'));
const ConversationsPage = lazy(() => import('./pages/ConversationsPage'));
const AppointmentsPage = lazy(() => import('./pages/AppointmentsPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const AIInsightsPage = lazy(() => import('./pages/AIInsightsPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1, refetchOnWindowFocus: false },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark">
        <BrowserRouter>
          <Suspense
            fallback={
              <div className="min-h-screen flex items-center justify-center bg-[#0a0a0f] text-white/40 text-sm animate-pulse">
                Loading CallRevive AI...
              </div>
            }
          >
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route
                element={
                  <ProtectedRoute>
                    <DashboardLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/leads" element={<LeadsPage />} />
                <Route path="/customers" element={<CustomersPage />} />
                <Route path="/calls" element={<CallsPage />} />
                <Route path="/conversations" element={<ConversationsPage />} />
                <Route path="/appointments" element={<AppointmentsPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/ai-insights" element={<AIInsightsPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
        <Toaster position="top-right" richColors theme="dark" />
      </ThemeProvider>
    </QueryClientProvider>
  );
}
