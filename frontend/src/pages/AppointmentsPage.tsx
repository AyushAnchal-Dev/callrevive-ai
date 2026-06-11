import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Calendar, ChevronLeft, ChevronRight, Clock, Loader2, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { useAppointments, useCreateAppointment } from '../hooks/useAppointments';
import { useCustomers } from '../hooks/useCustomers';
import { useAuthStore } from '../store/auth-store';
import { toast } from 'sonner';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, getDay, addMonths, subMonths, isSameDay, parseISO } from 'date-fns';

export default function AppointmentsPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showForm, setShowForm] = useState(false);

  const { data: appointmentsData, isLoading } = useAppointments();
  const { data: customersData } = useCustomers({ page: 1, limit: 1000 });
  const customers = customersData?.data || [];
  const { user } = useAuthStore();
  const businessId = user?.businessId;
  const createMutation = useCreateAppointment();

  // Parse appointments - handle both array and paginated response
  const appointments = useMemo(() => {
    if (!appointmentsData) return [];
    if (Array.isArray(appointmentsData)) return appointmentsData;
    if (appointmentsData.data) return appointmentsData.data;
    return [];
  }, [appointmentsData]);

  // Calendar days
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });
  const startPadding = getDay(monthStart);

  // Appointments with dots
  const apptDays = new Set(
    appointments.map((a: any) => {
      const d = a.scheduled_at || a.scheduledAt || a.date;
      return d ? format(new Date(d), 'yyyy-MM-dd') : null;
    }).filter(Boolean)
  );

  // Filter appointments for selected date
  const dayAppointments = appointments.filter((a: any) => {
    const d = a.scheduled_at || a.scheduledAt || a.date;
    if (!d) return false;
    return isSameDay(new Date(d), selectedDate);
  });

  const [formData, setFormData] = useState({
    title: '', customer_id: '', business_id: '', scheduled_at: '', duration_minutes: 30, description: '',
  });

  const handleCreate = async () => {
    if (!formData.title || !formData.scheduled_at || !formData.customer_id) {
      toast.error('Title, date/time, and customer are required');
      return;
    }
    if (!businessId) {
      toast.error('Business ID not found, please log in again.');
      return;
    }
    try {
      const scheduledAtIso = new Date(formData.scheduled_at).toISOString();
      await createMutation.mutateAsync({
        customer_id: formData.customer_id,
        business_id: businessId,
        title: formData.title,
        description: formData.description || undefined,
        scheduled_at: scheduledAtIso,
        duration_minutes: formData.duration_minutes,
      });
      toast.success('Appointment created!');
      setShowForm(false);
      setFormData({ title: '', customer_id: '', business_id: '', scheduled_at: '', duration_minutes: 30, description: '' });
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.detail || 'Failed to create appointment');
    }
  };

  const statusColor: Record<string, string> = {
    confirmed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    scheduled: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    completed: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    cancelled: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex justify-between items-center">
        <div><h1 className="text-2xl font-bold text-white">Appointments</h1><p className="text-sm text-white/40">Manage scheduled appointments</p></div>
        <Button onClick={() => setShowForm(true)} className="bg-gradient-to-r from-indigo-500 to-violet-500 text-white"><Plus className="w-4 h-4 mr-2" /> New Appointment</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <div className="lg:col-span-2 rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">{format(currentMonth, 'MMMM yyyy')}</h3>
            <div className="flex gap-1">
              <button onClick={() => setCurrentMonth(subMonths(currentMonth, 1))} className="p-1 rounded hover:bg-white/10" aria-label="Previous month"><ChevronLeft className="w-4 h-4 text-white/50" /></button>
              <button onClick={() => setCurrentMonth(addMonths(currentMonth, 1))} className="p-1 rounded hover:bg-white/10" aria-label="Next month"><ChevronRight className="w-4 h-4 text-white/50" /></button>
            </div>
          </div>
          <div className="grid grid-cols-7 gap-1 text-center mb-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => <div key={d} className="text-[10px] text-white/30 py-1">{d}</div>)}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {Array.from({ length: startPadding }).map((_, i) => <div key={`e${i}`} />)}
            {days.map(day => {
              const dayKey = format(day, 'yyyy-MM-dd');
              const isSelected = isSameDay(day, selectedDate);
              const isToday = isSameDay(day, new Date());
              const hasAppt = apptDays.has(dayKey);
              return (
                <button key={dayKey} onClick={() => setSelectedDate(day)}
                  className={`p-2 rounded-lg text-sm transition-all relative ${
                    isSelected ? 'bg-violet-500 text-white font-bold' : isToday ? 'bg-violet-500/20 text-violet-400' : 'text-white/50 hover:bg-white/10'
                  }`}>
                  {format(day, 'd')}
                  {hasAppt && !isSelected && <span className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-violet-400" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Day appointments */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white">Appointments on {format(selectedDate, 'MMM d, yyyy')}</h3>
          {isLoading ? (
            <div className="flex items-center justify-center py-8"><Loader2 className="w-5 h-5 text-violet-400 animate-spin" /></div>
          ) : dayAppointments.length === 0 ? (
            <p className="text-xs text-white/30">No appointments</p>
          ) : (
            <AnimatePresence>
              {dayAppointments.map((a: any) => (
                <motion.div key={a.id} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-white">{a.title}</p>
                      <p className="text-xs text-white/40 mt-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {a.scheduled_at || a.scheduledAt ? format(new Date(a.scheduled_at || a.scheduledAt), 'h:mm a') : ''} · {a.duration_minutes || a.duration || 30} min
                      </p>
                      {a.description && <p className="text-xs text-white/30 mt-1">{a.description}</p>}
                    </div>
                    <Badge className={`text-[10px] border ${statusColor[a.status] || statusColor.scheduled}`}>{a.status}</Badge>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </div>
      </div>

      {/* New Appointment Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="bg-[#12121e] border-white/10 text-white max-w-md">
          <DialogHeader>
            <DialogTitle>New Appointment</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-2">
            <div className="space-y-2">
              <Label className="text-white/70">Title *</Label>
              <Input value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })} placeholder="e.g. AC Repair" className="bg-white/5 border-white/10 text-white" />
            </div>
            <div className="space-y-2">
              <Label className="text-white/70">Customer *</Label>
              <select
                value={formData.customer_id}
                onChange={e => setFormData({ ...formData, customer_id: e.target.value })}
                className="w-full h-10 px-3 rounded-md bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 text-sm"
              >
                <option value="" className="bg-[#12121e]">Select a customer</option>
                {customers.map((c: any) => (
                  <option key={c.id} value={c.id} className="bg-[#12121e]">
                    {c.name} ({c.phone})
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label className="text-white/70">Date & Time *</Label>
              <Input type="datetime-local" value={formData.scheduled_at} onChange={e => setFormData({ ...formData, scheduled_at: e.target.value })} className="bg-white/5 border-white/10 text-white" />
            </div>
            <div className="space-y-2">
              <Label className="text-white/70">Duration (minutes)</Label>
              <Input type="number" value={formData.duration_minutes} onChange={e => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 30 })} className="bg-white/5 border-white/10 text-white" />
            </div>
            <div className="space-y-2">
              <Label className="text-white/70">Notes</Label>
              <Input value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} placeholder="Optional notes" className="bg-white/5 border-white/10 text-white" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="ghost" onClick={() => setShowForm(false)} className="text-white/60">Cancel</Button>
              <Button onClick={handleCreate} disabled={createMutation.isPending} className="bg-gradient-to-r from-indigo-500 to-violet-500 text-white">
                {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Create
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
