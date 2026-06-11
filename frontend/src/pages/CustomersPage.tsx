import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Users } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { customersApi } from '../api/customers';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';

const catColor = (c: string) => c === 'vip' ? 'default' : c === 'returning' ? 'secondary' : 'outline';

const formatLastContact = (isoString: string) => {
  if (!isoString) return 'Never';
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHrs = Math.floor(diffMins / 60);
  if (diffHrs < 24) return `${diffHrs}h ago`;
  const diffDays = Math.floor(diffHrs / 24);
  if (diffDays === 1) return '1 day ago';
  return `${diffDays} days ago`;
};

export default function CustomersPage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const { data: customersResponse, isLoading } = useQuery({
    queryKey: ['customers', page, search],
    queryFn: () => customersApi.getCustomers({ page, limit: 12, search }),
    staleTime: 30 * 1000,
  });

  const customers = customersResponse?.data || [];
  const totalPages = customersResponse?.totalPages || 1;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Customers</h1>
        <p className="text-sm text-white/40">Your customer database</p>
      </div>
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
        <Input
          placeholder="Search customers..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="pl-9 bg-white/5 border-white/10 text-white"
        />
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-sm text-white/40 animate-pulse">
          Loading customers...
        </div>
      ) : customers.length === 0 ? (
        <div className="text-center py-12 text-sm text-white/40 bg-white/5 rounded-xl border border-white/10">
          No customer records found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {customers.map((c, i) => (
            <motion.div
              key={c.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(i * 0.05, 0.5) }}
              className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-5 hover:border-violet-500/30 transition-all cursor-pointer group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white font-bold text-sm">
                  {c.name ? c.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : '??'}
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{c.name}</p>
                  <p className="text-xs text-white/40">{c.phone}</p>
                </div>
                <Badge variant={catColor(c.category) as any} className="ml-auto text-[10px]">
                  {c.category.toUpperCase()}
                </Badge>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-white/5">
                <div>
                  <p className="text-base font-bold text-white">{c.totalCalls}</p>
                  <p className="text-[10px] text-white/30">Calls</p>
                </div>
                <div>
                  <p className="text-base font-bold text-white">{c.totalCalls > 0 ? (c.totalRevenue > 0 ? `₹${(c.totalRevenue / 1000).toFixed(0)}k` : '₹0') : 'N/A'}</p>
                  <p className="text-[10px] text-white/30">Value</p>
                </div>
                <div>
                  <p className="text-xs text-white/50 mt-1">{formatLastContact(c.lastContactDate)}</p>
                  <p className="text-[10px] text-white/30">Last Active</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {!isLoading && totalPages > 1 && (
        <div className="flex justify-between items-center px-2">
          <p className="text-xs text-white/40">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={page <= 1}
              onClick={() => setPage(p => Math.max(p - 1, 1))}
              className="text-xs text-white border-white/10"
            >
              Previous
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={page >= totalPages}
              onClick={() => setPage(p => Math.min(p + 1, totalPages))}
              className="text-xs text-white border-white/10"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
