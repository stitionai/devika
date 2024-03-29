<script>
	import Sidebar from "$lib/components/Sidebar.svelte";
	import "../app.pcss";
</script>

<main class="ml-20 h-dvh">
	<Sidebar />
	<slot />
</main>
