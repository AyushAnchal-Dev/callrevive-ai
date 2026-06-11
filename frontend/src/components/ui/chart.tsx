import * as React from "react";
import * as RechartsPrimitive from "recharts";
import { cn } from "@/lib/utils";

// Chart config type
export type ChartConfig = Record<
  string,
  {
    label?: React.ReactNode;
    icon?: React.ComponentType;
    color?: string;
    theme?: Record<string, string>;
  }
>;

type ChartContextProps = {
  config: ChartConfig;
};

const ChartContext = React.createContext<ChartContextProps | null>(null);

function useChart() {
  const context = React.useContext(ChartContext);
  if (!context) {
    throw new Error("useChart must be used within a <ChartContainer />");
  }
  return context;
}

interface ChartContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  config: ChartConfig;
  children: React.ComponentProps<
    typeof RechartsPrimitive.ResponsiveContainer
  >["children"];
}

const ChartContainer = React.forwardRef<HTMLDivElement, ChartContainerProps>(
  ({ id, className, children, config, ...props }, ref) => {
    const uniqueId = React.useId();
    const chartId = `chart-${id || uniqueId.replace(/:/g, "")}`;

    return (
      <ChartContext.Provider value={{ config }}>
        <div
          data-chart={chartId}
          ref={ref}
          className={cn(
            "flex aspect-video justify-center text-xs",
            "[&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground",
            "[&_.recharts-cartesian-grid_line[stroke='#ccc']]:stroke-border/30",
            "[&_.recharts-curve.recharts-tooltip-cursor]:stroke-border",
            "[&_.recharts-dot[stroke='#fff']]:stroke-transparent",
            "[&_.recharts-layer]:outline-none",
            "[&_.recharts-polar-grid_[stroke='#ccc']]:stroke-border/30",
            "[&_.recharts-radial-bar-background-sector]:fill-muted/30",
            "[&_.recharts-rectangle.recharts-tooltip-cursor]:fill-muted/10",
            "[&_.recharts-reference-line_[stroke='#ccc']]:stroke-border/50",
            "[&_.recharts-sector[stroke='#fff']]:stroke-transparent",
            "[&_.recharts-sector]:outline-none",
            "[&_.recharts-surface]:outline-none",
            className
          )}
          {...props}
        >
          <style
            dangerouslySetInnerHTML={{
              __html: Object.entries(config)
                .map(
                  ([key, value]) =>
                    `[data-chart="${chartId}"] { --color-${key}: ${value.color || "var(--color-chart-1)"}; }`
                )
                .join("\n"),
            }}
          />
          <RechartsPrimitive.ResponsiveContainer>
            {children}
          </RechartsPrimitive.ResponsiveContainer>
        </div>
      </ChartContext.Provider>
    );
  }
);
ChartContainer.displayName = "ChartContainer";

const ChartTooltip = RechartsPrimitive.Tooltip;

interface ChartTooltipContentProps
  extends React.ComponentPropsWithoutRef<"div"> {
  hideLabel?: boolean;
  hideIndicator?: boolean;
  indicator?: "line" | "dot" | "dashed";
  nameKey?: string;
  labelKey?: string;
  labelFormatter?: (label: any, payload: any[]) => React.ReactNode;
  formatter?: (value: any, name: any, item: any, index: any) => React.ReactNode;
}

const ChartTooltipContent = React.forwardRef<
  HTMLDivElement,
  ChartTooltipContentProps & {
    active?: boolean;
    payload?: any[];
    label?: string;
    coordinate?: any;
    position?: any;
    viewBox?: any;
    content?: any;
  }
>(
  (
    {
      active,
      payload,
      className,
      indicator = "dot",
      hideLabel = false,
      hideIndicator = false,
      label,
      labelFormatter,
      formatter,
      nameKey,
      labelKey,
      coordinate,
      position,
      viewBox,
      content,
      ...props
    },
    ref
  ) => {
    const { config } = useChart();

    if (!active || !payload?.length) return null;

    return (
      <div
        ref={ref}
        className={cn(
          "grid min-w-[8rem] items-start gap-1.5 rounded-lg border border-border/60 bg-card/95 backdrop-blur-xl px-3 py-2 text-xs shadow-xl shadow-black/30",
          className
        )}
        {...props}
      >
        {!hideLabel && (
          <div className="font-medium text-foreground">
            {labelFormatter
              ? labelFormatter(label || "", payload)
              : labelKey
                ? payload[0]?.payload?.[labelKey] as string
                : label}
          </div>
        )}
        <div className="grid gap-1">
          {payload.map((item, index) => {
            const key = nameKey || item.dataKey || item.name || "value";
            const itemConfig = config[key] || {};
            const indicatorColor = item.color || itemConfig.color;

            return (
              <div
                key={item.dataKey || index}
                className="flex items-center gap-2 [&>svg]:h-2.5 [&>svg]:w-2.5 [&>svg]:text-muted-foreground"
              >
                {!hideIndicator && (
                  <div
                    className={cn(
                      "shrink-0 rounded-[2px]",
                      indicator === "dot" && "h-2.5 w-2.5 rounded-full",
                      indicator === "line" && "h-0.5 w-4",
                      indicator === "dashed" &&
                        "h-0.5 w-4 border-b-2 border-dashed"
                    )}
                    style={{ backgroundColor: indicatorColor }}
                  />
                )}
                <div className="flex flex-1 items-baseline justify-between gap-3 leading-none">
                  <span className="text-muted-foreground">
                    {itemConfig.label || item.name || key}
                  </span>
                  <span className="font-mono font-medium tabular-nums text-foreground">
                    {formatter
                      ? formatter(item.value, item.name, item, index)
                      : typeof item.value === "number"
                        ? item.value.toLocaleString()
                        : item.value}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }
);
ChartTooltipContent.displayName = "ChartTooltipContent";

const ChartLegend = RechartsPrimitive.Legend;

interface ChartLegendContentProps extends React.ComponentProps<"div"> {
  payload?: Array<{
    value: string;
    type?: string;
    id?: string;
    color?: string;
    dataKey?: string;
  }>;
  nameKey?: string;
  hideIcon?: boolean;
  verticalAlign?: "top" | "bottom";
}

const ChartLegendContent = React.forwardRef<
  HTMLDivElement,
  ChartLegendContentProps
>(({ className, hideIcon = false, payload, nameKey, ...props }, ref) => {
  const { config } = useChart();

  if (!payload?.length) return null;

  return (
    <div
      ref={ref}
      className={cn(
        "flex items-center justify-center gap-4 pt-3",
        className
      )}
      {...props}
    >
      {payload.map((item) => {
        const key = nameKey || item.dataKey || item.value || "value";
        const itemConfig = config[key] || {};

        return (
          <div
            key={item.value}
            className="flex items-center gap-1.5 [&>svg]:h-3 [&>svg]:w-3 [&>svg]:text-muted-foreground"
          >
            {!hideIcon && (
              <div
                className="h-2 w-2 shrink-0 rounded-[2px]"
                style={{
                  backgroundColor: item.color || itemConfig.color,
                }}
              />
            )}
            <span className="text-xs text-muted-foreground">
              {itemConfig.label || item.value}
            </span>
          </div>
        );
      })}
    </div>
  );
});
ChartLegendContent.displayName = "ChartLegendContent";

export {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  useChart,
};
