<script>
	export let href = '';
	export let tooltip = '';
	export let isSelected = false;
	export let icon; 
</script>

<a {href}>
	<div class="nav-button relative">
		<button
			class={`text-tertiary flex justify-center w-full hover:transition-colors ${
				isSelected ? 'text-foreground' : 'text-tertiary'
			}`}
		>
			<svelte:component this={icon} />
		</button>
		<span class="tooltip">{tooltip}</span>
	</div>
</a>

<style>
	.tooltip {
		font-size: 12px;
		background-color: black;
		color: white;
		text-align: center;
		border-radius: 100px;
		padding: 5px 10px;
		position: absolute;
		z-index: 1;
		opacity: 0;
		top: 50%;
		left: 90%;
        margin: 0px 12px;
		transform: translateY(-50%);
		transition: opacity 0.3s;
	}

	.nav-button:hover .tooltip {
		visibility: visible;
		opacity: 1;
	}
</style>
