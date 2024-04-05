<script>
  import Sidebar from "$lib/components/Sidebar.svelte";
  import FooterToolbar from "$lib/components/FooterToolbar.svelte";
  import "../app.pcss";
</script>

<main>
  <div class="h-dvh w-full flex flex-col">
    <div class="flex w-full h-full">
      <Sidebar />
      <slot />
    </div>
  
    <FooterToolbar />
  </div>
  
</main>
