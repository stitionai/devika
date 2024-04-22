<script>
	import { Dialog as SheetPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";
	let className = undefined;
	export { className as class };
</script>

<SheetPrimitive.Description class={cn("text-sm text-muted-foreground", className)} {...$$restProps}>
	<slot />
</SheetPrimitive.Description>
