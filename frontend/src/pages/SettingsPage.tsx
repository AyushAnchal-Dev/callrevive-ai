import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Building2, Sparkles, Bell, KeyRound, Save, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { useSettings, useUpdateSettings, useUpdateNotificationPrefs } from '@/hooks/useSettings';

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings();
  const updateMut = useUpdateSettings();
  const updateNotifMut = useUpdateNotificationPrefs();

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: '', category: '', phone_number: '', whatsapp_number: '',
    email: '', default_currency: 'INR', timezone: 'Asia/Kolkata',
  });

  // Voice AI form state
  const [voiceForm, setVoiceForm] = useState({
    language: 'Hinglish', voice_gender: 'female_hindi', tone: 'helpful',
    callback_delay: 'immediate', custom_prompt: '',
  });

  // Notification prefs state
  const [notifPrefs, setNotifPrefs] = useState({
    whatsapp_hot_leads: true, sms_callback_failures: false,
    daily_email_reports: true, in_app_sound: true,
  });

  // Populate forms when settings load
  useEffect(() => {
    if (settings) {
      setProfileForm({
        name: settings.business_name || '',
        category: settings.category || '',
        phone_number: settings.phone_number || '',
        whatsapp_number: settings.whatsapp_number || '',
        email: settings.email || '',
        default_currency: settings.default_currency || 'INR',
        timezone: settings.timezone || 'Asia/Kolkata',
      });
      const s = settings.settings || {};
      if (s.voice_ai) {
        setVoiceForm({
          language: s.voice_ai.language || 'Hinglish',
          voice_gender: s.voice_ai.voice_gender || 'female_hindi',
          tone: s.voice_ai.tone || 'helpful',
          callback_delay: s.voice_ai.callback_delay || 'immediate',
          custom_prompt: s.voice_ai.custom_prompt || '',
        });
      }
      if (s.notification_preferences) {
        setNotifPrefs({
          whatsapp_hot_leads: s.notification_preferences.whatsapp_hot_leads ?? true,
          sms_callback_failures: s.notification_preferences.sms_callback_failures ?? false,
          daily_email_reports: s.notification_preferences.daily_email_reports ?? true,
          in_app_sound: s.notification_preferences.in_app_sound ?? true,
        });
      }
    }
  }, [settings]);

  const handleSaveProfile = async () => {
    try {
      await updateMut.mutateAsync(profileForm);
      toast.success('Profile settings saved!');
    } catch {
      toast.error('Failed to save profile');
    }
  };

  const handleSaveVoice = async () => {
    try {
      await updateMut.mutateAsync({ settings: { ...(settings?.settings || {}), voice_ai: voiceForm } });
      toast.success('Voice AI settings saved!');
    } catch {
      toast.error('Failed to save voice config');
    }
  };

  const handleSaveNotifs = async () => {
    try {
      await updateNotifMut.mutateAsync(notifPrefs);
      toast.success('Alert preferences saved!');
    } catch {
      toast.error('Failed to save alerts');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-sm text-white/40">Manage your business profile, AI voice agents, alerts, and API credentials</p>
      </div>

      <Tabs defaultValue="business" className="w-full">
        <TabsList className="grid grid-cols-4 bg-white/5 border border-white/10 p-1 rounded-xl h-11 w-full md:w-auto">
          <TabsTrigger value="business" className="text-xs md:text-sm flex items-center gap-1.5 py-2"><Building2 className="w-4 h-4" />Profile</TabsTrigger>
          <TabsTrigger value="voice" className="text-xs md:text-sm flex items-center gap-1.5 py-2"><Sparkles className="w-4 h-4" />Voice AI</TabsTrigger>
          <TabsTrigger value="notifications" className="text-xs md:text-sm flex items-center gap-1.5 py-2"><Bell className="w-4 h-4" />Alerts</TabsTrigger>
          <TabsTrigger value="api" className="text-xs md:text-sm flex items-center gap-1.5 py-2"><KeyRound className="w-4 h-4" />Integrations</TabsTrigger>
        </TabsList>

        {/* PROFILE TAB */}
        <TabsContent value="business" className="mt-6">
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white">Business Profile</CardTitle>
              <CardDescription className="text-white/40">Configure settings for your business workspace</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="biz-name" className="text-white/70">Business Name</Label>
                  <Input id="biz-name" value={profileForm.name} onChange={e => setProfileForm({ ...profileForm, name: e.target.value })} className="bg-white/5 border-white/10 text-white" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="biz-category" className="text-white/70">Business Category</Label>
                  <Select value={profileForm.category} onValueChange={v => setProfileForm({ ...profileForm, category: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue placeholder="Select Category" /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="home_services">Home Services (Plumbing, AC)</SelectItem>
                      <SelectItem value="healthcare">Healthcare & Clinics</SelectItem>
                      <SelectItem value="legal">Legal & Professional Services</SelectItem>
                      <SelectItem value="retail">Retail & E-commerce</SelectItem>
                      <SelectItem value="real_estate">Real Estate</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="biz-phone" className="text-white/70">Inbound Twilio Number</Label>
                  <Input id="biz-phone" value={profileForm.phone_number} disabled className="bg-white/[0.02] border-white/10 text-white/50 cursor-not-allowed" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="biz-whatsapp" className="text-white/70">WhatsApp Sandbox Number</Label>
                  <Input id="biz-whatsapp" value={profileForm.whatsapp_number} disabled className="bg-white/[0.02] border-white/10 text-white/50 cursor-not-allowed" />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="biz-currency" className="text-white/70">Primary Currency</Label>
                  <Select value={profileForm.default_currency} onValueChange={v => setProfileForm({ ...profileForm, default_currency: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue placeholder="Select Currency" /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="INR">INR (₹) - Indian Rupee</SelectItem>
                      <SelectItem value="USD">USD ($) - US Dollar</SelectItem>
                      <SelectItem value="EUR">EUR (€) - Euro</SelectItem>
                      <SelectItem value="GBP">GBP (£) - British Pound</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="biz-timezone" className="text-white/70">Timezone</Label>
                  <Select value={profileForm.timezone} onValueChange={v => setProfileForm({ ...profileForm, timezone: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue placeholder="Select Timezone" /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="Asia/Kolkata">Asia/Kolkata (IST)</SelectItem>
                      <SelectItem value="America/New_York">America/New_York (EST)</SelectItem>
                      <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                      <SelectItem value="Asia/Singapore">Asia/Singapore (SGT)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end border-t border-white/5 pt-4">
              <Button onClick={handleSaveProfile} disabled={updateMut.isPending} className="bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white border-0 shadow-lg shadow-violet-500/20">
                {updateMut.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Changes
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        {/* VOICE AI TAB */}
        <TabsContent value="voice" className="mt-6">
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white">Voice Assistant Configuration</CardTitle>
              <CardDescription className="text-white/40">Tune the personality and language preferences of your AI agent</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-white/70">Primary Language</Label>
                  <Select value={voiceForm.language} onValueChange={v => setVoiceForm({ ...voiceForm, language: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="Hinglish">Hinglish (Hindi + English)</SelectItem>
                      <SelectItem value="en-US">English (US)</SelectItem>
                      <SelectItem value="hi-IN">Hindi (hi-IN)</SelectItem>
                      <SelectItem value="ta-IN">Tamil (ta-IN)</SelectItem>
                      <SelectItem value="te-IN">Telugu (te-IN)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-white/70">Agent Voice Accent/Gender</Label>
                  <Select value={voiceForm.voice_gender} onValueChange={v => setVoiceForm({ ...voiceForm, voice_gender: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="female_hindi">Google Hindi Female (Polite)</SelectItem>
                      <SelectItem value="male_hindi">Google Hindi Male</SelectItem>
                      <SelectItem value="female_en">Polly English Female (Emma)</SelectItem>
                      <SelectItem value="male_en">Polly English Male (Joey)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-white/70">Conversational Tone</Label>
                  <Select value={voiceForm.tone} onValueChange={v => setVoiceForm({ ...voiceForm, tone: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="helpful">Helpful & Warm (Recommended)</SelectItem>
                      <SelectItem value="formal">Formal & Corporate</SelectItem>
                      <SelectItem value="direct">Direct & Efficient</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-white/70">Callback Delay</Label>
                  <Select value={voiceForm.callback_delay} onValueChange={v => setVoiceForm({ ...voiceForm, callback_delay: v })}>
                    <SelectTrigger className="bg-white/5 border-white/10 text-white"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-[#151525] border-white/10 text-white">
                      <SelectItem value="immediate">Immediate (within 1 min)</SelectItem>
                      <SelectItem value="3mins">3 Minutes</SelectItem>
                      <SelectItem value="5mins">5 Minutes</SelectItem>
                      <SelectItem value="10mins">10 Minutes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-white/70">Custom AI Instruction Override</Label>
                <textarea rows={4} value={voiceForm.custom_prompt}
                  onChange={e => setVoiceForm({ ...voiceForm, custom_prompt: e.target.value })}
                  className="w-full rounded-md bg-white/5 border border-white/10 text-white p-3 text-sm focus:outline-none focus:ring-1 focus:ring-violet-500"
                  placeholder="e.g. You are the AI receptionist for our business. Greet customers warmly..."
                />
              </div>
            </CardContent>
            <CardFooter className="flex justify-end border-t border-white/5 pt-4">
              <Button onClick={handleSaveVoice} disabled={updateMut.isPending} className="bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white border-0 shadow-lg shadow-violet-500/20">
                {updateMut.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Voice Config
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        {/* ALERTS TAB */}
        <TabsContent value="notifications" className="mt-6">
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white">Notification Preferences</CardTitle>
              <CardDescription className="text-white/40">Select which events trigger alerts for business owners</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {([
                { key: 'whatsapp_hot_leads', label: 'WhatsApp Alerts for Hot Leads', desc: 'Send an instant WhatsApp message to your team when a hot lead is qualified.' },
                { key: 'sms_callback_failures', label: 'SMS Notifications on Callback Failures', desc: 'Receive an SMS alert if Twilio fails to dial the customer after 3 attempts.' },
                { key: 'daily_email_reports', label: 'Daily Emailed Summary Reports', desc: 'Get a daily digest detailing your recovered revenue and overall recovery stats.' },
                { key: 'in_app_sound', label: 'In-App Sound Notifications', desc: 'Play a subtle alert chime when a missed call comes in while dashboard is open.' },
              ] as const).map(item => (
                <div key={item.key} className="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/[0.01]">
                  <div className="space-y-0.5">
                    <Label className="text-sm font-semibold text-white">{item.label}</Label>
                    <p className="text-xs text-white/40">{item.desc}</p>
                  </div>
                  <Switch
                    checked={notifPrefs[item.key]}
                    onCheckedChange={v => setNotifPrefs({ ...notifPrefs, [item.key]: v })}
                  />
                </div>
              ))}
            </CardContent>
            <CardFooter className="flex justify-end border-t border-white/5 pt-4">
              <Button onClick={handleSaveNotifs} disabled={updateNotifMut.isPending} className="bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white border-0 shadow-lg shadow-violet-500/20">
                {updateNotifMut.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Alerts
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        {/* INTEGRATIONS TAB */}
        <TabsContent value="api" className="mt-6">
          <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white">API Integrations</CardTitle>
              <CardDescription className="text-white/40">Integration status — API keys are managed via server environment variables for security</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { label: 'Google Gemini API', envVar: 'GEMINI_API_KEY', description: 'Powers AI insights, lead qualification, and conversation analysis.' },
                { label: 'Twilio Account SID', envVar: 'TWILIO_ACCOUNT_SID', description: 'Handles voice calls, WhatsApp messaging, and SMS.' },
                { label: 'Twilio Auth Token', envVar: 'TWILIO_AUTH_TOKEN', description: 'Authentication for Twilio API requests.' },
                { label: 'Backblaze B2 Storage', envVar: 'BACKBLAZE_KEY_ID', description: 'Stores call recordings and media files.' },
              ].map(integration => (
                <div key={integration.envVar} className="flex items-center justify-between p-4 rounded-lg border border-white/5 bg-white/[0.01]">
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-white">{integration.label}</p>
                    <p className="text-xs text-white/40">{integration.description}</p>
                    <p className="text-[10px] text-white/25 font-mono">ENV: {integration.envVar}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs text-emerald-400 font-medium">Server-managed</span>
                  </div>
                </div>
              ))}
              <div className="p-3 rounded-lg border border-amber-500/20 bg-amber-500/5">
                <p className="text-xs text-amber-300">
                  <strong>Security Note:</strong> API keys are stored as environment variables on the server and are never exposed to the frontend. To update credentials, modify the <code className="font-mono bg-white/5 px-1 rounded">.env</code> file on your server.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
