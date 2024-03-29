<script lang="ts">
	import clsx from "clsx";
	export let isActive: boolean = undefined;
	export let disabled: boolean = undefined;
	export let onClick: () => void = undefined;
	export let activeText: string = undefined;
	export let text: string;
	export let type: "button" | "submit" | "reset" = undefined;
</script>

<button
	class={clsx(
		`mt-2 w-full rounded px-4 py-2 ${isActive ? "bg-slate-800" : "bg-indigo-700"}`,
		disabled ? "cursor-not-allowed bg-gray-600" : "cursor-pointer"
	)}
	on:click={onClick}
	disabled={isActive || disabled}
	{type}
>
	{@html isActive ? activeText : text}
</button>
