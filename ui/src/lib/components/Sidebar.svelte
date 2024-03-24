<script>
  let navItems = [
    { icon: "fa-home", tooltip: "Home" },
    { icon: "fa-cog", tooltip: "Settings" },
    { icon: "fa-history", tooltip: "Logs" },
  ];
</script>

<div class="flex flex-col p-4 gap-4 items-center bg-gray-100">
  {#each navItems as item (item.tooltip)}
    <div class="p-4 rounded nav-button relative">
      <button
        class="hover:text-gray-500 flex justify-center w-full hover:transition-colors"
      >
        <i class={`fas ${item.icon} fa-lg`}></i>
      </button>
      <span class="tooltip">{item.tooltip}</span>
    </div>
  {/each}
</div>

<style>
  .tooltip {
    font-size: 12px;
    background-color: black;
    color: white;
    text-align: center;
    border-radius: 100px;
    padding: 5px 10px;
    position: absolute;
    z-index: 1;
    opacity: 0;
    top: 50%;
    left: 90%;
    transform: translateY(-50%);
    transition: opacity 0.3s;
  }

  .nav-button:hover .tooltip {
    visibility: visible;
    opacity: 1;
  }
</style>
