import { useState } from 'react';
import { ChevronLeft, ChevronRight, Clock, User, CheckCircle2, Calendar } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

interface AppointmentItem {
  id: string;
  title: string;
  customerName: string;
  scheduledAt: string;
  durationMinutes: number;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  day: number;
}

interface AppointmentCalendarProps {
  appointments: AppointmentItem[];
  onSelectDate?: (date: Date) => void;
  onAddAppointment?: () => void;
}

export default function AppointmentCalendar({ appointments, onSelectDate, onAddAppointment }: AppointmentCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState(new Date().getDate());

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayIndex = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const dayHasAppointments = (day: number) => {
    return appointments.some((a) => a.day === day);
  };

  const selectedDayAppointments = appointments.filter((a) => a.day === selectedDay);

  const getStatusBadge = (status: AppointmentItem['status']) => {
    switch (status) {
      case 'confirmed':
        return <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">CONFIRMED</Badge>;
      case 'completed':
        return <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-[10px]">COMPLETED</Badge>;
      case 'cancelled':
        return <Badge variant="destructive" className="text-[10px]">CANCELLED</Badge>;
      case 'scheduled':
      default:
        return <Badge variant="secondary" className="text-[10px]">SCHEDULED</Badge>;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Calendar Grid Container */}
      <div className="lg:col-span-2 rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-5">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-base font-bold text-white">
            {currentDate.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
          </h3>
          <div className="flex gap-1.5">
            <Button size="icon" variant="outline" onClick={handlePrevMonth} className="w-8 h-8 border-white/10 text-white/60 hover:text-white hover:bg-white/5">
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button size="icon" variant="outline" onClick={handleNextMonth} className="w-8 h-8 border-white/10 text-white/60 hover:text-white hover:bg-white/5">
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Days Header */}
        <div className="grid grid-cols-7 gap-1 text-center mb-3">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
            <div key={d} className="text-[10px] text-white/30 py-1 uppercase tracking-wider font-semibold">
              {d}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1.5">
          {Array.from({ length: firstDayIndex }).map((_, idx) => (
            <div key={`empty-${idx}`} />
          ))}
          {Array.from({ length: daysInMonth }).map((_, idx) => {
            const d = idx + 1;
            const isSelected = d === selectedDay;
            const isToday = d === new Date().getDate() && currentDate.getMonth() === new Date().getMonth();
            const hasBooking = dayHasAppointments(d);
            
            return (
              <button
                key={d}
                onClick={() => {
                  setSelectedDay(d);
                  onSelectDate?.(new Date(currentDate.getFullYear(), currentDate.getMonth(), d));
                }}
                className={`p-2.5 rounded-lg text-sm transition-all relative cursor-pointer ${
                  isSelected
                    ? 'bg-violet-600 text-white font-bold shadow-md shadow-violet-950/20'
                    : isToday
                    ? 'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                    : 'text-white/60 hover:bg-white/5 hover:text-white'
                }`}
              >
                {d}
                {hasBooking && !isSelected && (
                  <span className="absolute bottom-1.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-violet-400 animate-pulse" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Day Bookings Detail Side Panel */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-violet-400" />
            Appointments: Day {selectedDay}
          </h4>
          {onAddAppointment && (
            <Button size="sm" onClick={onAddAppointment} className="h-7 text-xs bg-white/10 hover:bg-white/20 text-white border-0">
              New
            </Button>
          )}
        </div>

        <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
          {selectedDayAppointments.length > 0 ? (
            selectedDayAppointments.map((appt) => (
              <div
                key={appt.id}
                className="p-4 rounded-xl border border-white/10 bg-white/5 space-y-3 hover:border-violet-500/20 transition-all"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-bold text-white leading-tight">{appt.title}</p>
                    <div className="flex items-center gap-1 text-xs text-white/40 mt-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      {appt.scheduledAt} ({appt.durationMinutes}m)
                    </div>
                  </div>
                  {getStatusBadge(appt.status)}
                </div>
                <div className="flex items-center gap-1.5 text-xs text-white/50 border-t border-white/5 pt-2">
                  <User className="w-3.5 h-3.5 text-white/30" />
                  {appt.customerName}
                </div>
              </div>
            ))
          ) : (
            <div className="py-12 text-center rounded-xl border border-white/5 bg-white/[0.01]">
              <CheckCircle2 className="w-6 h-6 text-white/20 mx-auto mb-2" />
              <p className="text-xs text-white/40">No appointments booked</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
