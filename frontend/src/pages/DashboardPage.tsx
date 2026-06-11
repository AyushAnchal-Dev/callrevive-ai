import { motion } from 'framer-motion';
import StatsCards from '../components/dashboard/StatsCards';
import RevenueChart from '../components/dashboard/RevenueChart';
import LeadsPipeline from '../components/dashboard/LeadsPipeline';
import RecentCalls from '../components/dashboard/RecentCalls';
import AIInsights from '../components/dashboard/AIInsights';

export default function DashboardPage() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-white/40">Welcome back. Here's your business overview.</p>
      </div>
      <StatsCards />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2"><RevenueChart /></div>
        <div><LeadsPipeline /></div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentCalls />
        <AIInsights />
      </div>
    </motion.div>
  );
}
