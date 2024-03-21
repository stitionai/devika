<script>
  import { agentState } from "../store";
  import { API_BASE_URL } from "../api";
</script>

<div class="flex flex-col bg-black border border-gray-800 rounded-lg flex-1 overflow-hidden">
  <div class="p-2 flex items-center border-b border-gray-700">
    <div class="flex space-x-2 ml-2 mr-4">
      <div class="w-3 h-3 bg-red-500 rounded-full"></div>
      <div class="w-3 h-3 bg-yellow-400 rounded-full"></div>
      <div class="w-3 h-3 bg-green-500 rounded-full"></div>
    </div>
    <input
      type="text"
      id="browser-url"
      class="flex-grow text-sm bg-gray-900 px-4 py-2 rounded-full pointer-events-none"
      placeholder="chrome://newtab"
      value={$agentState?.browser_session.url || ""}
      readonly
    />
  </div>
  <div id="browser-content" class="flex-grow overflow-auto">
    {#if $agentState?.browser_session.screenshot}
      <img
        class=" block object-contain w-full"
        src={API_BASE_URL + "/api/get-browser-snapshot?snapshot_path=" + $agentState?.browser_session.screenshot}
        alt="Browser snapshot"
      />
    {:else}
      <div class="text-white text-center mt-5"><strong>💡 TIP:</strong> You can include a Git URL in your prompt to clone a repo!</div>
    {/if}
  </div>
</div>

<style>

</style>