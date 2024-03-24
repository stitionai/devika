<script type="ts">
  import { onMount } from "svelte";
  import { getSettings, setSettings } from "../../../lib/api";
  import Button from "./Button.svelte";
  import Input from "./Input.svelte";
  let result;
  onMount(async () => {
    result = await getSettings();
    console.log(result);
  });

  async function handleSubmit() {
    const postResult = await setSettings(result);
    console.log(postResult);
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <p>API_KEYS</p>
  {#if result}
    <div class="pl-4">
      <Input
        label="CLAUDE"
        type="text"
        bind:value={result["API_KEYS"]["CLAUDE"]}
      />
    </div>
  {/if}

  <Button type="submit" text="Submit"></Button>
</form>
