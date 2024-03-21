<script>
  import { agentState } from "../store";
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
    <p class="text-xs text-gray-400">Devika's Internal Monologue</p>
    <p class="text-xs">{$agentState?.internal_monologue || "😴"}</p>
  </div>
</div>

<style>
  .avatar {
    width: 40px;
    height: 40px;
  }
</style>
