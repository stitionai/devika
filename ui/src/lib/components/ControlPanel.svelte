<script>
  import { onMount } from "svelte";
  import { projectList, modelList, internet, tokenUsage, agentState, messages, searchEngineList} from "$lib/store";
  import { createProject, fetchMessages, fetchInitialData, deleteProject, fetchAgentState} from "$lib/api";
  import { get } from "svelte/store";

  let selectedProject;
  let selectedModel;
  let selectedSearchEngine;

  const checkListAndSetItem = (list, itemKey, defaultItem) => {
    if (get(list) && get(list).length > 0) {
      const item = localStorage.getItem(itemKey);
      return item ? item : defaultItem;
    } else {
      localStorage.setItem(itemKey, "");
      return defaultItem;
    }
  };

  selectedProject = checkListAndSetItem( projectList, "selectedProject", "Select Project");
  selectedModel = checkListAndSetItem( modelList, "selectedModel", "Select Model");
  selectedSearchEngine = checkListAndSetItem( searchEngineList, "selectedSearchEngine", "Select Search Engine");


  function selectProject(project) {
    selectedProject = project;
    localStorage.setItem("selectedProject", project);
    fetchMessages();
    fetchAgentState();
    document.getElementById("project-dropdown").classList.add("hidden");
  }
  function selectModel(model) {
    selectedModel = `${model[0]}`;
    localStorage.setItem("selectedModel", model[1]);
    document.getElementById("model-dropdown").classList.add("hidden");
  }
  function selectSearchEngine(searchEngine) {
    selectedSearchEngine = searchEngine;
    localStorage.setItem("selectedSearchEngine", searchEngine);
    document.getElementById("search-engine-dropdown").classList.add("hidden");
  }

  async function createNewProject() {
    const projectName = prompt('Enter the project name:');
    if (projectName) {
      await createProject(projectName);
      selectProject(projectName);
    }
  }
  async function deleteproject(project) {
    if (confirm(`Are you sure you want to delete ${project}?`)) {
      await deleteProject(project);
      await fetchInitialData();
      messages.set([]);
      agentState.set(null);
      tokenUsage.set(0);
      selectedProject = "Select Project";
      localStorage.setItem("selectedProject", "");
    }
  }

  const dropdowns = [
    { dropdown: "project-dropdown", button: "project-button" },
    { dropdown: "model-dropdown", button: "model-button" },
    { dropdown: "search-engine-dropdown", button: "search-engine-button" },
  ];
  function closeDropdowns(event) {
    dropdowns.forEach(({ dropdown, button }) => {
      const dropdownElement = document.getElementById(dropdown);
      const buttonElement = document.getElementById(button);

      if (
        dropdownElement &&
        buttonElement &&
        !dropdownElement.contains(event.target) &&
        !buttonElement.contains(event.target)
      ) {
        dropdownElement.classList.add("hidden");
      }
    });
  }
  onMount(() => {
    dropdowns.forEach(({ dropdown, button }) => {
      document.getElementById(button).addEventListener("click", function () {
        const dropdownElement = document.getElementById(dropdown);
        dropdownElement.classList.toggle("hidden");
      });
    });
    document.addEventListener("click", closeDropdowns);
    return () => {
      document.removeEventListener("click", closeDropdowns);
    };
  });
  
</script>

