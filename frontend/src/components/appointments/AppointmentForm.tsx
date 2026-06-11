import { useState } from 'react';
import { Calendar, Clock, User, FileText, Check } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { toast } from 'sonner';

interface AppointmentFormProps {
  onCancel?: () => void;
  onSubmitSuccess?: () => void;
}

export default function AppointmentForm({ onCancel, onSubmitSuccess }: AppointmentFormProps) {
  const [formData, setFormData] = useState({
    customerName: '',
    customerPhone: '',
    title: '',
    date: new Date().toISOString().split('T')[0],
    time: '10:00',
    duration: '60',
    notes: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.customerName || !formData.title || !formData.date) {
      toast.error('Please fill in all required fields');
      return;
    }
    toast.success('Appointment scheduled successfully!');
    onSubmitSuccess?.();
  };

  return (
    <Card className="bg-white/5 border-white/10 backdrop-blur-xl max-w-md w-full mx-auto">
      <CardHeader>
        <CardTitle className="text-white text-base font-bold flex items-center gap-1.5">
          <Calendar className="w-4 h-4 text-violet-400" />
          Schedule Appointment
        </CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {/* Customer Name */}
          <div className="space-y-1.5">
            <Label htmlFor="customerName" className="text-xs text-white/70">Customer Name *</Label>
            <div className="relative">
              <Input
                id="customerName"
                name="customerName"
                placeholder="e.g. Rajesh Kumar"
                value={formData.customerName}
                onChange={handleChange}
                className="bg-white/5 border-white/10 text-white pl-9 text-xs"
                required
              />
              <User className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
            </div>
          </div>

          {/* Customer Phone */}
          <div className="space-y-1.5">
            <Label htmlFor="customerPhone" className="text-xs text-white/70">Phone Number</Label>
            <Input
              id="customerPhone"
              name="customerPhone"
              placeholder="e.g. +91 98765 43210"
              value={formData.customerPhone}
              onChange={handleChange}
              className="bg-white/5 border-white/10 text-white text-xs"
            />
          </div>

          {/* Service Title */}
          <div className="space-y-1.5">
            <Label htmlFor="title" className="text-xs text-white/70">Appointment / Service Title *</Label>
            <Input
              id="title"
              name="title"
              placeholder="e.g. AC Maintenance Service"
              value={formData.title}
              onChange={handleChange}
              className="bg-white/5 border-white/10 text-white text-xs"
              required
            />
          </div>

          {/* Date & Time Row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="date" className="text-xs text-white/70">Date *</Label>
              <Input
                id="date"
                name="date"
                type="date"
                value={formData.date}
                onChange={handleChange}
                className="bg-white/5 border-white/10 text-white text-xs"
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="time" className="text-xs text-white/70">Time *</Label>
              <div className="relative">
                <Input
                  id="time"
                  name="time"
                  type="time"
                  value={formData.time}
                  onChange={handleChange}
                  className="bg-white/5 border-white/10 text-white pl-9 text-xs"
                  required
                />
                <Clock className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
              </div>
            </div>
          </div>

          {/* Duration Selector */}
          <div className="space-y-1.5">
            <Label htmlFor="duration" className="text-xs text-white/70">Duration</Label>
            <Select
              defaultValue="60"
              onValueChange={(val) => handleSelectChange('duration', val)}
            >
              <SelectTrigger className="bg-white/5 border-white/10 text-white text-xs">
                <SelectValue placeholder="Select Duration" />
              </SelectTrigger>
              <SelectContent className="bg-[#151525] border-white/10 text-white text-xs">
                <SelectItem value="15">15 Minutes</SelectItem>
                <SelectItem value="30">30 Minutes</SelectItem>
                <SelectItem value="45">45 Minutes</SelectItem>
                <SelectItem value="60">60 Minutes (1 hr)</SelectItem>
                <SelectItem value="120">120 Minutes (2 hrs)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Notes */}
          <div className="space-y-1.5">
            <Label htmlFor="notes" className="text-xs text-white/70">Notes</Label>
            <div className="relative">
              <textarea
                id="notes"
                name="notes"
                rows={3}
                placeholder="Describe any special customer requirements..."
                value={formData.notes}
                onChange={handleChange}
                className="w-full rounded-md bg-white/5 border border-white/10 text-white p-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-violet-500 pl-9"
              />
              <FileText className="w-3.5 h-3.5 absolute left-3 top-3.5 text-white/30" />
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2 border-t border-white/5 pt-4">
          {onCancel && (
            <Button type="button" variant="ghost" onClick={onCancel} className="text-xs text-white/60 hover:text-white hover:bg-white/5">
              Cancel
            </Button>
          )}
          <Button type="submit" className="bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white border-0 text-xs">
            <Check className="w-3.5 h-3.5 mr-1" />
            Schedule
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
