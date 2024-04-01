<script>
	import { Dialog as SheetPrimitive } from "bits-ui";
	import { fade } from "svelte/transition";
	import { cn } from "$lib/utils.js";
	let className = undefined;
	export let transition = fade;
	export let transitionConfig = {
		duration: 150,
	};
	export { className as class };
</script>

<SheetPrimitive.Overlay
	{transition}
	{transitionConfig}
	class={cn("fixed inset-0 z-50 bg-background/80 backdrop-blur-sm ", className)}
	{...$$restProps}
/>
