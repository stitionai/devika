<script>
  import Sidebar from "$lib/components/Sidebar.svelte";
  import "../app.pcss";
</script>

<main class="flex h-dvh w-full">
	<Sidebar />
	<slot />
</main>
