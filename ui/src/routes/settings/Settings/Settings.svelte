<script type="ts">
  import { onMount } from "svelte";
  import { getSettings, setSettings } from "../../../lib/api";
  import Button from "./Button.svelte";
  import Input from "./Input.svelte";
  let result;
  let settingsLoading;
  onMount(async () => {
    result = await getSettings();
    console.log(result);
  });

  async function handleSubmit() {
    settingsLoading = true;
    const postResult = await setSettings(result);
    console.log(postResult);
    settingsLoading = false;
  }
</script>

<div class="px-4 py-8 max-w-[600px]">
  {#if result}
    <form on:submit|preventDefault={handleSubmit}>
      <div class="space-y-8">
        {#each Object.keys(result) as mainKey}
          <div>
            <p class="mb-4">{mainKey}</p>
            <div class="pl-4 space-y-3">
              {#each Object.keys(result[mainKey]) as key}
                <Input
                  label={key}
                  type="text"
                  bind:value={result[mainKey][key]}
                />
              {/each}
            </div>
          </div>
        {/each}
      </div>
      <div class="h-[20px]"></div>
      <Button
        type="submit"
        text="Submit"
        isActive={settingsLoading}
        activeText="Submitting..."
      ></Button>
    </form>
  {/if}
</div>
