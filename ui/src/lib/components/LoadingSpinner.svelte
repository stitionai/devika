<script>
  export let size = "h-8 w-8";
  export let message = "Loading...";
</script>

<div class="flex items-center justify-center h-full">
  <div class="text-center">
    <div class="animate-spin rounded-full {size} border-b-2 border-primary mx-auto mb-4"></div>
    <p class="text-foreground-light">{message}</p>
  </div>
</div>
