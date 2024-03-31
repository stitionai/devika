<script>
  import { messages } from "$lib/store";
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
  class="flex flex-col flex-1 gap-2 overflow-y-auto border-2 rounded-lg px-2 py-4"
  bind:this={messageContainer}
>
  {#if $messages !== null}
  <div class="flex flex-col px-2 divide-y-2">
    {#each $messages as message}
      <div class="flex items-start px-2 py-4 gap-2">
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
        <div class="flex flex-col w-full">
          <p class="text-xs text-gray-400">
            {message.from_devika ? "Devika" : "You"}
            <span class="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
          </p>
          {#if message.from_devika && message.message.startsWith("{")}
            <div class="flex flex-col gap-5 w-full" contenteditable="false">
              {@html `<strong>Here's my step-by-step plan:</strong>`}
              <div class="flex flex-col gap-3">
              {#if JSON.parse(message.message)}
                {#each Object.entries(JSON.parse(message.message)) as [step, description]}
                  <div class="flex gap-2 items-center">
                    <input type="checkbox" id="step-{step}" disabled />
                    <label for="step-{step}"><strong>Step {step}</strong>: {description}</label>
                  </div>
                {/each}
              {/if}
              </div>
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
  </div>
  {/if}
</div>

<style>
  .timestamp {
    margin-left: 8px;
    font-size: smaller;
    color: #aaa;
  }

  input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    -ms-appearance: none;
    -o-appearance: none;
    width: 12px;
    height: 12px;
    border: 2px solid black;
    border-radius: 4px;
  }
</style>
