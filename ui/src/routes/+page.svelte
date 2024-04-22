<script>
  import { onMount } from "svelte";
  import ControlPanel from "$lib/components/ControlPanel.svelte";
  import MessageContainer from "$lib/components/MessageContainer.svelte";
  import MessageInput from "$lib/components/MessageInput.svelte";
  import BrowserWidget from "$lib/components/BrowserWidget.svelte";
  import TerminalWidget from "$lib/components/TerminalWidget.svelte";
  import {
    fetchInitialData,
    fetchAgentState,
    checkInternetStatus,
    socket
  } from "$lib/api";
  import { messages,tokenUsage, agentState } from "$lib/store";

  onMount(() => {
    // localStorage.clear();
    const load = async () => {
      await fetchInitialData();

      await fetchAgentState();
      // await fetchMessages();
      await checkInternetStatus();
    };
    load();

    socket.emit('socket_connect', {data: 'frontend connected!'});
    socket.on('socket_response', function(msg) {console.log(msg)});

    socket.on('server-message', function(data) {
      console.log("server-message: ", data);
      messages.update((msgs) => [...msgs, data['messages']]);
    });

    socket.on('agent-state', function(state) {
      const lastState = state[state.length - 1];
      agentState.set(lastState);
      console.log("server-state: ", lastState);
      });
    
    socket.on('tokens', function(tokens) {
      tokenUsage.set(tokens["token_usage"]);
    });

});
</script>

<div class="flex h-full flex-col flex-1 gap-4 p-4">
  <ControlPanel />

  <div class="flex space-x-4 h-full overflow-y-auto">
    <div class="flex flex-col gap-2 w-1/2">
      <MessageContainer />
      <MessageInput />
    </div>

    <div class="flex flex-col gap-4 w-1/2">
      <BrowserWidget />
      <TerminalWidget />
    </div>
  </div>
</div>
