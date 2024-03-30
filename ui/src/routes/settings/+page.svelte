<script>
  import { updateSettings, fetchSettings } from "$lib/api";
  import { onMount } from "svelte";

  let settings = {};
  let editMode = false;

  onMount(async () => {
    settings = await fetchSettings();
  });

  const save = async () => {
    await updateSettings({"API_KEYS": settings["API_KEYS"]});
    editMode = !editMode;
  };

  const edit = () => {
    editMode = !editMode;
  };
</script>

<div class="p-4 h-full w-full gap-8 flex flex-col">
  <h1 class="text-3xl">Settings</h1>
  <div class="flex flex-col w-full">
    {#if settings["API_KEYS"]}
      <div class="flex flex-col gap-4">
        <h2 class="text-xl">API Keys</h2>
        <div class="flex flex-col gap-4">
          {#each Object.entries(settings["API_KEYS"]) as [key, value]}
            <div class="flex gap-3 items-center">
              <p class="w-20">{key}</p>
              <input
                type="text"
                bind:value={settings["API_KEYS"][key]}
                name={key}
                class="w-1/3 p-2 border-2 rounded-lg {editMode ? '' : 'bg-gray-100 text-gray-500'}"
                readonly={!editMode}
              />
            </div>
          {/each}
        </div>
        <!-- edit and save button -->
        <div class="flex gap-4">
          {#if !editMode}
            <button
              id="btn-edit"
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-gray-200"
              on:click={edit}
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
          {:else}
            <button
              id="btn-save"
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-gray-200"
              on:click={save}
            >
              <i class="fas fa-save"></i>
              Save
            </button>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>
