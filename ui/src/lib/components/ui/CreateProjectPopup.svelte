<script>
    import { createEventDispatcher } from "svelte";
    import { fly } from 'svelte/transition';
    import { createProject, fetchProjectList } from "$lib/api";
    import { selectedProject } from '$lib/store';

    const dispatch = createEventDispatcher();

    let projectName = '';

    async function createNewProject(){

        if (projectName) {

            const createProjectMessage  = await createProject(projectName);
            alert(createProjectMessage);
            await fetchProjectList();

            selectedProject.set(projectName);
            projectName = '';
        }

    }
</script>

<style>
input[type=text]{
    border-radius: 5px;
    border-width: 2px;
    border-color: #4338ca;
    line-height: 30px;
    background-color: #000000;
    color: white;
    box-sizing: border-box;
}

input[type=text]:focus{
    outline: none;
}

input[type=text]::placeholder{
    padding: 10px; 
}

button {

    margin-left: 10px;
    border-radius: 5px;
    border-width: 2px;
    border-color: #4338ca;
    padding: 5px 10px 5px 10px;
}

button:hover {

margin-left: 10px;
border-radius: 5px;
border-width: 2px;
border-color: #4338ca;
padding: 5px 10px 5px 10px;
}
</style>

<div class="create-project-wrapper" >
    <div class="newproject-popup" transition:fly={{y: -500}}>
    
        <input bind:value={projectName} type="text" id="pname" placeholder="Enter project name">
        
        <button on:click={() => createNewProject()}>Create </button>
               
    </div>
</div>