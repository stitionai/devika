<script>
  import Sidebar from "$lib/components/Sidebar.svelte";
  import "../app.pcss";
</script>

<main>
  <div class="flex h-dvh w-full">
    <Sidebar />
    <slot />
  </div>
  <div>
<!-- TODO bottom bar -->
  </div>
</main>
