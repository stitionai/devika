<script>
  /**
   * @type {string} The text shown when no option is selected
   */
  export let label;

  /** 
   * @type {string | null | undefined} The ID of the selected entry or null
   */
  export let selection = undefined;

  /** 
   * @type {Record<string, string>} An object of options with the key as the ID and the value as the label
  */
  export let options;

  /** @type {HTMLElement | null} **/
  let dropdown = null;

  let open = false;

  /**
   * @param {string} id ID of the selected element
   */
  function selectElement(id) { 
    selection = id;
    open = false;
  }

  /**
   * Svelte Action function to handle clicks outside of the given element
   * @param {HTMLElement} element The dropdown element
   * @param {() => void} callbackFunction The function to call when a click outside is detected
   */
  function onClickOutside(element, callbackFunction) {
		function onClick(event) {
			if (!element.contains(event.target)) {
				callbackFunction();
			}
		}
		
    let registered = false;

    setTimeout(() => {
      document.body.addEventListener('click', onClick);
      registered = true;
    }, 100)
		
		return {
			update(newCallbackFunction) {
				callbackFunction = newCallbackFunction;
			},
			destroy() {
				if (registered) {
          document.body.removeEventListener('click', onClick);
          registered = false;
        }
			}
		}
	}

  // This needs to be a function so it can passed as slot prop
  function closeDropdown() {
    open = false;
  }
</script>

<div class="dropdown-menu relative inline-block">
  <button
    type="button"
    class="inline-flex justify-center w-full gap-x-1.5 rounded-md bg-slate-900 px-3 py-2 text-sm font-semibold text-white shadow-sm ring-1 ring-inset ring-indigo-700 hover:bg-slate-800"
    aria-expanded="true"
    aria-haspopup="true"
    on:click={() => open = !open}
  >
    <span>
      {selection ? options[selection] : label}
    </span>

    <svg
      class="-mr-1 h-5 w-5 text-gray-400"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fill-rule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
        clip-rule="evenodd"
      />
    </svg>
  </button>
  {#if open}
    <div
      bind:this={dropdown}
      class="absolute left-0 z-10 w-fit origin-top-left rounded-md bg-slate-800 shadow-lg ring-1 ring-indigo-700 ring-opacity-5 focus:outline-none"
      role="menu"
      tabindex="-1"
      use:onClickOutside={() => { open = false; }}
    >
      <div role="none">
        <slot name="prefix-entries" {closeDropdown} />

        {#each Object.entries(options) as [id, label]}
          <button
            class="text-white block px-4 py-2 text-sm hover:bg-slate-700 w-full text-left overflow-clip"
            on:click|preventDefault={() => selectElement(id)}
          >
            {label}
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>
