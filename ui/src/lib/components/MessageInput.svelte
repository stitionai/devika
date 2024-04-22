<script>
  import { API_BASE_URL,  socket } from "$lib/api";
  import { agentState, messages } from "$lib/store";
    import { CornerDownLeft } from "lucide-svelte";

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
          search_engine: serachEngine
        });
      } else {
        socket.emit("user-message", { 
          action: "continue",
          message: messageInput,
          base_model: selectedModel,
          project_name: projectName,
          search_engine: serachEngine
         });
      }
      messageInput = "";
    }
  }

  function calculateTokens(event) {
    const prompt = event.target.value;
    fetch(`${API_BASE_URL}/api/calculate-tokens`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    })
      .then((response) => response.json())
      .then((data) => {
        document.querySelector(".token-count").textContent =
          `${data.token_usage} tokens`;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }


</script>

<div class="expandable-input relative">
  <textarea
    id="message-input"
    class="w-full p-4 font-medium focus:text-foreground rounded-2xl outline-none h-28 pr-20 bg-secondary"
    placeholder="Type your message..."
    bind:value={messageInput}
    on:input={calculateTokens}
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
    class="absolute text-secondary bg-primary p-2 right-4 top-4 rounded-full"
  >
  <CornerDownLeft />    
  </button>

</div>

<style>
  .expandable-input textarea {
    min-height: 60px;
    max-height: 200px;
    resize: none;
  }
</style>