<div class="control-panel">
  <div class="dropdown-menu relative inline-block">
    <button
      type="button"
      class="inline-flex items-center justify-center w-full gap-2 rounded-md px-3 py-2 text-sm font-semibold border-2 border-gray-300"
      id="project-button"
      aria-expanded="true"
      aria-haspopup="true"
    >
      <span id="selected-project">{selectedProject}</span>
      <i class="fas fa-angle-down"></i>
    </button>
    <div
      id="project-dropdown"
      class="absolute left-0 z-10 mt-2 w-40 origin-top-left rounded-md bg-gray-100 shadow-lg max-h-96 overflow-y-auto hidden"
      role="menu"
      aria-orientation="vertical"
      aria-labelledby="project-button"
      tabindex="-1"
    >
      <div role="none" class="flex flex-col divide-y-2 w-full">
        <button
          class="flex gap-2 items-center text-sm px-4 py-3 w-full"
          on:click|preventDefault={createNewProject}
        >
          <i class="fas fa-plus"></i>
          new project
        </button>
        {#if $projectList !== null}
          {#each $projectList as project}
            <div
              class="flex items-center px-4 hover:bg-gray-200 transition-colors">
              <button
                href="#"
                class="flex gap-2 items-center text-sm py-3 w-full h-full overflow-x-visible"
                on:click|preventDefault={() => selectProject(project)}
              >
                {project}
              </button>
              <button
                class="fa-regular fa-trash-can hover:text-red-600"
                on:click={() => deleteproject(project)}
                aria-label="Delete project"
              ></button>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
  <div
    class="right-controls"
    style="display: flex; align-items: center; gap: 20px"
  >
    <div class="flex items-center space-x-2">
      <span>Internet:</span>
      <div
        id="internet-status"
        class="internet-status"
        class:online={$internet}
        class:offline={!$internet}
      ></div>
      <span id="internet-status-text"></span>
    </div>
    <div class="flex items-center space-x-2">
      <span>Token Usage:</span>
      <span id="token-count" class="token-count-animation">{$tokenUsage}</span>
    </div>
    <div class="relative inline-block text-left">
      <div>
        <button
          type="button"
          class="inline-flex items-center justify-center w-fit gap-2 rounded-md px-3 py-2 text-sm font-semibold border-2 border-gray-300"
          id="search-engine-button"
          aria-expanded="true"
          aria-haspopup="true"
        >
          <span id="selected-search-engine">{selectedSearchEngine}</span>
          <i class="fas fa-angle-down"></i>
        </button>
      </div>

      <div
        id="search-engine-dropdown"
        class="absolute left-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-gray-100 shadow-lg max-h-96 overflow-y-auto hidden"
        role="menu"
        aria-orientation="vertical"
        aria-labelledby="search-engine-button"
        tabindex="-1"
      >
        <div role="none" class="flex flex-col divide-y-2 w-full">
          {#if $searchEngineList !== null}
            {#each $searchEngineList as engine}
              <div
                class="flex items-center px-4 hover:bg-gray-300 transition-colors
            {selectSearchEngine === engine ? 'bg-gray-300' : ''}"
              >
                <button
                  href="#"
                  class="flex gap-2 items-center text-sm py-3 w-full text-clip"
                  on:click|preventDefault={() => selectSearchEngine(engine)}
                >
                  {engine}
                </button>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
    <div class="relative inline-block text-left">
      <div>
        <button
          type="button"
          class="inline-flex items-center justify-center w-fit gap-x-1.5 rounded-md px-3 py-2 text-sm font-semibold border-2 border-gray-300"
          id="model-button"
          aria-expanded="true"
          aria-haspopup="true"
        >
          <span id="selected-model">{selectedModel}</span>
          <i class="fas fa-angle-down"></i>
        </button>
      </div>

      <div
        id="model-dropdown"
        class="absolute right-0 z-10 mt-2 w-64 origin-top-right rounded-md bg-gray-100 shadow-lg max-h-96 overflow-y-auto hidden"
        role="menu"
        aria-orientation="vertical"
        aria-labelledby="model-button"
        tabindex="-1"
      >
        {#if $modelList !== null}
          <div class="flex flex-col divide-y-2">
            {#each Object.entries($modelList) as [modelName, modelItems]}
              <div class="flex flex-col py-4 gap-2" role="none">
                <span class="text-sm px-4 w-full font-semibold"
                  >{modelName.toLowerCase()}</span
                >
                <div class="flex flex-col gap-[1px] px-6 w-full">
                  {#each modelItems as models}
                    <button
                      class="relative nav-button flex text-start text-sm text-clip hover:bg-gray-300 px-2 py-1 rounded-md
                      transition-colors {selectedModel ==
                        `${models[0]} (${models[1]})` ||
                      selectedModel == models[1]
                        ? 'bg-gray-300'
                        : ''}"
                      on:click|preventDefault={() => selectModel(models)}
                    >
                      {models[0]}
                      <span class="tooltip text-[10px] px-2 text-gray-500"
                        >{models[1]}</span
                      >
                    </button>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .tooltip {
    font-size: 10px;
    background-color: black;
    color: white;
    text-align: center;
    border-radius: 100px;
    padding: 5px 10px;
    position: absolute;
    z-index: 1;
    opacity: 0;
    top: -20px;
    right: 0;
    transition: opacity 0.3s;
  }
  .nav-button:hover .tooltip {
    visibility: visible;
    opacity: 1;
  }
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
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .control-panel > *:not(:first-child) {
    margin-left: 20px;
  }

  .right-controls > *:not(:last-child) {
    border-right: 1px solid #4b5563;
    padding-right: 20px;
  }
</style>
