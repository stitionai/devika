<script>
  import { agentState } from "../store";
</script>

<div
  class="internal-monologue bg-slate-950 gap-3 border border-indigo-700 p-3 rounded mt-4 mx-3 flex items-start "
>
  <img
    src="/assets/devika-avatar.png"
    alt="Devika's Avatar"
    class="w-[40px] h-[40px] flex-shrink-0 rounded-full border-2 border-indigo-500"
  />
  <div>
    <p class="text-xs text-gray-400">Devika's Internal Monologue</p>
    <p class="text-sm">{$agentState?.internal_monologue || "😴"}</p>
  </div>
</div>

<style>
  
</style>
