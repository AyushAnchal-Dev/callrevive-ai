import { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Sparkles, TrendingUp, AlertTriangle, ArrowUpRight, DollarSign, Lightbulb, Heart, Target, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { useOverview } from '../hooks/useAnalytics';
import { analyticsApi } from '../api/analytics';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export default function AIInsightsPage() {
  const { data: overview, isLoading: overviewLoading } = useOverview();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [aiMetrics, setAiMetrics] = useState<any>(null);
  const [generating, setGenerating] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);
  const navigate = useNavigate();

  const generateInsights = async () => {
    setGenerating(true);
    try {
      const data = await analyticsApi.getAIInsights();
      setRecommendations(data.recommendations || []);
      setAiMetrics(data);
      setHasGenerated(true);
      toast.success('AI insights generated!');
    } catch {
      toast.error('Failed to generate insights');
    } finally {
      setGenerating(false);
    }
  };

  const revenueRecovered = aiMetrics?.revenue_recovered ?? overview?.revenueRecovered ?? 0;
  const conversionRate = aiMetrics?.conversion_rate ?? overview?.recoveryRate ?? 0;
  const recoveryRate = aiMetrics?.recovery_rate ?? overview?.recoveryRate ?? 0;

  const statusRoutes: Record<string, string> = {
    'Action Needed': '/leads',
    'Configure Auto-Reply': '/settings',
    'Send WhatsApp': '/conversations',
    'Review Transcripts': '/conversations',
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white">AI Insights</h1>
            <Sparkles className="w-5 h-5 text-violet-400 animate-pulse" />
          </div>
          <p className="text-sm text-white/40">Real-time revenue intelligence and business growth suggestions</p>
        </div>
        <Button onClick={generateInsights} disabled={generating}
          className="bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white border-0 shadow-lg shadow-violet-500/20">
          {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Brain className="w-4 h-4 mr-2" />}
          {generating ? 'Generating...' : 'Generate New Recommendations'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-white/60">Revenue Recovery Health</CardTitle>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-3xl font-bold text-white">{overviewLoading ? '...' : `₹${revenueRecovered.toLocaleString('en-IN')}`}</p>
              <p className="text-xs text-white/40 mt-1">Recovered in the last 30 days</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-white/60">Recovery Rate</span>
                <span className="text-emerald-400 font-medium">{recoveryRate}%</span>
              </div>
              <Progress value={recoveryRate} className="h-1.5 bg-white/10" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-white/60">AI Lead Conversion Rate</CardTitle>
              <Target className="w-4 h-4 text-violet-400" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-3xl font-bold text-white">{overviewLoading ? '...' : `${conversionRate}%`}</p>
              <p className="text-xs text-white/40 mt-1">From automated call to qualified lead</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-white/60">Industry Benchmark</span>
                <span className="text-white/40">28.0%</span>
              </div>
              <Progress value={Math.min(conversionRate / 0.5, 100)} className="h-1.5 bg-white/10" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 border-white/10 backdrop-blur-xl">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-white/60">Active Metrics</CardTitle>
              <Heart className="w-4 h-4 text-rose-400" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-3xl font-bold text-white">{overviewLoading ? '...' : overview?.hotLeads ?? 0} Hot</p>
              <p className="text-xs text-white/40 mt-1">Leads requiring immediate attention</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-white/60">Total leads</span>
                <span className="text-white/40">{overview?.totalLeads ?? 0}</span>
              </div>
              <Progress value={overview?.totalLeads ? ((overview?.hotLeads ?? 0) / overview.totalLeads) * 100 : 0} className="h-1.5 bg-white/10" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6">
        <div className="flex items-center gap-2 mb-6">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <h3 className="text-lg font-bold text-white">AI Action Plan</h3>
        </div>
        {!hasGenerated ? (
          <div className="py-12 text-center">
            <Brain className="w-10 h-10 text-white/15 mx-auto mb-3" />
            <p className="text-sm text-white/40">Click "Generate New Recommendations" to get AI-powered insights</p>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-sm text-white/40">No recommendations generated. Try again.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec: any, idx: number) => (
              <motion.div key={idx} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}
                className="p-5 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-violet-500/20 transition-all flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300">{rec.category}</span>
                    <span className="text-[11px] font-medium text-emerald-400">{rec.impact}</span>
                  </div>
                  <h4 className="text-base font-bold text-white mb-2">{rec.title}</h4>
                  <p className="text-xs text-white/60 leading-relaxed mb-4">{rec.description}</p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <span className="text-[10px] text-white/30 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3 text-yellow-400/70" /> Recommended action
                  </span>
                  <Button size="sm" onClick={() => navigate(statusRoutes[rec.status] || '/dashboard')}
                    className="bg-white/10 hover:bg-white/20 text-white text-xs border-0">
                    {rec.status} <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
