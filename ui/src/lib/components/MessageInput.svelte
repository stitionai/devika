<script>
  import { socket } from "$lib/api";
  import { agentState, messages } from "$lib/store";
  import { calculateTokens } from "$lib/token";
  import { Icons } from "../icons";

  let isAgentActive = false;

  if ($agentState !== null) {
    isAgentActive = $agentState.agent_is_active;
  }

  let messageInput = "";
  async function handleSendMessage() {
    const projectName = localStorage.getItem("selectedProject");
    const selectedModel = localStorage.getItem("selectedModel");
    const serachEngine = localStorage.getItem("selectedSearchEngine");

    if (!projectName) {
      alert("Please select a project first!");
      return;
    }
    if (!selectedModel) {
      alert("Please select a model first!");
      return;
    }

    if (messageInput.trim() !== "" && !isAgentActive) {
      if ($messages.length === 0) {
        socket.emit("user-message", { 
          action: "execute_agent",
          message: messageInput,
          base_model: selectedModel,
          project_name: projectName,
          search_engine: serachEngine,
        });
      } else {
        socket.emit("user-message", { 
          action: "continue",
          message: messageInput,
          base_model: selectedModel,
          project_name: projectName,
          search_engine: serachEngine,
        });
      }
      messageInput = "";
    }
  }

  function setTokenSize(event) {
    const prompt = event.target.value;
    let tokens = calculateTokens(prompt);
    document.querySelector(".token-count").textContent = `${tokens}`;
  }
</script>

<div class="expandable-input relative">
  <div class="py-3 px-1 rounded-md text-xs">
    Agent status:
    {#if $agentState !== null}
      {#if $agentState.agent_is_active}
        <span class="text-green-500">Active</span>
      {:else}
        <span class="text-orange-600">Inactive</span>
      {/if}
    {:else}
      Deactive
    {/if}
  </div>

  <textarea
    id="message-input"
    class="w-full p-4 font-medium focus:text-foreground rounded-xl outline-none h-28 pr-20 bg-secondary"
    placeholder="Type your message..."
    bind:value={messageInput}
    on:input={setTokenSize}
    on:keydown={(e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    }}
  ></textarea>

  <button 
    on:click={handleSendMessage}
    disabled={isAgentActive}
    class="absolute text-secondary bg-primary p-2 right-4 bottom-6 rounded-full"
  >
  {@html Icons.CornerDownLeft} 
  </button>
  <p class="absolute text-tertiary p-2 right-4 top-12">
    <span class="token-count">0</span>
  </p>
</div>

<style>
  .expandable-input textarea {
    min-height: 60px;
    max-height: 200px;
    resize: none;
  }
</style>
