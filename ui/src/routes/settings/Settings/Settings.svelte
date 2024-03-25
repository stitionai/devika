<script lang="ts">
  import { onMount } from "svelte";
  import { getSettings, setSettings } from "../../../lib/api";
  import Button from "./Button.svelte";
  import Input from "./Input.svelte";
  let result: any;
  let settingsLoading: boolean;
  onMount(async () => {
    result = await getSettings();
    // console.log(result);
  });

  async function handleSubmit() {
    settingsLoading = true;
    const postResult = await setSettings(result);
    // console.log(postResult);
    settingsLoading = false;
    formChanged = false;
  }
  function checkNonEmptyRecursive(obj) {
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        if (typeof obj[key] === "object") {
          if (!checkNonEmptyRecursive(obj[key])) {
            return false;
          }
        } else if (!obj[key]) {
          return false;
        }
      }
    }
    return true;
  }
  $: formValid = checkNonEmptyRecursive(result);
  let formChanged = false;
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
                  on:input={() => {
                    formChanged = true;
                  }}
                  error={!result[mainKey][key] ? "field can't be empty" : ""}
                />
              {/each}
            </div>
          </div>
        {/each}
      </div>
      <div class="h-[20px]"></div>
      {#if !formValid}
        <p class="text-[#f55]">All fields must be filled</p>
        <div class="h-[10px]"></div>
      {/if}

      {#if formChanged}
        <Button
          type="submit"
          text="Save"
          isActive={settingsLoading}
          activeText="Saving..."
          disabled={!formValid}
        ></Button>
      {/if}
    </form>
  {/if}
</div>
