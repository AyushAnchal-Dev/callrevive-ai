import { useState } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { useLeads, useUpdateLeadStatus } from '../../hooks/useLeads';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

const scoreColor = (s: number) => s >= 70 ? 'text-emerald-400' : s >= 40 ? 'text-amber-400' : 'text-rose-400';
const catBadge = (c: string) => c === 'hot' ? 'destructive' : c === 'warm' ? 'secondary' : 'outline';

export default function LeadTable({ filter }: { filter?: string }) {
  const [page, setPage] = useState(1);
  const [selectedLead, setSelectedLead] = useState<any | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const { data: leadsResponse, isLoading } = useLeads({
    page,
    limit: 10,
    category: filter === 'all' ? undefined : filter,
  });

  const updateStatusMutation = useUpdateLeadStatus();

  const leads = leadsResponse?.data || [];
  const totalPages = leadsResponse?.totalPages || 1;

  const handleStatusChange = (newStatus: string) => {
    if (selectedLead) {
      updateStatusMutation.mutate(
        { id: selectedLead.id, status: newStatus },
        {
          onSuccess: (updatedLead) => {
            setSelectedLead((prev: any) => prev ? { ...prev, status: newStatus } : null);
          },
        }
      );
    }
  };

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10 bg-white/5">
                {['Customer', 'Service', 'Score', 'Category', 'Revenue', 'Urgency', 'Status', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-xs text-white/40 animate-pulse">
                    Loading leads...
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-xs text-white/40">
                    No leads found.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => {
                      setSelectedLead(lead);
                      setIsDetailOpen(true);
                    }}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
                  >
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-white">{lead.customerName}</p>
                      <p className="text-xs text-white/40">{lead.customerPhone}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-white/70">{lead.service}</td>
                    <td className="px-4 py-3">
                      <span className={`text-sm font-bold ${scoreColor(lead.score)}`}>{lead.score}</span>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={catBadge(lead.category) as any}>{lead.category.toUpperCase()}</Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-white font-medium">
                      ₹{lead.revenueEstimate.toLocaleString('en-IN')}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="outline" className="text-xs">{lead.urgency}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="secondary" className="text-xs capitalize">{lead.status}</Badge>
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setSelectedLead(lead);
                          setIsDetailOpen(true);
                        }}
                        className="text-xs text-violet-400 hover:text-violet-300"
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
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

      {/* Details Dialog */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="bg-[#12121a]/95 border-white/10 text-white backdrop-blur-xl max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold text-white">Lead Details</DialogTitle>
            <DialogDescription className="text-white/40 text-xs">
              AI qualification audit and details for this opportunity.
            </DialogDescription>
          </DialogHeader>

          {selectedLead && (
            <div className="space-y-4 py-2">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-[10px] text-white/40 uppercase font-medium">Customer</p>
                  <p className="text-sm font-semibold text-white mt-0.5">{selectedLead.customerName}</p>
                  <p className="text-xs text-white/50">{selectedLead.customerPhone}</p>
                </div>
                <div>
                  <p className="text-[10px] text-white/40 uppercase font-medium">Estimated Revenue</p>
                  <p className="text-sm font-bold text-emerald-400 mt-0.5">
                    ₹{selectedLead.revenueEstimate.toLocaleString('en-IN')}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <p className="text-[10px] text-white/40 uppercase font-medium">Score</p>
                  <p className={`text-sm font-bold ${scoreColor(selectedLead.score)} mt-0.5`}>
                    {selectedLead.score}/100
                  </p>
                </div>
                <div>
                  <p className="text-[10px] text-white/40 uppercase font-medium">Category</p>
                  <Badge variant={catBadge(selectedLead.category) as any} className="mt-1">
                    {selectedLead.category.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <p className="text-[10px] text-white/40 uppercase font-medium">Urgency</p>
                  <Badge variant="outline" className="mt-1 text-xs">
                    {selectedLead.urgency}
                  </Badge>
                </div>
              </div>

              <div>
                <p className="text-[10px] text-white/40 uppercase font-medium">Requested Service</p>
                <p className="text-sm text-white/80 mt-0.5">{selectedLead.service}</p>
              </div>

              <div>
                <p className="text-[10px] text-white/40 uppercase font-medium">AI Qualification Notes</p>
                <p className="text-xs text-white/60 bg-white/5 p-3 rounded-lg border border-white/5 leading-relaxed mt-1 whitespace-pre-wrap max-h-32 overflow-y-auto">
                  {selectedLead.notes || 'No qualification notes available.'}
                </p>
              </div>

              <div className="pt-2 border-t border-white/5">
                <p className="text-[10px] text-white/40 uppercase font-medium mb-1.5">Lead Status</p>
                <Select value={selectedLead.status} onValueChange={handleStatusChange}>
                  <SelectTrigger className="bg-white/5 border-white/10 text-white text-xs h-9">
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#12121a] border-white/10 text-white">
                    {['new', 'contacted', 'qualified', 'converted', 'lost'].map(st => (
                      <SelectItem key={st} value={st} className="text-xs capitalize focus:bg-white/10 focus:text-white">
                        {st}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          <DialogFooter className="pt-2 border-t border-white/5">
            <Button
              onClick={() => setIsDetailOpen(false)}
              className="bg-violet-600 hover:bg-violet-500 text-white text-xs"
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
