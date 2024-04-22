<script>
  import { updateSettings, fetchSettings } from "$lib/api";
  import { onMount } from "svelte";
  import * as Tabs from "$lib/components/ui/tabs";
    import Separator from "$lib/components/ui/separator/separator.svelte";
    import Button from "$lib/components/ui/button/button.svelte";
    import { toggleMode } from "mode-watcher";

  let settings = {};
  let editMode = false;
  let original = {};

  onMount(async () => {
    settings = await fetchSettings();
    // this is for correcting order of apis shown in the settings page
    settings["API_KEYS_FOR_MODELS"] = {
      "BING": settings["API_KEYS_FOR_MODELS"]["BING"],
      "GOOGLE_SEARCH": settings["API_KEYS_FOR_MODELS"]["GOOGLE_SEARCH"],
      "GOOGLE_SEARCH_ENGINE_ID": settings["API_KEYS_FOR_MODELS"]["GOOGLE_SEARCH_ENGINE_ID"],
      "CLAUDE": settings["API_KEYS_FOR_MODELS"]["CLAUDE"],
      "OPENAI": settings["API_KEYS_FOR_MODELS"]["OPENAI"],
      "GEMINI": settings["API_KEYS_FOR_MODELS"]["GEMINI"],
      "MISTRAL": settings["API_KEYS_FOR_MODELS"]["MISTRAL"],
      "GROQ": settings["API_KEYS_FOR_MODELS"]["GROQ"],
      "NETLIFY": settings["API_KEYS_FOR_MODELS"]["NETLIFY"]
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
    <Tabs.Root value="apikeys" class="w-[400px] flex flex-col justify-start ms-2">
      <Tabs.List class="ps-0">
        <Tabs.Trigger value="apikeys">API Keys</Tabs.Trigger>
        <Tabs.Trigger value="endpoints">API Endpoints</Tabs.Trigger>
        <Tabs.Trigger value="logging">Logs Settings</Tabs.Trigger>
        <Tabs.Trigger value="theme">Theme</Tabs.Trigger>
      </Tabs.List>
      <Separator />
      <Tabs.Content value="apikeys">
        {#if settings["API_KEYS_FOR_MODELS"]}
          <div class="flex gap-4 w-full">
            <div class="flex flex-col gap-4 w-full">
              <!-- <h2 class="text-xl">API Keys</h2> -->
              <div class="flex flex-col gap-4">
                {#each Object.entries(settings["API_KEYS_FOR_MODELS"]) as [key, value]}
                  <div class="flex gap-1 items-center">
                    <p class="w-48 text-sm">{key.toLowerCase()}</p>
                    <input
                      type="text"
                      bind:value={settings["API_KEYS_FOR_MODELS"][key]}
                      name={key}
                      class="p-2 border-2 w-1/2 rounded-lg {editMode
                        ? ''
                        : 'bg-gray-100 text-gray-500'}"
                      readonly={!editMode}
                    />
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
        <div class="flex gap-4 mt-5">
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
      </Tabs.Content>
      <Tabs.Content value="endpoints">
        {#if settings["API_KEYS_FOR_MODELS"]}
          <div class="flex gap-4 w-full">
            <div class="flex flex-col gap-2">
              <!-- <h2 class="text-xl">API Endpoints</h2> -->
              <div class="flex flex-col gap-4">
                {#each Object.entries(settings["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]) as [key, value]}
                  <div class="flex gap-3 items-center">
                    <p class="w-28">{key.toLowerCase()}</p>
                    <input
                      type="text"
                      bind:value={settings["API_ENDPOINTS_FOR_ONLINE_SEARCHES"][key]}
                      name={key}
                      class="p-2 w-1/2 border-2 rounded-lg {editMode
                        ? ''
                        : 'bg-gray-100 text-gray-500'}"
                      readonly={!editMode}
                    />
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
        <div class="flex gap-4 mt-5">
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
      </Tabs.Content>
      <Tabs.Content value="logging">
        {#if settings["API_KEYS_FOR_MODELS"]}
          <div class="flex flex-col gap-2">
            <!-- <h2 class="text-xl">Logging</h2> -->
            <div class="flex flex-col gap-4">
              {#each Object.entries(settings["LOGGING_DUMPS"]) as [key, value]}
                <div class="flex gap-3 items-center">
                  <p class="w-28">{key.toLowerCase()}</p>
                  <input
                    type="text"
                    bind:value={settings["LOGGING_DUMPS"][key]}
                    name={key}
                    class="p-2 border-2 rounded-lg {editMode
                      ? ''
                      : 'bg-gray-100 text-gray-500'}"
                    readonly={!editMode}
                    placeholder="true/false"
                  />
                </div>
              {/each}
            </div>
          </div>
        {/if}
        <div class="flex gap-4 mt-5">
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
      </Tabs.Content>
      <Tabs.Content value="theme">
        <Button on:click={toggleMode} variant="outline">
          toggle theme
        </Button>
      </Tabs.Content>
    </Tabs.Root>
  </div>
</div>