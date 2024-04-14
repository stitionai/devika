<script>
	import { Select as SelectPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";
    import { Icons } from "../../../icons";
	let className = undefined;
	export let value;
	export let label = undefined;
	export let disabled = undefined;
	export { className as class };
</script>

<SelectPrimitive.Item
	{value}
	{disabled}
	{label}
	class={cn(
		"relative flex w-full select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none data-[disabled]:pointer-events-none data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground data-[disabled]:opacity-50 cursor-pointer",
		className
	)}
	{...$$restProps}
	on:click
	on:keydown
	on:focusin
	on:focusout
	on:pointerleave
	on:pointermove
>
	<span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
		<SelectPrimitive.ItemIndicator class="h-4 w-4">
			{@html Icons.Check}
		</SelectPrimitive.ItemIndicator>
	</span>
	<slot>
		{label || value}
	</slot>
</SelectPrimitive.Item>
