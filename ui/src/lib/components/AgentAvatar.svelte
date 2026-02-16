<script>
  export let agent;
  export let presence = null;
  export let isSpeaking = false;
  export let isTyping = false;
  
  // Get status color
  $: statusColor = getStatusColor(presence?.status || 'offline');
  $: statusText = getStatusText(presence?.status || 'offline');
  
  function getStatusColor(status) {
    const colors = {
      'online': '#22C55E',
      'offline': '#6B7280',
      'busy': '#F59E0B',
      'in_meeting': '#3B82F6',
      'idle': '#9CA3AF'
    };
    return colors[status] || '#6B7280';
  }
  
  function getStatusText(status) {
    const texts = {
      'online': 'Online',
      'offline': 'Offline',
      'busy': 'Busy',
      'in_meeting': 'In Meeting',
      'idle': 'Idle'
    };
    return texts[status] || 'Unknown';
  }
</script>

<div class="flex flex-col items-center p-3 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors">
  <!-- Avatar Container -->
  <div class="relative">
    <!-- Avatar Circle -->
    <div 
      class="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl"
      style="background-color: {agent.color}"
    >
      {agent.name[0]}
    </div>
    
    <!-- Status Ring -->
    <div 
      class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-2 border-secondary"
      style="background-color: {statusColor}"
      title={statusText}
    ></div>
    
    <!-- Speaking Indicator -->
    {#if isSpeaking}
      <div class="absolute -top-1 -right-1">
        <div class="flex gap-0.5">
          <div class="w-1 h-3 bg-green-500 rounded animate-pulse"></div>
          <div class="w-1 h-4 bg-green-500 rounded animate-pulse" style="animation-delay: 0.1s"></div>
          <div class="w-1 h-2 bg-green-500 rounded animate-pulse" style="animation-delay: 0.2s"></div>
        </div>
      </div>
    {/if}
    
    <!-- Typing Indicator -->
    {#if isTyping}
      <div class="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
        <div class="flex gap-1 bg-primary/20 px-2 py-1 rounded-full">
          <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></div>
          <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
          <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Agent Info -->
  <div class="mt-2 text-center">
    <p class="font-medium text-sm text-primary">{agent.name}</p>
    <p class="text-xs text-muted-foreground">{agent.role}</p>
  </div>
  
  <!-- Current Task (if busy) -->
  {#if presence?.current_task}
    <div class="mt-1 px-2 py-0.5 bg-yellow-500/20 rounded text-xs text-yellow-600 truncate max-w-full">
      {presence.current_task}
    </div>
  {/if}
</div>

<style>
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .animate-pulse {
    animation: pulse 1s ease-in-out infinite;
  }
  
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
  }
  
  .animate-bounce {
    animation: bounce 0.6s ease-in-out infinite;
  }
</style>