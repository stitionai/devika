<script>
  import MessageContainer from "$lib/components/MessageContainer.svelte";
  import InternalMonologue from "$lib/components/InternalMonologue.svelte";
  import MessageInput from "$lib/components/MessageInput.svelte";
  import BrowserWidget from "$lib/components/BrowserWidget.svelte";
  import TerminalWidget from "$lib/components/TerminalWidget.svelte";
  import { onMount } from "svelte";
  import { fetchMessages } from "$lib/api";
  import {page} from "$app/stores";
  onMount(() => {
    console.log(page.params.slug)
    localStorage.setItem("selectedProject", page.params.slug);
    const load = async () => {
      fetchMessages();
    };
    load();
  });

</script>

<div class="flex flex-col gap-2 w-1/2">
  <MessageContainer />
  <InternalMonologue />
  <MessageInput />
</div>

<div class="flex flex-col gap-4 w-1/2">
  <BrowserWidget />
  <TerminalWidget />
</div>
