<script>
  import { onMount } from "svelte";
  import ControlPanel from "$lib/components/ControlPanel.svelte";
  import MessageContainer from "$lib/components/MessageContainer.svelte";
  import InternalMonologue from "$lib/components/InternalMonologue.svelte";
  import MessageInput from "$lib/components/MessageInput.svelte";
  import BrowserWidget from "$lib/components/BrowserWidget.svelte";
  import TerminalWidget from "$lib/components/TerminalWidget.svelte";
  import {
    fetchProjectList,
    fetchModelList,
    fetchAgentState,
    fetchMessages,
    checkInternetStatus,
  } from "$lib/api";

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

<div class="flex flex-col p-4 h-full">
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

<style>
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
