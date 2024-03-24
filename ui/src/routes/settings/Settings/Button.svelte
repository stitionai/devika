<script lang="ts">
  export let isActive: boolean = undefined;
  export let onClick: () => void = undefined;
  export let activeText: string = undefined;
  export let text: string;
  export let type: "button" | "submit" | "reset" = undefined;
</script>

<button
  class={`px-4 py-2 rounded w-full mt-2 ${isActive ? "bg-slate-800" : "bg-indigo-700"}`}
  on:click={onClick}
  disabled={isActive}
  {type}
>
  {@html isActive ? activeText : text}
</button>
