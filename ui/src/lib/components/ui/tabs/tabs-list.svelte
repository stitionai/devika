<script>
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";
	let className = undefined;
	export { className as class };
</script>

<TabsPrimitive.List
	class={cn(
		"inline-flex h-10 items-center justify-start rounded-md bg-muted p-1 text-muted-foreground mb-3",
		className
	)}
	{...$$restProps}
>
	<slot />
</TabsPrimitive.List>
