<script>
  export let message;
  
  // Determine if this is a system message
  $: isSystem = message.agent_id === 'system';
  
  // Get agent color based on agent_id
  $: agentColor = getAgentColor(message.agent_id);
  
  function getAgentColor(agentId) {
    const colors = {
      'bambu-executiveusa': '#4F46E5',
      'pauli-planner': '#059669',
      'synthia-executor': '#DC2626',
      'alex-metagpt': '#D97706',
      'user': '#6366F1',
      'system': '#6B7280'
    };
    return colors[agentId] || '#6B7280';
  }
  
  function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

{#if isSystem}
  <!-- System Message -->
  <div class="flex justify-center">
    <div class="px-4 py-2 bg-muted rounded-full text-xs text-muted-foreground">
      {message.content}
    </div>
  </div>
{:else}
  <!-- Agent/User Message -->
  <div class="flex gap-3 items-start">
    <!-- Avatar -->
    <div 
      class="w-8 h-8 rounded-full flex items-center justify-center text-white font-medium text-sm flex-shrink-0"
      style="background-color: {agentColor}"
    >
      {message.agent_name[0]}
    </div>
    
    <!-- Message Content -->
    <div class="flex-1">
      <div class="flex items-baseline gap-2">
        <span class="font-medium text-sm" style="color: {agentColor}">
          {message.agent_name}
        </span>
        <span class="text-xs text-muted-foreground">
          {formatTime(message.timestamp)}
        </span>
      </div>
      
      <div class="mt-1 px-3 py-2 bg-primary/10 rounded-lg">
        <p class="text-sm text-foreground">{message.content}</p>
      </div>
    </div>
  </div>
{/if}