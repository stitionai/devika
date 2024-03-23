<script>
  import { agentState } from "$lib/store";
  import { API_BASE_URL } from "$lib/api";
</script>

<div class="flex flex-col bg-slate-950 border border-indigo-700 rounded flex-1 overflow-hidden">
  <div class="p-2 flex items-center border-b border-gray-700">
    <div class="flex space-x-2 ml-2 mr-4">
      <div class="w-3 h-3 bg-red-500 rounded-full"></div>
      <div class="w-3 h-3 bg-yellow-400 rounded-full"></div>
      <div class="w-3 h-3 bg-green-500 rounded-full"></div>
    </div>
    <input
      type="text"
      id="browser-url"
      class="flex-grow bg-slate-900 p-2 rounded"
      placeholder="chrome://newtab"
      value={$agentState?.browser_session.url || ""}
      readonly
    />
  </div>
  <div id="browser-content" class="flex-grow overflow-auto">
    {#if $agentState?.browser_session.screenshot}
      <img
        class="browser-img"
        src={API_BASE_URL + "/api/get-browser-snapshot?snapshot_path=" + $agentState?.browser_session.screenshot}
        alt="Browser snapshot"
      />
    {:else}
      <div class="text-white text-center mt-5"><strong>💡 TIP:</strong> You can include a Git URL in your prompt to clone a repo!</div>
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
    max-width: 100%;
  }
</style>