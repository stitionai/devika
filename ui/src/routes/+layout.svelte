<script>
  import Sidebar from "$lib/components/Sidebar.svelte";
  import { Toaster } from "$lib/components/ui/sonner";
  import { ModeWatcher } from "mode-watcher";
  import "../app.pcss";
</script>

<main>
  <div class="h-dvh w-full flex">
      <Toaster richColors/>
      <ModeWatcher />
      <Sidebar />
      <slot />
  </div>
</main>
