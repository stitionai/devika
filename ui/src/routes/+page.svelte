<script>
  import { onDestroy, onMount } from "svelte";
  import { toast } from "svelte-sonner";

  import ControlPanel from "$lib/components/ControlPanel.svelte";
  import MessageContainer from "$lib/components/MessageContainer.svelte";
  import MessageInput from "$lib/components/MessageInput.svelte";
  import BrowserWidget from "$lib/components/BrowserWidget.svelte";
  import TerminalWidget from "$lib/components/TerminalWidget.svelte";
  import EditorWidget from "../lib/components/EditorWidget.svelte";
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

      if(!(await checkServerStatus())) {
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

<div class="flex h-full flex-col flex-1 gap-4 p-4 overflow-hidden">
  <ControlPanel />

  {#if $serverStatus === undefined}
    <div class="flex items-center justify-center h-full">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p class="text-foreground-light">Connecting to server...</p>
      </div>
    </div>
  {:else if !$serverStatus}
    <div class="flex items-center justify-center h-full">
      <div class="text-center">
        <p class="text-red-500 mb-2">Failed to connect to server</p>
        <button
          class="px-4 py-2 bg-primary text-foreground-invert rounded hover:bg-btn-active"
          on:click={() => window.location.reload()}>
          Retry Connection
        </button>
      </div>
    </div>
  {:else}
    <div class="flex h-full overflow-x-auto md:overflow-x-hidden">
      <div class="flex flex-col md:flex-row w-full h-full gap-2">
        <div class="flex flex-col gap-2 w-full h-full md:w-1/2 lg:w-2/5">
          <MessageContainer />
          <MessageInput />
        </div>
        <div class="flex flex-col gap-4 h-full w-full md:w-1/2 lg:w-3/5 p-2">
          <BrowserWidget />
          <TerminalWidget />
          <EditorWidget />
        </div>
      </div>
    </div>
  {/if}
</div>
