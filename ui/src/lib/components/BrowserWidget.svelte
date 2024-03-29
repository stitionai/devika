<script>
	import { agentState } from "$lib/store";
	import { API_BASE_URL } from "$lib/api";
</script>

<div class="flex flex-1 flex-col overflow-hidden rounded border border-indigo-700 bg-slate-950">
	<div class="flex items-center border-b border-gray-700 p-2">
		<div class="ml-2 mr-4 flex space-x-2">
			<div class="h-3 w-3 rounded-full bg-red-500"></div>
			<div class="h-3 w-3 rounded-full bg-yellow-400"></div>
			<div class="h-3 w-3 rounded-full bg-green-500"></div>
		</div>
		<input
			type="text"
			id="browser-url"
			class="flex-grow rounded bg-slate-900 p-2"
			placeholder="chrome://newtab"
			value={$agentState?.browser_session.url || ""}
			readonly
		/>
	</div>
	<div id="browser-content" class="flex-grow overflow-auto">
		{#if $agentState?.browser_session.screenshot}
			<img
				class="browser-img"
				src={API_BASE_URL +
					"/api/get-browser-snapshot?snapshot_path=" +
					$agentState?.browser_session.screenshot}
				alt="Browser snapshot"
			/>
		{:else}
			<div class="mt-5 text-center text-white">
				<strong>💡 TIP:</strong> You can include a Git URL in your prompt to clone a repo!
			</div>
		{/if}
	</div>
</div>

<style>
	#browser-url {
		pointer-events: none;
	}

	.browser-img {
		display: block;
		object-fit: contain;
		max-width: 100%;
	}
</style>
