<script>
	import { agentState } from "$lib/store";
</script>

<div
	class="internal-monologue mt-4 flex items-start space-x-3 rounded border border-indigo-700 bg-slate-950 p-2"
>
	<img
		src="/assets/devika-avatar.png"
		alt="Devika's Avatar"
		class="avatar flex-shrink-0 rounded-full"
	/>
	<div>
		<p class="text-xs text-gray-400">Devika's Internal Monologue</p>
		<p class="text-sm">{$agentState?.internal_monologue || "😴"}</p>
	</div>
</div>

<style>
	.avatar {
		width: 40px;
		height: 40px;
	}
</style>
