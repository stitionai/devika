<script>
  import { cn } from "$lib/utils.js";
  
  let className = undefined;
  export { className as class };
  
  export let variant = "default";
  export let size = "default";
  export let type = "button";
  export let disabled = false;
</script>

<button
  {type}
  class={cn(
    "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
    {
      "bg-primary text-primary-foreground shadow hover:bg-primary/90": variant === "default",
      "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90": variant === "destructive",
      "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground": variant === "outline",
      "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80": variant === "secondary",
      "bg-transparent text-foreground underline-offset-4 hover:underline": variant === "link",
      "h-9 px-4 py-2": size === "default",
      "h-8 rounded-md px-3 text-xs": size === "sm",
      "h-10 rounded-md px-8": size === "lg",
      "h-11 rounded-md px-8": size === "xl"
    },
    className
  )}
  {disabled}
  on:click
  on:keydown
  {...$$restProps}
>
  <slot />
</button>