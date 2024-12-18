<script>
  export let message = "An error occurred";
  export let retryAction = () => window.location.reload();
</script>

<div class="flex items-center justify-center h-full">
  <div class="text-center">
    <p class="text-red-500 mb-2">{message}</p>
    <button
      class="px-4 py-2 bg-primary text-foreground-invert rounded hover:bg-btn-active"
      on:click={retryAction}>
      Retry
    </button>
  </div>
</div>
