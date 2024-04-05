<script>
  import { agentState } from "$lib/store";
  import { API_BASE_URL, socket } from "$lib/api";
  
  socket.on('screenshot', function(msg) {
    const data = msg['data'];
    const img = document.querySelector('.browser-img');
    img.src = `data:image/png;base64,${data}`;
  });

</script>

<div class="flex flex-col rounded-3xl h-1/2 overflow-y-auto border-tertiary border-solid border-4">
  <div class="p-2 flex items-center border-b bg-secondary">
    <div class="flex space-x-2 ml-2 mr-4">
      <div class="w-3 h-3 bg-background rounded-full"></div>
      <div class="w-3 h-3 bg-background rounded-full"></div>
      <div class="w-3 h-3 bg-background rounded-full"></div>
    </div>
    <input
      type="text"
      id="browser-url"
      class="flex-grow bg-background rounded-lg p-1 px-2 me-2 overflow-x-auto"
      placeholder="chrome://newtab"
      value={$agentState?.browser_session.url || ""}
      
    />
  </div>
  <div id="browser-content" class="flex-grow overflow-y-auto bg-primary">
    {#if $agentState?.browser_session.screenshot}
      <img
        class="browser-img"
        alt="Browser snapshot"
        src={API_BASE_URL + "/api/get-browser-snapshot?snapshot_path=" + $agentState?.browser_session.screenshot}
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