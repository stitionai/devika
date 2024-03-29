<div
	class="fixed left-0 top-0 z-10 flex h-dvh w-20 flex-col items-center space-y-4 bg-slate-950 p-4 shadow-2xl shadow-indigo-700"
>
	<div class="nav-button relative rounded p-5">
		<a href="/">
			<button class="flex w-full justify-center text-gray-400 hover:text-white">
				<i class="fas fa-home fa-lg"></i>
			</button>
		</a>
		<span class="tooltip">Home</span>
	</div>
	<div class="nav-button relative rounded p-5">
		<a href="/settings">
			<button class="flex w-full justify-center text-gray-400 hover:text-white">
				<i class="fas fa-cog fa-lg"></i>
			</button>
		</a>
		<span class="tooltip">Settings</span>
	</div>
	<div class="nav-button relative rounded p-5">
		<button class="flex w-full justify-center text-gray-400 hover:text-white">
			<i class="fas fa-history fa-lg"></i>
		</button>
		<span class="tooltip">Logs</span>
	</div>
</div>

<style>
	.tooltip {
		visibility: hidden;
		width: 120px;
		background-color: #10172a;
		color: #fff;
		text-align: center;
		border-radius: 6px;
		padding: 5px 0;
		position: absolute;
		z-index: 1;
		top: 50%;
		left: 150%;
		transform: translateY(-50%);
		opacity: 0;
		transition: opacity 0.3s;
	}

	.nav-button:hover .tooltip {
		visibility: visible;
		opacity: 1;
	}
</style>
