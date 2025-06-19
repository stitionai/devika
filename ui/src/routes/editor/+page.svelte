<script>
  import { onMount } from 'svelte';
  import { selectedProject } from '$lib/store';
  import { WebCodeEditor } from '$lib/components/CodeEditor';
  import { toast } from 'svelte-sonner';

  let editorHeight = '100%';

  onMount(() => {
    // Set editor height based on viewport
    const updateHeight = () => {
      const vh = window.innerHeight;
      const headerHeight = 60; // Approximate header height
      editorHeight = `${vh - headerHeight}px`;
    };

    updateHeight();
    window.addEventListener('resize', updateHeight);
    
    return () => {
      window.removeEventListener('resize', updateHeight);
    };
  });

  $: if (!$selectedProject || $selectedProject === 'select project') {
    toast.error('Please select a project first');
  }
</script>

<div class="editor-page h-full w-full">
  {#if $selectedProject && $selectedProject !== 'select project'}
    <WebCodeEditor height={editorHeight} />
  {:else}
    <div class="no-project flex items-center justify-center h-full">
      <div class="text-center text-tertiary">
        <i class="fas fa-folder-open text-6xl mb-4"></i>
        <h2 class="text-2xl mb-2">No Project Selected</h2>
        <p class="text-lg">Please select a project from the control panel to start coding</p>
      </div>
    </div>
  {/if}
</div>

<style>
  .editor-page {
    background-color: var(--background);
  }
  
  .no-project {
    background-color: var(--terminal-window-background);
  }
</style>