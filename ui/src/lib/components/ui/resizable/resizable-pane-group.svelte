<script>
	import * as ResizablePrimitive from "paneforge";
	import { cn } from "$lib/utils.js";
	let className = undefined;
	export let direction;
	export let paneGroup = undefined;
	export let el = undefined;
	export { className as class };
</script>

<ResizablePrimitive.PaneGroup
	bind:el
	bind:paneGroup
	{direction}
	class={cn("flex h-full w-full data-[direction=vertical]:flex-col", className)}
	{...$$restProps}
>
	<slot />
</ResizablePrimitive.PaneGroup>
