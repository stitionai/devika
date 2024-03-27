<script>
  import { onMount } from 'svelte';
  import { selectedProject, selectedModel, projectList, modelList, internet } from '$lib/store';
  import { createProject, fetchProjectList, getTokenUsage } from '$lib/api';

  let tokenUsage = 0;

  async function updateTokenUsage() {
    tokenUsage = await getTokenUsage();
  }

  function selectProject(project) {
    $selectedProject = project;
  }

  function selectModel(model) {
    $selectedModel = `${model[0]} (${model[1]})`;
  }

  async function createNewProject() {
    const projectName = prompt('Enter the project name:');
    if (projectName) {
      await createProject(projectName);
      await fetchProjectList();
      selectProject(projectName);
    }
  }

  function closeDropdowns(event) {
    const projectDropdown = document.getElementById('project-dropdown');
    const modelDropdown = document.getElementById('model-dropdown');
    const projectButton = document.getElementById('project-button');
    const modelButton = document.getElementById('model-button');

    if (!projectDropdown.contains(event.target) && !projectButton.contains(event.target)) {
      projectDropdown.classList.add('hidden');
    }

    if (!modelDropdown.contains(event.target) && !modelButton.contains(event.target)) {
      modelDropdown.classList.add('hidden');
    }
  }

  onMount(() => {
    setInterval(updateTokenUsage, 1000);

    document.getElementById('project-button').addEventListener('click', function () {
      const dropdown = document.getElementById('project-dropdown');
      dropdown.classList.toggle('hidden');
    });

    document.getElementById('model-button').addEventListener('click', function () {
      const dropdown = document.getElementById('model-dropdown');
      dropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', closeDropdowns);

    return () => {
      document.removeEventListener('click', closeDropdowns);
    };
  });
</script>

<div class="control-panel bg-slate-900 border border-indigo-700 rounded">
  <div class="dropdown-menu relative inline-block">
    <button
      type="button"
      class="inline-flex justify-center w-full gap-x-1.5 rounded-md bg-slate-900 px-3 py-2 text-sm font-semibold text-white shadow-sm ring-1 ring-inset ring-indigo-700 hover:bg-slate-800"
      id="project-button"
      aria-expanded="true"
      aria-haspopup="true"
    >
      <span id="selected-project">{$selectedProject}</span>
      <svg class="-mr-1 h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path
          fill-rule="evenodd"
          d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
    <div
      id="project-dropdown"
      class="absolute left-0 z-10 mt-2 w-full origin-top-left rounded-md bg-slate-800 shadow-lg ring-1 ring-indigo-700 ring-opacity-5 focus:outline-none hidden"
      role="menu"
      aria-orientation="vertical"
      aria-labelledby="project-button"
      tabindex="-1"
    >
      <div class="py-1" role="none">
        <button class="text-white block px-4 py-2 text-sm hover:bg-slate-700" on:click={createNewProject}>
          + Create new project
        </button>
        {#if $projectList.length > 0}
          {#each $projectList as project}
            <button class="text-white block px-4 py-2 text-sm hover:bg-slate-700" on:click={() => selectProject(project)}>
              {project}
            </button>
          {/each}
        {/if}
      </div>
    </div>
  </div>

  <div class="right-controls" style="display: flex; align-items: center; gap: 20px">
    <div class="flex items-center space-x-2">
      <span>Internet:</span>
      <div id="internet-status" class="internet-status" class:online={$internet} class:offline={!$internet} />
      <span id="internet-status-text" />
    </div>
    <div class="flex items-center space-x-2">
      <span>Token Usage:</span>
      <span id="token-count" class="token-count-animation">{tokenUsage}</span>
    </div>
    <div class="relative inline-block text-left">
      <div>
        <button
          type="button"
          class="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-slate-900 px-3 py-2 text-sm font-semibold text-white shadow-sm ring-1 ring-inset ring-indigo-700 hover:bg-slate-800"
          id="model-button"
          aria-expanded="true"
          aria-haspopup="true"
        >
          <span id="selected-model">{$selectedModel}</span>
          <svg class="-mr-1 h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>

      <div
        id="model-dropdown"
        class="absolute right-0 z-10 mt-2 w-full origin-top-right rounded-md bg-slate-800 shadow-lg ring-1 ring-indigo-700 ring-opacity-5 focus:outline-none hidden"
        role="menu"
        aria-orientation="vertical"
        aria-labelledby="model-button"
        tabindex="-1"
      >
        <div class="py-1" role="none">
          {#if $modelList.length > 0}
            {#each $modelList as model}
              <button
                class="text-white block px-4 py-2 text-sm hover:bg-slate-700"
                on:click={() => selectModel(model)}
              >
                {model[0]} ({model[1]})
              </button>
            {/each}
          {/if}
        </div>
      </div>
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