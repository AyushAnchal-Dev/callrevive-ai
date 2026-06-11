import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, Eye, EyeOff, Loader2, User, Building2, Phone, ArrowLeft, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BUSINESS_CATEGORIES } from "@/lib/constants";
import { useAuth } from "@/hooks/useAuth";

const step1Schema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

const step2Schema = z.object({
  businessName: z.string().min(2, "Business name is required"),
  businessCategory: z.string().min(1, "Please select a category"),
  phone: z.string().min(10, "Please enter a valid phone number"),
});

type Step1Data = z.infer<typeof step1Schema>;
type Step2Data = z.infer<typeof step2Schema>;

export function SignupForm() {
  const [step, setStep] = useState(1);
  const [step1Data, setStep1Data] = useState<Step1Data | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const { registerMutation } = useAuth();

  const step1Form = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });

  const step2Form = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
    defaultValues: { businessName: "", businessCategory: "", phone: "" },
  });

  const handleStep1 = (data: Step1Data) => {
    setStep1Data(data);
    setStep(2);
  };

  const handleStep2 = (data: Step2Data) => {
    if (!step1Data) return;
    registerMutation.mutate(
      {
        name: step1Data.name,
        email: step1Data.email,
        password: step1Data.password,
        businessName: data.businessName,
        businessCategory: data.businessCategory,
        phone: data.phone,
      },
      {
        onError: (error: Error) => {
          toast.error("Registration Failed", {
            description: error.message || "Something went wrong",
          });
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <div className="flex items-center justify-center gap-3">
        {[1, 2].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-all duration-300 ${
                s === step
                  ? "bg-gradient-to-r from-indigo-500 to-violet-500 text-white shadow-lg shadow-violet-500/30"
                  : s < step
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "bg-white/[0.05] text-muted-foreground border border-white/[0.08]"
              }`}
            >
              {s}
            </div>
            {s < 2 && (
              <div
                className={`h-[2px] w-12 rounded transition-colors duration-300 ${
                  step > 1 ? "bg-violet-500" : "bg-white/[0.08]"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {step === 1 && (
          <motion.form
            key="step1"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            onSubmit={step1Form.handleSubmit(handleStep1)}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Full Name</Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="John Doe"
                  className="pl-10 bg-white/[0.04] border-white/[0.08] h-11"
                  {...step1Form.register("name")}
                />
              </div>
              {step1Form.formState.errors.name && (
                <p className="text-xs text-rose-400">
                  {step1Form.formState.errors.name.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="email"
                  placeholder="you@example.com"
                  className="pl-10 bg-white/[0.04] border-white/[0.08] h-11"
                  {...step1Form.register("email")}
                />
              </div>
              {step1Form.formState.errors.email && (
                <p className="text-xs text-rose-400">
                  {step1Form.formState.errors.email.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  className="pl-10 pr-10 bg-white/[0.04] border-white/[0.08] h-11"
                  {...step1Form.register("password")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {step1Form.formState.errors.password && (
                <p className="text-xs text-rose-400">
                  {step1Form.formState.errors.password.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">
                Confirm Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type={showConfirm ? "text" : "password"}
                  placeholder="••••••••"
                  className="pl-10 pr-10 bg-white/[0.04] border-white/[0.08] h-11"
                  {...step1Form.register("confirmPassword")}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={showConfirm ? "Hide confirm password" : "Show confirm password"}
                >
                  {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {step1Form.formState.errors.confirmPassword && (
                <p className="text-xs text-rose-400">
                  {step1Form.formState.errors.confirmPassword.message}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full h-11 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white font-semibold shadow-lg shadow-violet-500/25"
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </motion.form>
        )}

        {step === 2 && (
          <motion.form
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
            onSubmit={step2Form.handleSubmit(handleStep2)}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">
                Business Name
              </Label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Acme Corp"
                  className="pl-10 bg-white/[0.04] border-white/[0.08] h-11"
                  {...step2Form.register("businessName")}
                />
              </div>
              {step2Form.formState.errors.businessName && (
                <p className="text-xs text-rose-400">
                  {step2Form.formState.errors.businessName.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">
                Business Category
              </Label>
              <Select
                onValueChange={(val) =>
                  step2Form.setValue("businessCategory", val)
                }
              >
                <SelectTrigger className="bg-white/[0.04] border-white/[0.08] h-11">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {BUSINESS_CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {step2Form.formState.errors.businessCategory && (
                <p className="text-xs text-rose-400">
                  {step2Form.formState.errors.businessCategory.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">
                Phone Number
              </Label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="tel"
                  placeholder="+91 98765 43210"
                  className="pl-10 bg-white/[0.04] border-white/[0.08] h-11"
                  {...step2Form.register("phone")}
                />
              </div>
              {step2Form.formState.errors.phone && (
                <p className="text-xs text-rose-400">
                  {step2Form.formState.errors.phone.message}
                </p>
              )}
            </div>

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                className="flex-1 h-11"
                onClick={() => setStep(1)}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <Button
                type="submit"
                disabled={registerMutation.isPending}
                className="flex-1 h-11 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white font-semibold shadow-lg shadow-violet-500/25"
              >
                {registerMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Create Account"
                )}
              </Button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}
