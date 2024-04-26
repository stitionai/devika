<script>
  import { onDestroy, onMount } from "svelte";
  import { toast } from "svelte-sonner";

  import ControlPanel from "$lib/components/ControlPanel.svelte";
  import MessageContainer from "$lib/components/MessageContainer.svelte";
  import MessageInput from "$lib/components/MessageInput.svelte";
  import BrowserWidget from "$lib/components/BrowserWidget.svelte";
  import TerminalWidget from "$lib/components/TerminalWidget.svelte";
  import * as Resizable from "$lib/components/ui/resizable/index.js";

  import { serverStatus } from "$lib/store";
  import { initializeSockets, destroySockets } from "$lib/sockets";
  import { checkInternetStatus, checkServerStatus } from "$lib/api";


  let resizeEnabled =
    localStorage.getItem("resize") &&
    localStorage.getItem("resize") === "enable";

  onMount(() => {
    const load = async () => {
      await checkInternetStatus();

      if(!await checkServerStatus()) {
        toast.error("Failed to connect to server");
        return;
      }
      serverStatus.set(true);
      await initializeSockets();
    };
    load();
  });
  onDestroy(() => {
    destroySockets();
  });
</script>

<div class="flex h-full flex-col flex-1 gap-4 p-4">
  <ControlPanel />

  <Resizable.PaneGroup direction="horizontal" class="max-w-full">
    <Resizable.Pane defaultSize={50}>
      <div class="flex flex-col gap-2 w-full h-full pr-4">
        <MessageContainer />
        <MessageInput />
      </div>
    </Resizable.Pane>
    {#if resizeEnabled}
      <Resizable.Handle />
    {/if}
    <Resizable.Pane defaultSize={50}>
      <Resizable.PaneGroup direction="vertical">
        <Resizable.Pane defaultSize={50}>
          <div class="flex h-full items-center justify-center p-2">
            <BrowserWidget />
          </div>
        </Resizable.Pane>
        <!-- {#if resizeEnabled}
          <Resizable.Handle />
        {/if} -->
        <Resizable.Pane defaultSize={50}>
          <div class="flex h-full items-center justify-center p-2">
            <TerminalWidget />
          </div>
        </Resizable.Pane>
      </Resizable.PaneGroup>
    </Resizable.Pane>
  </Resizable.PaneGroup>
</div>
