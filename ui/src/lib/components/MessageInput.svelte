<script>
  import { sendMessage, executeAgent, API_BASE_URL } from "$lib/api";
  import { agentState, messages } from "$lib/store";

  let isAgentActive = false;

  if ($agentState !== null) {
    isAgentActive = $agentState.agent_is_active;
    console.log("Agent is active", isAgentActive);
  }

  let messageInput = "";
  async function handleSendMessage() {
    const projectName = localStorage.getItem("selectedProject");

    if (!projectName) {
      alert("Please select a project first!");
      return;
    }

    if (messageInput.trim() !== "" && !isAgentActive) {
      if ($messages.length === 0) {
        console.log("Executing agent", messageInput);
        await executeAgent(messageInput);
      } else {
        console.log("Sending message", messageInput);
        await sendMessage(messageInput);
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

<div class="expandable-input mt-4 relative">
  <textarea
    id="message-input"
    class="w-full p-2 bg-slate-800 rounded pr-20"
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
  <div class="token-count absolute right-2 bottom-2 text-gray-400 text-xs">
    0 tokens
  </div>
  <button
    id="send-message-btn"
    class={`px-4 py-2 rounded w-full mt-2 ${isAgentActive ? "bg-slate-800" : "bg-indigo-700"}`}
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
    overflow-y: hidden;
    resize: none;
  }
</style>