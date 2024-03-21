<script>
  import { onMount } from "svelte";
  import { projectList, modelList, internet } from "../store";
  import { createProject, fetchProjectList, getTokenUsage } from "../api";

  let selectedProject;
  let selectedModel;

  if (projectList !== null) {
    selectedProject = "Select Project";
    localStorage.setItem("selectedProject", "");
  } else {
    selectedProject = localStorage.getItem("selectedProject") || projectList[0];
  }
  if(modelList !== null) {
    selectedModel = localStorage.getItem("selectedModel") || modelList[0][1];
  } else {
    selectedModel = "Select Model";
    localStorage.setItem("selectedModel", "");
  }

  let tokenUsage = 0;

  async function updateTokenUsage() {
    tokenUsage = await getTokenUsage();
  }

  function selectProject(project) {
    selectedProject = project;
    localStorage.setItem("selectedProject", project);
    document.getElementById("project-dropdown").classList.add("hidden");
  }

  function selectModel(model) {
    selectedModel = `${model[0]} (${model[1]})`;
    localStorage.setItem("selectedModel", model[1]);
    document.getElementById("model-dropdown").classList.add("hidden");
  }

  async function createNewProject() {
    const projectName = prompt("Enter the project name:");
    if (projectName) {
      await createProject(projectName);
      await fetchProjectList();
      selectProject(projectName);
    }
  }

  function closeDropdowns(event) {
    const projectDropdown = document.getElementById("project-dropdown");
    const modelDropdown = document.getElementById("model-dropdown");
    const projectButton = document.getElementById("project-button");
    const modelButton = document.getElementById("model-button");

    if (
      !projectDropdown.contains(event.target) &&
      !projectButton.contains(event.target)
    ) {
      projectDropdown.classList.add("hidden");
    }

    if (
      !modelDropdown.contains(event.target) &&
      !modelButton.contains(event.target)
    ) {
      modelDropdown.classList.add("hidden");
    }
  }

  onMount(async () => {
    await updateTokenUsage();

    document
      .getElementById("project-button")
      .addEventListener("click", function () {
        const dropdown = document.getElementById("project-dropdown");
        dropdown.classList.toggle("hidden");
      });

    document
      .getElementById("model-button")
      .addEventListener("click", function () {
        const dropdown = document.getElementById("model-dropdown");
        dropdown.classList.toggle("hidden");
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
      class="inline-flex items-center justify-center w-full gap-2 rounded-md px-3 py-2 text-sm font-semibold border-2 border-gray-200 "
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
        <a
          href="#"
          class="flex gap-2 items-center text-sm px-4 py-3 w-full"
          on:click|preventDefault={createNewProject}
        >
        <i class="fas fa-plus"></i>
          new project
        </a>
        {#if $projectList !== null}
          {#each $projectList as project}
            <a
              href="#"
              class="flex gap-2 items-center text-sm px-4 py-3 w-full text-clip {selectedProject === project ? 'bg-gray-300' : ''}"
              on:click|preventDefault={() => selectProject(project)}
            >
              {project}
            </a>
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
      <span id="token-count" class="token-count-animation">{tokenUsage}</span>
    </div>
    <div class="relative inline-block text-left">
      <div>
        <button
          type="button"
          class="inline-flex items-center justify-center w-fit gap-x-1.5 rounded-md px-3 py-2 text-sm font-semibold ring-2 ring-inset ring-black"
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
        <div class="flex flex-col divide-y-2 w-full" role="none">
          {#if $modelList !== null}
            {#each $modelList as model}
              <a
                href="#"
                class="flex gap-2 items-center text-sm px-4 py-3 w-full text-clip 
                {(selectedModel == `${model[0]} (${model[1]})`) || (
                  selectedModel == model[1]
                ) ? 'bg-gray-300' : ''}"
                on:click|preventDefault={() => selectModel(model)}
              >
                {model[0]} ({model[1]})
              </a>
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
  /* no visible scrollbar */
  #model-dropdown {
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
    scroll-behavior: smooth;
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
