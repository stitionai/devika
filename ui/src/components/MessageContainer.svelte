<script>
  import { messages } from "../store";
  import { onMount, afterUpdate } from "svelte";

  let messageContainer;
  let previousMessageCount = 0;

  afterUpdate(() => {
    if ($messages && $messages.length > previousMessageCount) {
      messageContainer.scrollTop = messageContainer.scrollHeight;
      previousMessageCount = $messages.length;
    }
  });
</script>

<div
  id="message-container"
  class="flex flex-col flex-1 gap-2 overflow-y-auto border-2 rounded-lg p-4"
  bind:this={messageContainer}
>
  {#if $messages !== null}
    {#each $messages as message}
      <div class="flex items-center justify-center gap-2 px-2 py-4 border-b-2">
        {#if message.from_devika}
          <img
            src="/assets/devika-avatar.png"
            alt="Devika's Avatar"
            class="avatar rounded-full flex-shrink-0"
            style="width: 40px; height: 40px;"
          />
        {:else}
          <img
            src="/assets/user-avatar.png"
            alt="User's Avatar"
            class="avatar rounded-full flex-shrink-0"
            style="width: 40px; height: 40px;"
          />
        {/if}
        <div class="flex flex-col w-full gap-1">
          <p class="text-xs text-gray-400">
            {message.from_devika ? "Devika" : "You"}
            <span class="timestamp"
              >{new Date(message.timestamp).toLocaleTimeString()}</span
            >
          </p>
          {#if message.from_devika && message.message.startsWith("{")}
            <div class="w-full" contenteditable="false">
              {@html `<strong>Here's my step-by-step plan:</strong>`}
              <br /><br />
              {#if JSON.parse(message.message)}
                {#each Object.entries(JSON.parse(message.message)) as [step, description]}
                  <input type="checkbox" id="step-{step}" disabled />
                  <label for="step-{step}"
                    ><strong>Step {step}</strong>: {description}</label
                  >
                  <br /><br />
                {/each}
              {/if}
            </div>
          {:else if /https?:\/\/[^\s]+/.test(message.message)}
            <div class="w-full" contenteditable="false">
              {@html message.message.replace(
                /(https?:\/\/[^\s]+)/g,
                '<u><a href="$1" target="_blank" style="font-weight: bold;">$1</a></u>'
              )}
            </div>
          {:else}
            <div
              class="w-full"
              contenteditable="false"
              bind:innerHTML={message.message}
            ></div>
          {/if}
        </div>
      </div>
    {/each}
  {/if}
</div>

<style>
  .sender-name {
    margin-bottom: 4px;
    display: flex;
    align-items: baseline;
  }

  .timestamp {
    margin-left: 8px;
    font-size: smaller;
    color: #aaa;
  }

  #message-container {
    overflow-y: auto;
  }
  /* scrollbar hidden for all browsers*/
  #message-container::-webkit-scrollbar {
    display: none;
  }
  #message-container {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    -ms-appearance: none;
    -o-appearance: none;
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #4337c9;
    border-radius: 4px;
    margin-right: 8px;
    position: relative;
    top: 3px;
  }
</style>
