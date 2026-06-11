import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary/15 text-primary",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground",
        destructive:
          "border-transparent bg-destructive/15 text-destructive",
        outline: "text-foreground border-border",
        hot: "border-rose-400/20 bg-rose-400/10 text-rose-400 animate-hot-pulse",
        warm: "border-amber-400/20 bg-amber-400/10 text-amber-400",
        cold: "border-blue-400/20 bg-blue-400/10 text-blue-400",
        success:
          "border-emerald-400/20 bg-emerald-400/10 text-emerald-400",
        warning:
          "border-amber-400/20 bg-amber-400/10 text-amber-400",
        critical:
          "border-rose-400/20 bg-rose-400/10 text-rose-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
