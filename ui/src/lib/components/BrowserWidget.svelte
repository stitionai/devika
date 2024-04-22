<script>
  import { agentState } from "$lib/store";
  import { API_BASE_URL, socket } from "$lib/api";
  
  socket.on('screenshot', function(msg) {
    const data = msg['data'];
    const img = document.querySelector('.browser-img');
    img.src = `data:image/png;base64,${data}`;
  });

</script>

<div class="flex flex-col border-[4px] rounded-3xl h-1/2 overflow-y-auto bg-black/40 border-window-outline">
  <div class="p-2 flex items-center border-b border-border bg-browser-window-background h-12">
    <div class="flex space-x-2 ml-2 mr-4 text-browser-window-dots">
      <div class="red-dot "></div>
      <div class="yellow-dot"></div>
      <div class="green-dot"></div>
    </div>
    <input
      type="text"
      id="browser-url"
      class="flex-grow border-2 rounded-lg p-2 overflow-x-auto"
      placeholder="chrome://newtab"
      value={$agentState?.browser_session.url || ""}
      
    />
  </div>
  <div id="browser-content" class="flex-grow overflow-y-auto">
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
  .red-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: #FF605C;
  }
  .yellow-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color:  #FFBD44;
  }
  .green-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: #00CA4E;
  }
</style>