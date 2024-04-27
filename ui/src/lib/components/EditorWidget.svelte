<script>
    import { onDestroy, onMount } from 'svelte';
    import { initializeMonaco, createEditors, disposeEditors, enableTabSwitching } from './MonacoEditor';
    import { socket, fetchProjectFiles } from "$lib/api";
    import { selectedProject, projectFiles } from "$lib/store";

    let monaco;
    let editors = {};
    let editorContainer;
    let tabContainer;

    const reCreateEditor = async (files) => {
        disposeEditors(editors);
        editors = {};
        files.forEach((file) => {
            let editor = createEditors(editorContainer, monaco, file);
            editors = {
                ...editors,
                [file.file]: editor
            };
        });
        enableTabSwitching(editors, tabContainer);
    };

    const patchOrFeature = (files) => {
        files.forEach((file, index) => {
            const editor = editors[file.file];
            if (editor) {
                editor.setValue(file.code);
            }else {
              let editor = createEditors(editorContainer, monaco, file);
                editors = {
                  ...editors,
                  [file.file]: editor
              };
            }
        });
        enableTabSwitching(editors, tabContainer);
    };

    const initializeEditor = async () => {
        monaco = await initializeMonaco();
        // const files = await fetchProjectFiles();
        // reCreateEditor(files)
    };

    onMount(async () => {
        await initializeEditor()
        socket.on('code', async function (data) {
          if(data.from === 'coder'){
            reCreateEditor(data.files);
          }else{
            patchOrFeature(data.files)
          }
        });

        projectFiles.subscribe((files) => {
          if (files){
            reCreateEditor(files);
          }
        });
    });

    onDestroy(() => {
        disposeEditors(editors);
    });

    // $: if ($selectedProject && $selectedProject != 'select project') {
    //   initializeEditor()
    // }
</script>


<div
  class="w-full h-full flex flex-1 flex-col border-[3px] overflow-hidden rounded-xl border-window-outline p-0"
>
  <div class="flex items-center p-2 border-b bg-terminal-window-ribbon">
    <div class="flex ml-2 mr-4 space-x-2">
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
    </div>
      <div class="flex text-tertiary text-sm overflow-x-auto" bind:this={tabContainer} />
      {#if Object.keys(editors).length == 0}
        <div class="flex items-center text-tertiary text-sm">Code viewer</div>
      {/if}
  </div>
  <div
    class="h-full rounded-bl-lg bg-terminal-window-background p-0" bind:this={editorContainer}
  ></div>
</div>