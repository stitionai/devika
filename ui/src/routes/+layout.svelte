<script>
  import Sidebar from "$lib/components/Sidebar.svelte";
  import "../app.pcss";
</script>

<main class="h-dvh ml-20">
  <Sidebar />
  <slot />
</main>
