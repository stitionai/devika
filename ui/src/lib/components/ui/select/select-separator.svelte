<script>
	import { Select as SelectPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";
	let className = undefined;
	export { className as class };
</script>

<SelectPrimitive.Separator class={cn("-mx-1 my-1 h-px bg-muted", className)} {...$$restProps} />
