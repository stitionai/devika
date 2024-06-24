<script>
  import DOMPurify from "dompurify";
  import { emitMessage, socketListener } from "$lib/sockets";
  import { agentState, messages, isSending } from "$lib/store";
  import { calculateTokens } from "$lib/token";
  import { onMount } from "svelte";
  import { Icons } from "../icons";

  let inference_time = 0;

  agentState.subscribe((value) => {
    if (value !== null && value.agent_is_active == false) {
      isSending.set(false);
    }
    if (value == null) {
      inference_time = 0;
    }
  });

  let messageInput = "";

  // Function to escape HTML
  function escapeHTML(input) {
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return input.replace(/[&<>"']/g, function (m) {
      return map[m];
    });
  }

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

    const sanitizedMessage = DOMPurify.sanitize(messageInput);
    const escapedMessage = escapeHTML(sanitizedMessage);


    if (messageInput.trim() !== "" && escapedMessage.trim() !== "" && isSending) {
      $isSending = true;
      emitMessage("user-message", {
        message: escapedMessage,
        base_model: selectedModel,
        project_name: projectName,
        search_engine: serachEngine,
      });
      messageInput = "";
    }
  }
  onMount(() => {
    socketListener("inference", function (data) {
      if (data["type"] == "time") {
        inference_time = data["elapsed_time"];
      }
    });
  });

  function setTokenSize(event) {
    const prompt = event.target.value;
    let tokens = calculateTokens(prompt);
    document.querySelector(".token-count").textContent = `${tokens}`;
  }
</script>

<div class="flex flex-col gap-2">
  <div class="flex gap-4 justify-between">
    <div class="px-1 rounded-md text-xs">
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
    <!-- {#if $agentState !== null} -->
    <div class="px-1 rounded-md text-xs">
      Model Inference: <span class="text-orange-600">{inference_time} sec</span>
    </div>
    <!-- {/if} -->
  </div>

  <div class="expandable-input relative">
    <textarea
      id="message-input"
      class="w-full p-4 font-medium focus:text-foreground rounded-xl outline-none h-28 pr-20 bg-secondary
    {$isSending ? 'cursor-not-allowed' : ''}"
      placeholder="Type your message..."
      disabled={$isSending}
      bind:value={messageInput}
      on:input={setTokenSize}
      on:keydown={(e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          handleSendMessage();
          document.querySelector(".token-count").textContent = 0;
        }
      }}
    ></textarea>
    <button
      on:click={handleSendMessage}
      disabled={$isSending}
      class="absolute text-secondary bg-primary p-2 right-4 bottom-6 rounded-full
    {$isSending ? 'cursor-not-allowed' : ''}"
    >
      {@html Icons.CornerDownLeft}
    </button>
    <p class="absolute text-tertiary p-2 right-4 top-2">
      <span class="token-count">0</span>
    </p>
  </div>
</div>

<style>
  .expandable-input textarea {
    min-height: 60px;
    max-height: 200px;
    resize: none;
  }
</style>
