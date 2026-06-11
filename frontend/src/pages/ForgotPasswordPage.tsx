import { motion } from 'framer-motion';
import { Phone, Sparkles } from 'lucide-react';
import { ForgotPasswordForm } from '../components/auth/ForgotPasswordForm';
import { Link } from 'react-router-dom';

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0f] relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(99,102,241,0.15)_0%,_transparent_70%)]" />
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="relative z-10 w-full max-w-md mx-4">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-2xl p-8 shadow-2xl">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-white">Reset Password</h1>
            <p className="text-sm text-white/40 mt-1">Enter your email to receive a reset link</p>
          </div>
          <ForgotPasswordForm />
          <p className="text-center text-sm text-white/40 mt-6">
            <Link to="/login" className="text-violet-400 hover:text-violet-300">← Back to login</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
