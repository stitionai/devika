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

  <div class="flex h-full overflow-x-scroll">
    <div class="flex flex-1 min-w-[calc(100vw-120px)] h-full gap-2">
      <div class="flex flex-col gap-2 w-full h-full pr-4">
        <MessageContainer />
        <MessageInput />
      </div>
      <div class="flex flex-col gap-4 h-full w-full p-2">
        <BrowserWidget />
        <TerminalWidget />
      </div>
    </div>
    <div class="flex flex-col gap-2 min-w-[calc(100vw-120px)] h-full pr-4 p-2">
      <EditorWidget />
    </div>
  </div>
</div>