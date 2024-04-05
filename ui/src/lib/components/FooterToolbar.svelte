<script>
	import Seperator from './ui/Seperator.svelte';
</script>

<div class="px-2">
	<div
		class="border-t flex items-center justify-between p-1.5 text-[13px] border-border"
	>
		<!-- right -->
		<div>
			<div class="relative group px-1.5 py-0.5 hover:bg-secondary rounded-md">
				<p>
					Status:
					<span class="text-white"> setting up API server </span>
				</p>

                <div class="absolute hidden group-hover:block -left-1 text-[13px] w-[400px] bg-monologue-background bottom-8 duration-300 p-3 rounded-2xl space-y-2 outline outline-monologue-outline z-20">
                    <p>Monologue:</p>
                    <p class="text-white">Okay, let me break down this step-by-step plan into simple, easy-to-follow instructions for printing numbers in Python. I'll make sure to explain each step clearly and concisely.</p>
                </div>
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
