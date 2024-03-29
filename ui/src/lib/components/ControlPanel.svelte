<script>
  import { onMount } from 'svelte';
  import { selectedProject, selectedModel, projectList, modelList, internet } from '$lib/store';
  import { createProject, fetchProjectList, getTokenUsage } from "$lib/api";
  import Dropdown from "./ui/Dropdown.svelte";

  let tokenUsage = 0;

  async function updateTokenUsage() {
    tokenUsage = await getTokenUsage();
  }

  async function createNewProject() {
    const projectName = prompt('Enter the project name:');
    if (projectName) {
      await createProject(projectName);
      await fetchProjectList();

      selectedProject.set(projectName);
    }
  }

  onMount(() => {
    setInterval(updateTokenUsage, 1000);
  });
</script>

<div class="control-panel bg-slate-900 border border-indigo-700 rounded">
  <Dropdown options={Object.fromEntries($projectList.map((x) => [x, x]))} label="Select Project" bind:selection={$selectedProject}>
    <div slot="prefix-entries" let:closeDropdown={close}>
      <button
        class="text-white block px-4 py-2 text-sm hover:bg-slate-700 w-full text-left overflow-clip"
        on:click|preventDefault={() => {
          createNewProject();
          close();
        }}
      >
        + Create New Project
      </button>
    </div>
  </Dropdown>
  <div
    class="right-controls"
    style="display: flex; align-items: center; gap: 20px"
  >
    <div class="flex items-center space-x-2">
      <span>Internet:</span>
      <div id="internet-status" class="internet-status" class:online={$internet} class:offline={!$internet} />
      <span id="internet-status-text" />
    </div>
    <div class="flex items-center space-x-2">
      <span>Token Usage:</span>
      <span class="token-count-animation">{tokenUsage}</span>
    </div>
    <div class="relative inline-block text-left">
      <Dropdown
        options={Object.fromEntries($modelList.map(([name, id]) => [id, `${name} (${id})`]))}
        label="Select Model"
        bind:selection={$selectedModel}
      />
    </div>
  </div>
</div>

<style>
  .internet-status {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }

  .online {
    background-color: #22c55e;
  }

  .offline {
    background-color: #ef4444;
  }

  @keyframes roll {
    0% {
      transform: translateY(-5%);
    }
    100% {
      transform: translateY(0);
    }
  }

  .token-count-animation {
    display: inline-block;
    animation: roll 0.5s ease-in-out;
  }

  .control-panel {
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .control-panel > *:not(:first-child) {
    margin-left: 20px;
  }

  .right-controls > *:not(:last-child) {
    border-right: 1px solid #4b5563;
    padding-right: 20px;
  }
</style>
