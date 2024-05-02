<script>
  import { updateSettings, fetchSettings } from "$lib/api";
  import { onMount } from "svelte";
  import * as Tabs from "$lib/components/ui/tabs";
  import { setMode } from "mode-watcher";
  import * as Select from "$lib/components/ui/select/index.js";
  import Seperator from "../../lib/components/ui/Seperator.svelte";
    import { toast } from "svelte-sonner";

  let settings = {};
  let editMode = false;
  let original = {};

  function getSelectedTheme() {
    let theme = localStorage.getItem('mode-watcher-mode');
    if (theme === "light") {
      return { value: "light", label: "Light" };
    } else if (theme === "dark") {
      return { value: "dark", label: "Dark" };
    } else if (theme === "system") {
      return { value: "system", label: "System" };
    } else {
      return { value: "system", label: "System" };
    }
  }

  function getSelectedResize() {
    let resize = localStorage.getItem('resize');
    if (resize === "enable") {
      return { value: "enable", label: "Enable" };
    } else {
      return { value: "disable", label: "Disable" };
    }
  }

  let selectedTheme = getSelectedTheme();
  let selectedResize = getSelectedResize();

  function setResize(value) {
    localStorage.setItem('resize', value);
  }

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
      for (let subkey in settings[key]) {
        if (settings[key][subkey] !== original[key][subkey]) {
          if (!updated[key]) {
            updated[key] = {};
          }
          updated[key][subkey] = settings[key][subkey];
        }
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
  <div class="flex flex-col w-full text-sm">
    <Tabs.Root
      value="apikeys"
      class="w-full flex flex-col justify-start ms-2"
    >
      <Tabs.List class="ps-0">
        <Tabs.Trigger value="apikeys">API Keys</Tabs.Trigger>
        <Tabs.Trigger value="endpoints">API Endpoints</Tabs.Trigger>
        <Tabs.Trigger value="config">Config</Tabs.Trigger>
        <Tabs.Trigger value="appearance">Appearance</Tabs.Trigger>
      </Tabs.List>
      
      <Seperator direction="vertical"/>
      
      <Tabs.Content value="apikeys" class="mt-4">
        {#if settings["API_KEYS"]}
          <div class="flex gap-4 w-full">
            <div class="flex flex-col gap-4 w-full">
              <div class="flex flex-col gap-4">
                {#each Object.entries(settings["API_KEYS"]) as [key, value]}
                  <div class="flex gap-1 items-center">
                    <p class="w-48">{key.toLowerCase()}</p>
                    <input
                      type={editMode ? "text" : "password"}
                      value={settings["API_KEYS"][key]}
                      on:input={(e) => settings["API_KEYS"][key] = e.target.value}
                      name={key}
                      class="p-2 border-2 w-1/2 rounded-lg {editMode
                        ? ''
                        : ' text-gray-500'}"
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
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-secondary"
              on:click={edit}
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
          {:else}
            <button
              id="btn-save"
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-secondary"
              on:click={save}
            >
              <i class="fas fa-save"></i>
              Save
            </button>
          {/if}
        </div>
      </Tabs.Content>
      <Tabs.Content value="endpoints" class="mt-4">
        {#if settings["API_ENDPOINTS"]}
          <div class="flex gap-4 w-full">
              <div class="flex flex-col w-full gap-4">
                {#each Object.entries(settings["API_ENDPOINTS"]) as [key, value]}
                  <div class="flex gap-3 items-center">
                    <p class="w-28">{key.toLowerCase()}</p>
                    <input
                      type="text"
                      value={settings["API_ENDPOINTS"][key]}
                      on:input={(e) => settings["API_ENDPOINTS"][key] = e.target.value}
                      name={key}
                      class="p-2 border-2 w-1/2 rounded-lg {editMode
                        ? ''
                        : 'text-gray-500'}"
                      readonly={!editMode}
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
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-secondary"
              on:click={edit}
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
          {:else}
            <button
              id="btn-save"
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-secondary"
              on:click={save}
            >
              <i class="fas fa-save"></i>
              Save
            </button>
          {/if}
        </div>
      </Tabs.Content>
      <Tabs.Content value="config" class="mt-4">
        {#if settings["TIMEOUT"]}
          <div class="flex flex-col gap-8 w-full">
          
            <div class="flex flex-col gap-4">
              <div class="text-xl font-semibold">
                Timouts
              </div>
              <div class="flex flex-col w-64 gap-4">
                {#each Object.entries(settings["TIMEOUT"]) as [key, value]}
                    <div class="flex gap-3 items-center">
                      <p class="w-28">{key.toLowerCase()}</p>
                      <input
                        type="number"
                        bind:value={settings["TIMEOUT"][key]}
                        name={key}
                        placeholder="in seconds"
                        class="p-2 border-2 w-1/2 rounded-lg {editMode
                          ? ''
                          : 'text-gray-500'}"
                        readonly={!editMode}
                      />
                    </div>
                {/each}
              </div>
            </div>
          
            <div class="flex flex-col gap-4">
              <div class="text-xl font-semibold">
                Logging
              </div>
              <div class="flex flex-col w-64 gap-4">
                {#each Object.entries(settings["LOGGING"]) as [key, value]}
                <div class="flex gap-10 items-center">
                  <p class="w-28">{key.toLowerCase()}</p>
                  <Select.Root onSelectedChange={(v)=>{settings["LOGGING"][key] = v.value}}
                    disabled={!editMode}>
                    <Select.Trigger class="w-[180px]" >
                      <Select.Value placeholder={settings["LOGGING"][key]} />
                    </Select.Trigger>
                    <Select.Content>
                      <Select.Group>
                        <Select.Item value={"true"} label={"True"}>true</Select.Item>
                        <Select.Item value={"false"} label={"False"}>false</Select.Item>
                      </Select.Group>
                    </Select.Content>
                    <Select.Input name={key} />
                  </Select.Root>
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
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-secondary"
              on:click={edit}
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
          {:else}
            <button
              id="btn-save"
              class="p-2 border-2 rounded-lg flex gap-3 items-center hover:bg-secondary"
              on:click={save}
            >
              <i class="fas fa-save"></i>
              Save
            </button>
          {/if}
        </div>
      </Tabs.Content>
      <Tabs.Content value="appearance" class="mt-4 w-fit">
        <div class="flex w-full justify-between items-center my-2 gap-8">
          <div>
            Select a theme
          </div>
          <div>
            <Select.Root onSelectedChange={(v)=>{setMode(v.value)}}>
              <Select.Trigger class="w-[180px]">
                <Select.Value  placeholder={selectedTheme.label} />
              </Select.Trigger>
              <Select.Content>
                <Select.Group>
                  <Select.Item value={"light"} label={"Light"}>Light</Select.Item>
                  <Select.Item value={"dark"} label={"Dark"}>Dark</Select.Item>
                  <Select.Item value={"system"} label={"System"}>System</Select.Item>
                </Select.Group>
              </Select.Content>
              <Select.Input name="favoriteFruit" />
            </Select.Root>
          </div>
        </div>
        <div class="flex w-full justify-between items-center  my-2 gap-8">
          <div>
            Enable tab resize
          </div>
          <div>
            <Select.Root onSelectedChange={(v)=>{setResize(v.value)}}>
              <Select.Trigger class="w-[180px]">
                <Select.Value placeholder={selectedResize.label}/>
              </Select.Trigger>
              <Select.Content>
                <Select.Group>
                  <Select.Item value={"enable"} label={"Enable"}>Enable</Select.Item>
                  <Select.Item value={"disable"} label={"Disable"}>Disable</Select.Item>
                </Select.Group>
              </Select.Content>
              <Select.Input name="favoriteFruit" />
            </Select.Root>
          </div>
        </div>
        <div class="flex w-full justify-between items-center  my-2 gap-8">
          <div>
            Reset layout
          </div>
          <div>
            <button
              class="min-w-[180px] p-2 border-2 rounded-lg flex gap-3 items-center justify-between hover:bg-secondary"
              on:click={() => {
                toast.warning("Resetting layout");
                localStorage.removeItem('paneforge:default');
              }}
            >
              Reset
              <i class="fas fa-undo"></i>
            </button>
          </div>
        </div>
      </Tabs.Content>
    </Tabs.Root>
  </div>
</div>
