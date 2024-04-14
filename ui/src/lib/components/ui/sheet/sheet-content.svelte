<script>
	import { Dialog as SheetPrimitive } from "bits-ui";
	import { fly } from "svelte/transition";
	import { SheetOverlay, SheetPortal, sheetTransitions, sheetVariants } from "./index.js";
	import { cn } from "$lib/utils.js";
    import { Icons } from "../../../icons.js";
	let className = undefined;
	export let side = "right";
	export { className as class };
	export let inTransition = fly;
	export let inTransitionConfig = sheetTransitions[side ?? "right"].in;
	export let outTransition = fly;
	export let outTransitionConfig = sheetTransitions[side ?? "right"].out;
</script>

<SheetPortal>
	<SheetOverlay />
	<SheetPrimitive.Content
		{inTransition}
		{inTransitionConfig}
		{outTransition}
		{outTransitionConfig}
		class={cn(sheetVariants({ side }), className)}
		{...$$restProps}
	>
		<slot />
		<SheetPrimitive.Close
			class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-secondary"
		>
			{@html Icons.X}
			<span class="sr-only">Close</span>
		</SheetPrimitive.Close>
	</SheetPrimitive.Content>
</SheetPortal>
