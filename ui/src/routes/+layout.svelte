<script>
  import Sidebar from "$lib/components/Sidebar.svelte";
  import FooterToolbar from "$lib/components/FooterToolbar.svelte";
  import { Toaster } from "$lib/components/ui/sonner";
  import "../app.pcss";
</script>

<main>
  <div class="h-dvh w-full flex flex-col">
    <div class="flex w-full" style="height: calc(100vh - 37px)">
      <Toaster />
      <Sidebar />
      <slot />
    </div>
    <FooterToolbar />
  </div>
</main>
