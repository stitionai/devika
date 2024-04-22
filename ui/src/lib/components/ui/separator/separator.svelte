<script>
	import { Separator as SeparatorPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";
	let className = undefined;
	export let orientation = "horizontal";
	export let decorative = undefined;
	export { className as class };
</script>

<SeparatorPrimitive.Root
	class={cn(
		"shrink-0 bg-border",
		orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
		className
	)}
	{orientation}
	{decorative}
	{...$$restProps}
/>
