<script>
  import { agentState } from "$lib/store";
  import { API_BASE_URL } from "$lib/api";
</script>

<div class="flex flex-col border-[4px] rounded-3xl h-1/2 overflow-y-auto bg-browser-window-background border-window-outline">
  <div class="p-2 flex items-center border-b border-border bg-browser-window-ribbon h-12">
    <div class="flex space-x-2 ml-2 mr-4">
      <div class="w-3 h-3 bg-browser-window-dots rounded-full"></div>
      <div class="w-3 h-3 bg-browser-window-dots rounded-full"></div>
      <div class="w-3 h-3 bg-browser-window-dots rounded-full"></div>
    </div>
    <input
      type="text"
      id="browser-url"
      class="flex-grow h-7 rounded-lg p-2 overflow-x-auto bg-browser-window-search text-browser-window-foreground"
      placeholder="chrome://newtab"
      value={$agentState?.browser_session.url || ""}
    />
  </div>
  <div id="browser-content" class="flex-grow overflow-y-auto">
    {#if $agentState?.browser_session.screenshot}
      <img
        class="browser-img"
        src={API_BASE_URL + "/api/get-browser-snapshot?snapshot_path=" + $agentState?.browser_session.screenshot}
        alt="Browser snapshot"
      />
    {:else}
      <div class="text-gray-400 text-center mt-5"><strong>💡 TIP:</strong> You can include a Git URL in your prompt to clone a repo!</div>
    {/if}
  </div>
</div>

<style>
  #browser-url {
    pointer-events: none
  }

  .browser-img {
    display: block;
    object-fit: contain;
  }
</style>