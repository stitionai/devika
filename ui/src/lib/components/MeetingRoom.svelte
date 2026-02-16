<script>
  import { onMount } from "svelte";
  import AgentAvatar from "./AgentAvatar.svelte";
  import ChatBubble from "./ChatBubble.svelte";
  import { socket } from "$lib/api";
  import { agentPresence, meetingMessages, roomState } from "$lib/store";
  
  // Agent configurations
  const agents = [
    { id: "bambu-executiveusa", name: "Bambu", role: "CEO & Coordinator", color: "#4F46E5" },
    { id: "pauli-planner", name: "Pauli", role: "Planner", color: "#059669" },
    { id: "synthia-executor", name: "Synthia", role: "Executor", color: "#DC2626" },
    { id: "alex-metagpt", name: "Alex", role: "Developer", color: "#D97706" }
  ];
  
  let messageInput = "";
  let messages = [];
  let speakingAgent = null;
  let typingAgents = new Set();
  
  // Subscribe to store updates
  $: presence = $agentPresence || [];
  $: currentRoomState = $roomState || {};
  
  function sendMessage() {
    if (!messageInput.trim()) return;
    
    socket.emit("meeting-message", {
      content: messageInput,
      agent_id: "user" // User messages
    });
    
    messageInput = "";
  }
  
  function handleKeyPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }
  
  onMount(() => {
    // Listen for agent messages
    socket.on("agent-speaking", (data) => {
      speakingAgent = data.message.agent_id;
      messages = [...messages, data.message];
      
      // Clear speaking indicator after delay
      setTimeout(() => {
        if (speakingAgent === data.message.agent_id) {
          speakingAgent = null;
        }
      }, 2000);
    });
    
    // Listen for agent typing
    socket.on("agent-typing", (data) => {
      if (data.is_typing) {
        typingAgents.add(data.agent_id);
      } else {
        typingAgents.delete(data.agent_id);
      }
      typingAgents = typingAgents; // Trigger reactivity
    });
    
    // Listen for meeting events
    socket.on("meeting-started", (data) => {
      messages = [...messages, {
        agent_id: "system",
        agent_name: "System",
        content: `Meeting "${data.meeting.title}" has started`,
        timestamp: new Date().toISOString()
      }];
    });
    
    socket.on("meeting-ended", (data) => {
      messages = [...messages, {
        agent_id: "system",
        agent_name: "System",
        content: `Meeting "${data.meeting.title}" has ended`,
        timestamp: new Date().toISOString()
      }];
    });
  });
</script>

<div class="flex h-full gap-4">
  <!-- Agent Avatars Section -->
  <div class="flex flex-col w-1/3 bg-secondary rounded-xl p-4">
    <h2 class="text-lg font-semibold mb-4 text-primary">Agents in Room</h2>
    
    <div class="grid grid-cols-2 gap-4">
      {#each agents as agent}
        <AgentAvatar 
          {agent}
          presence={presence.find(p => p.agent_id === agent.id)}
          isSpeaking={speakingAgent === agent.id}
          isTyping={typingAgents.has(agent.id)}
        />
      {/each}
    </div>
    
    <!-- Room Status -->
    <div class="mt-4 p-3 bg-primary/10 rounded-lg">
      <h3 class="text-sm font-medium text-primary">Room Status</h3>
      <p class="text-xs text-muted-foreground mt-1">
        Active Meeting: {currentRoomState.active_meeting_id ? 'Yes' : 'No'}
      </p>
      <p class="text-xs text-muted-foreground">
        Agents in Room: {currentRoomState.agents_in_room?.length || 0}
      </p>
    </div>
  </div>
  
  <!-- Chat Section -->
  <div class="flex flex-col flex-1 bg-secondary rounded-xl p-4">
    <h2 class="text-lg font-semibold mb-4 text-primary">Meeting Chat</h2>
    
    <!-- Messages -->
    <div class="flex-1 overflow-y-auto space-y-2 mb-4">
      {#each messages as message}
        <ChatBubble {message} />
      {/each}
      
      {#if messages.length === 0}
        <div class="text-center text-muted-foreground py-8">
          <p>No messages yet. Start a conversation!</p>
        </div>
      {/if}
    </div>
    
    <!-- Input -->
    <div class="flex gap-2">
      <input
        type="text"
        bind:value={messageInput}
        on:keypress={handleKeyPress}
        placeholder="Type a message..."
        class="flex-1 px-4 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
      />
      <button
        on:click={sendMessage}
        class="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
      >
        Send
      </button>
    </div>
  </div>
</div>