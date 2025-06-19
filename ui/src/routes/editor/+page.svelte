<script>
  import { onMount } from 'svelte';
  import { selectedProject } from '$lib/store';
  import { EnhancedWebCodeEditor } from '$lib/components/CodeEditor';
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
    <EnhancedWebCodeEditor height={editorHeight} />
  {:else}
    <div class="no-project flex items-center justify-center h-full">
      <div class="text-center text-tertiary">
        <i class="fas fa-folder-open text-6xl mb-4 opacity-50"></i>
        <h2 class="text-2xl mb-2 font-light">No Project Selected</h2>
        <p class="text-lg mb-4 opacity-75">Please select a project from the control panel to start coding</p>
        <div class="space-y-2 text-sm">
          <p>✨ Enhanced with Svelte for better performance</p>
          <p>🚀 Advanced features and smooth interactions</p>
          <p>💡 Intelligent code completion and suggestions</p>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .editor-page {
    background-color: var(--background);
  }
  
  .no-project {
    background: linear-gradient(135deg, var(--terminal-window-background) 0%, var(--secondary) 100%);
  }
</style>