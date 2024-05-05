<script>
    import { onDestroy, onMount } from 'svelte';
    import { initializeMonaco, initializeEditorRef, createModel, disposeEditor, enableTabSwitching, sidebar } from './MonacoEditor';
    import { socket } from "$lib/api";
    import { projectFiles } from "$lib/store";

    let monaco;
    let models = {};
    let editor = null;
    let editorContainer;
    let tabContainer;
    let sidebarContainer;

    const reCreateEditor = async (files) => {
        disposeEditor(editor);
        models = {};
        editor = await initializeEditorRef(monaco, editorContainer)
        files.forEach((file) => {
            let model = createModel(monaco, file);
            editor.setModel(model);
            models = {
                ...models,
                [file.file]: model
            };
        });
        enableTabSwitching(editor, models, tabContainer);
        sidebar(editor, models, sidebarContainer);
    };

    const patchOrFeature = (files) => {
        files.forEach((file, index) => {
            const model = models[file.file];
            if (model) {
                model.setValue(file.code);
            }else {
              let model = createModel(monaco, file);
                models = {
                  ...models,
                  [file.file]: model
              };
            }
        });
        enableTabSwitching(editor, models, tabContainer);
        sidebar(editor, models, sidebarContainer);
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
        disposeEditor(editor);
        models = {};
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
      <div id="tabContainer" class="flex text-tertiary text-sm overflow-x-auto" bind:this={tabContainer} />
      {#if Object.keys(models).length == 0}
        <div class="flex items-center text-tertiary text-sm">Code viewer</div>
      {/if}
  </div>
  <div class="h-full w-full flex">
    <div class="min-w-[260px] overflow-y-auto bg-secondary h-full text-foreground text-sm flex flex-col pt-2" bind:this={sidebarContainer} />
    <div class="h-full w-full rounded-bl-lg bg-terminal-window-background p-0" bind:this={editorContainer} />
  </div>
</div>