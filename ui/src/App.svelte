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

<div class="flex flex-col h-screen bg-[#101010]">
  <ControlPanel />

  <div class="flex flex-row  flex-1 p-0">
    
    <Sidebar />

    <div class="flex h-full w-full">
      <div class="flex flex-col w-1/2 h-full">
        <MessageContainer />
        <InternalMonologue />
        <MessageInput />
      </div>

      <div class="flex flex-col w-1/2 space-y-2 p-3">
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
    width: 2px;
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