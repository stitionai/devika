<script>
	import "../app.pcss"
	import Sidebar from '$lib/components/Sidebar.svelte'
</script>

<main class="flex h-dvh w-full">
	<Sidebar />
	<slot />
</main>