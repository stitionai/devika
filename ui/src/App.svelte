<script>
  import { onMount } from "svelte";
  import Sidebar from "./components/Sidebar.svelte";
  import ControlPanel from "./components/ControlPanel.svelte";
  import MessageContainer from "./components/MessageContainer.svelte";
  import InternalMonologue from "./components/InternalMonologue.svelte";
  import MessageInput from "./components/MessageInput.svelte";
  import BrowserWidget from "./components/BrowserWidget.svelte";
  import TerminalWidget from "./components/TerminalWidget.svelte";
  import {
    fetchProjectList,
    fetchModelList,
    fetchAgentState,
    fetchMessages,
    checkInternetStatus,
  } from "./api";

  onMount(() => {
    localStorage.clear();

    const intervalId = setInterval(async () => {
      await fetchProjectList();
      await fetchModelList();
      await fetchAgentState();
      await fetchMessages();
      await checkInternetStatus();
    }, 1000);

    return () => clearInterval(intervalId);
  });
</script>

<div class="flex h-screen">
  <Sidebar />

  <div class="flex flex-col flex-1 p-4">
    <ControlPanel />

    <div class="flex h-full space-x-4">
      <div class="flex flex-col w-1/2">
        <MessageContainer />
        <InternalMonologue />
        <MessageInput />
      </div>

      <div class="flex flex-col w-1/2 space-y-4">
        <BrowserWidget />
        <TerminalWidget />
      </div>
    </div>
  </div>
</div>

<style>
  @import "tailwindcss/base";
  @import "tailwindcss/components";
  @import "tailwindcss/utilities";

  :global(::-webkit-scrollbar) {
    width: 10px;
  }

  :global(::-webkit-scrollbar-track) {
    background: #2d3748;
    border-radius: 10px;
  }

  :global(::-webkit-scrollbar-thumb) {
    background: #4a5568;
    border-radius: 10px;
  }

  :global(::-webkit-scrollbar-thumb:hover) {
    background: #6b7280;
  }
</style>