<script>
  import { sendMessage, executeAgent, API_BASE_URL } from "../api";
  import { agentState, messages } from "../store";

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

<div class="expandable-input flex flex-col mt-0 gap-3 p-3 ">
  <div class="flex flex-row w-full h-fit gap-3 ">
     <textarea
    id="message-input"
    class="text-sm w-full flex flex-row items-center  max-h-[200px] resize-none  bg-[#1d2228] rounded-xl ltr outline-none  p-3 box-content  text-white overflow-y-scroll"
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
    id="send-message-btn"
    class={` px-4 py-2 rounded w-20  ${isAgentActive ? "bg-slate-800" : "bg-indigo-700 hover:bg-indigo-600 active:bg-indigo-800"}`}
    on:click={handleSendMessage}
    disabled={isAgentActive}
  >
    <i class="fas fa-paper-plane"></i>
    <!-- {@html isAgentActive ? "<i>Agent is busy...</i>" : "Send"} -->
  </button> 
  
  </div>
  <div class="token-count right-2 bottom-2 text-gray-400 text-xs">
    0 tokens
  </div>
</div>

<style>
  
</style>