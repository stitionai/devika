<script>
  import { messages } from "$lib/store";
  import { afterUpdate } from "svelte";

  let messageContainer;
  let previousMessageCount = 0;
  
  afterUpdate(() => {
  if ($messages && $messages.length > 0) {
    messageContainer.scrollTo({
      top: messageContainer.scrollHeight,
      behavior: "smooth"
    });
  }
});

</script>

<div
  id="message-container"
  class="flex flex-col flex-1 gap-2 overflow-y-auto rounded-lg"
  bind:this={messageContainer}
>
  {#if $messages !== null}
  <div class="flex flex-col divide-y-2">
    {#each $messages as message}
      <div class="flex items-start gap-2 px-2 py-4">
        {#if message.from_devika}
          <img
            src="/assets/devika-avatar.png"
            alt="Devika's Avatar"
            class="flex-shrink-0 rounded-full avatar"
            style="width: 28px; height: 28px;"
          />
        {:else}
          <img
            src="/assets/user-avatar.svg"
            alt="User's Avatar"
            class="flex-shrink-0 rounded-full avatar"
            style="width: 28px; height: 28px;"
          />
        {/if}
        <div class="flex flex-col w-full text-sm">
          <p class="text-xs text-gray-400">
            {message.from_devika ? "Devika" : "You"}
            <span class="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
          </p>
          {#if message.from_devika && message.message.startsWith("{")}
            <div class="flex flex-col w-full gap-5" contenteditable="false">
              {@html `<strong>Here's my step-by-step plan:</strong>`}
              <div class="flex flex-col gap-3">
              {#if JSON.parse(message.message)}
                {#each Object.entries(JSON.parse(message.message)) as [step, description]}
                  <div class="flex items-center gap-2">
                    <input type="checkbox" id="step-{step}" disabled />
                    <label for="step-{step}" class="cursor-auto"><strong>Step {step}</strong>: {description}</label>
                  </div>
                {/each}
              {/if}
              </div>
            </div>
          {:else if /https?:\/\/[^\s]+/.test(message.message)}
            <div class="w-full cursor-auto" contenteditable="false">
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
  #message-container {
    scrollbar-width: none;
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
