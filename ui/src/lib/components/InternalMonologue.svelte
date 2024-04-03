<script>
  import { agentState } from "$lib/store";  

</script>

<div
  class="internal-monologue  border-2 flex items-center justify-center gap-2 px-2 py-4 rounded-lg"
>
  <img
    src="/assets/devika-avatar.png"
    alt="Devika's Avatar"
    class="avatar rounded-full flex-shrink-0"
  />
  <div class="flex flex-col w-full gap-1">
    <p class="text-xs text-gray-400">Devika's Internal Monologue | Agent status:
     {#if $agentState !== null}
      {#if $agentState.agent_is_active}
        <span class="text-green-500">Active</span>
      {:else}
        <span class="text-orange-600">Inactive</span>
      {/if}
      {:else}
      Deactive
    {/if}
    </p>
    <p class="text-xs">{$agentState?.internal_monologue || "😴"}</p>
  </div>
</div>

<style>
  .avatar {
    width: 40px;
    height: 40px;
  }
</style>