<script>
	import { agentState } from "$lib/store";
	import Seperator from "./ui/Seperator.svelte";
</script>

<div class="px-2">
	<div class="border-t flex items-center justify-between p-1.5 text-[13px] border-border">
		<!-- right -->
		<div class="flex">
			<div class="relative group px-1.5 py-0.5 hover:bg-secondary rounded-md">
				<p>
					Monologue:
					<span class="text-white">Hover me</span>
				</p>
				<div class="absolute hidden group-hover:block -left-1 text-[13px] w-[400px] bg-monologue-background bottom-8 duration-300 p-3 rounded-2xl space-y-2 outline outline-monologue-outline z-20">
					<p>Monologue:</p>
					<p class="text-white">
						{$agentState?.internal_monologue || "😴"}
					</p>
				</div>
			</div>
			<Seperator height={24} />
			<div class="relative px-1.5 py-0.5 rounded-md">
				<p>
					Agent status:
					{#if $agentState !== null}
						{#if $agentState.agent_is_active}
							<span class="text-green-500">Active</span>
						{:else}
							<span class="text-orange-600">Inactive</span>
						{/if}
					{:else}
						Deactive
					{/if}
				</p>
			</div>
		</div>

		<!-- left -->
		<div class="flex gap-5 items-center">
			<p>
				Temperature:
				<span class="text-white"> 0.6 </span>
			</p>
			<Seperator height={14} />
			<p>
				Max Tokens:
				<span class="text-white"> 2200 </span>
			</p>
			<Seperator height={14} />
			<p>
				Top P:
				<span class="text-white"> 0.4 </span>
			</p>
		</div>
	</div>
</div>
