<script>
  import { updateSettings, fetchSettings } from "$lib/api";
  import { onMount } from "svelte";

  let settings = {};
  let editMode = false;
  let original = {};

  onMount(async () => {
    settings = await fetchSettings();
    // this is for correcting order of apis shown in the settings page
    settings["API_KEYS"] = {
      "BING": settings["API_KEYS"]["BING"],
      "GOOGLE_SEARCH": settings["API_KEYS"]["GOOGLE_SEARCH"],
      "GOOGLE_SEARCH_ENGINE_ID": settings["API_KEYS"]["GOOGLE_SEARCH_ENGINE_ID"],
      "CLAUDE": settings["API_KEYS"]["CLAUDE"],
      "OPENAI": settings["API_KEYS"]["OPENAI"],
      "GEMINI": settings["API_KEYS"]["GEMINI"],
      "MISTRAL": settings["API_KEYS"]["MISTRAL"],
      "GROQ": settings["API_KEYS"]["GROQ"],
      "NETLIFY": settings["API_KEYS"]["NETLIFY"]
    };
    // make a copy of the original settings
    original = JSON.parse(JSON.stringify(settings));

  });

  const save = async () => {
    let updated = {};
    for (let key in settings) {
      if (settings[key] !== original[key]) {
        updated[key] = settings[key];
      }
    }
    await updateSettings(updated);

    editMode = !editMode;
  };

  const edit = () => {
    editMode = !editMode;
  };
</script>

<div class="p-4 h-full w-full gap-8 flex flex-col overflow-y-auto">
  <h1 class="text-3xl">Settings</h1>
  <div class="flex flex-col w-full">
    {#if settings["API_KEYS"]}
      <div class="flex gap-4 w-full">
        
        <div class="flex flex-col gap-4 w-full">
          <h2 class="text-xl">API Keys</h2>
          <div class="flex flex-col gap-4">
            {#each Object.entries(settings["API_KEYS"]) as [key, value]}
              <div class="flex gap-1 items-center">
                <p class="w-48 text-sm">{key.toLowerCase()}</p>
                <input
                  type="text"
                  bind:value={settings["API_KEYS"][key]}
                  name={key}
                  class="p-2 border-2 w-1/2 rounded-lg {editMode ? '' : 'bg-gray-100 text-gray-500'}"
                  readonly={!editMode}
                />
              </div>
            {/each}
          </div>
        </div>
        
        <div class="flex flex-col gap-8 w-full">
          
          <div class="flex flex-col gap-2">
            <h2 class="text-xl">API Endpoints</h2>
            <div class="flex flex-col gap-4">
              {#each Object.entries(settings["API_ENDPOINTS"]) as [key, value]}
                <div class="flex gap-3 items-center">
                  <p class="w-28">{key.toLowerCase()}</p>
                  <input
                    type="text"
                    bind:value={settings["API_ENDPOINTS"][key]}
                    name={key}
                    class="p-2 w-1/2 border-2 rounded-lg {editMode ? '' : 'bg-gray-100 text-gray-500'}"
                    readonly={!editMode}
                  />
                </div>
              {/each}
            </div>
            
          </div>
          <div class="flex flex-col gap-2">
            <h2 class="text-xl">Logging</h2>
            <div class="flex flex-col gap-4">
              {#each Object.entries(settings["LOGGING"]) as [key, value]}
                <div class="flex gap-3 items-center">
                  <p class="w-28">{key.toLowerCase()}</p>
                  <input
                    type="text"
                    bind:value={settings["LOGGING"][key]}
                    name={key}
                    class="p-2 border-2 rounded-lg {editMode ? '' : 'bg-gray-100 text-gray-500'}"
                    readonly={!editMode}
                    placeholder="true/false"
                  />
                </div>
              {/each}
          </div>

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

      </div>
    {/if}
  </div>
</div>
