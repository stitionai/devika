<script>
  import { socket } from "$lib/api";
  import { agentState, messages } from "$lib/store";
  import { calculateTokens } from "$lib/token";

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
    document.querySelector(".token-count").textContent = `${tokens} tokens`;
  }
</script>

<div class="expandable-input relative">
  <textarea
    id="message-input"
    class="w-full p-2 border-2 rounded-lg pr-20"
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
  <div class="token-count text-gray-400 text-xs p-1">0 tokens</div>
  <button
    id="send-message-btn"
    class={`px-4 py-3 text-white rounded-lg w-full ${isAgentActive ? "bg-slate-800" : "bg-black"}`}
    on:click={handleSendMessage}
    disabled={isAgentActive}
  >
    {@html isAgentActive ? "<i>Agent is busy...</i>" : "Send"}
  </button>
</div>

<style>
  .expandable-input textarea {
    min-height: 60px;
    max-height: 200px;
    resize: none;
  }
</style>
