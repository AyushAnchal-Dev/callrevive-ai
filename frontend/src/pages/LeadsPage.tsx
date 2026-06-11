import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Search } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import LeadTable from '../components/leads/LeadTable';
import { useLeadAnalytics } from '../hooks/useAnalytics';

export default function LeadsPage() {
  const [active, setActive] = useState('all');
  const [search, setSearch] = useState('');
  const { data: leadDist } = useLeadAnalytics();

  const getCount = (cat: string) => {
    if (!leadDist) return 0;
    if (cat === 'all') {
      return leadDist.reduce((acc, curr) => acc + curr.count, 0);
    }
    return leadDist.find(l => l.category === cat)?.count || 0;
  };

  const tabs = [
    { key: 'all', label: 'All', count: getCount('all') },
    { key: 'hot', label: '🔥 Hot', count: getCount('hot') },
    { key: 'warm', label: 'Warm', count: getCount('warm') },
    { key: 'cold', label: 'Cold', count: getCount('cold') },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Leads</h1>
          <p className="text-sm text-white/40">Manage and qualify your leads</p>
        </div>
        <Button className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white">
          <Plus className="w-4 h-4 mr-2" /> Add Lead
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setActive(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${active === t.key ? 'bg-violet-500/20 text-violet-400 border border-violet-500/30' : 'text-white/40 hover:text-white/60 border border-transparent'}`}>
            {t.label} <span className="ml-1 text-xs opacity-60">({t.count})</span>
          </button>
        ))}
      </div>
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
        <Input
          placeholder="Search leads..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 bg-white/5 border-white/10 text-white"
        />
      </div>
      <LeadTable filter={active} />
    </motion.div>
  );
}
