<script>
  import { onMount } from "svelte";
  import { socket } from "$lib/api";
  import { toast } from "svelte-sonner";
  
  // Available agents
  const agents = [
    { id: "bambu-executiveusa", name: "Bambu", role: "CEO & Coordinator" },
    { id: "pauli-planner", name: "Pauli", role: "Planner" },
    { id: "synthia-executor", name: "Synthia", role: "Executor" },
    { id: "alex-metagpt", name: "Alex", role: "Developer" }
  ];
  
  // Invitation form
  let selectedAgent = "";
  let invitationMessage = "";
  let meetingId = "";
  
  // Invitations
  let sentInvitations = [];
  let receivedInvitations = [];
  let isLoading = false;
  
  function sendInvitation() {
    if (!selectedAgent) {
      toast.error("Please select an agent to invite");
      return;
    }
    
    socket.emit("invitation-send", {
      to_agent: selectedAgent,
      message: invitationMessage,
      meeting_id: meetingId || null
    });
    
    // Reset form
    selectedAgent = "";
    invitationMessage = "";
    meetingId = "";
    
    toast.success("Invitation sent");
  }
  
  function loadInvitations() {
    isLoading = true;
    socket.emit("invitation-list", {});
  }
  
  function acceptInvitation(invitationId) {
    socket.emit("invitation-accept", { invitation_id: invitationId });
    toast.success("Invitation accepted");
  }
  
  function declineInvitation(invitationId) {
    socket.emit("invitation-decline", { invitation_id: invitationId });
    toast.info("Invitation declined");
  }
  
  function getStatusBadgeClass(status) {
    const classes = {
      'pending': 'bg-yellow-500/20 text-yellow-600',
      'accepted': 'bg-green-500/20 text-green-600',
      'declined': 'bg-red-500/20 text-red-600',
      'expired': 'bg-gray-500/20 text-gray-600'
    };
    return classes[status] || 'bg-gray-500/20 text-gray-600';
  }
  
  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleString();
  }
  
  function getAgentName(agentId) {
    const agent = agents.find(a => a.id === agentId);
    return agent ? agent.name : agentId;
  }
  
  onMount(() => {
    loadInvitations();
    
    socket.on("invitation-list-response", (data) => {
      sentInvitations = data.sent || [];
      receivedInvitations = data.received || [];
      isLoading = false;
    });
    
    socket.on("invitation-received", (data) => {
      receivedInvitations = [data, ...receivedInvitations];
      toast.info(`New invitation from ${getAgentName(data.from_agent)}`);
    });
    
    socket.on("invitation-updated", (data) => {
      // Update the invitation in the list
      sentInvitations = sentInvitations.map(inv => 
        inv.invitation_id === data.invitation_id ? data : inv
      );
    });
  });
</script>

<div class="flex h-full gap-4">
  <!-- Send Invitation Form -->
  <div class="w-1/3 bg-secondary rounded-xl p-4 overflow-y-auto">
    <h2 class="text-lg font-semibold mb-4 text-primary">Send Invitation</h2>
    
    <div class="space-y-4">
      <!-- Select Agent -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Invite Agent *
        </label>
        <select
          bind:value={selectedAgent}
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Select an agent...</option>
          {#each agents as agent}
            <option value={agent.id}>{agent.name} ({agent.role})</option>
          {/each}
        </select>
      </div>
      
      <!-- Message -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Message
        </label>
        <textarea
          bind:value={invitationMessage}
          placeholder="Let's discuss the project..."
          rows="3"
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary resize-none"
        ></textarea>
      </div>
      
      <!-- Meeting ID (optional) -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Meeting ID (optional)
        </label>
        <input
          type="text"
          bind:value={meetingId}
          placeholder="Leave empty for ad-hoc invitation"
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
      
      <!-- Submit -->
      <button
        on:click={sendInvitation}
        class="w-full py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
      >
        Send Invitation
      </button>
    </div>
    
    <!-- Quick Invite Buttons -->
    <div class="mt-6">
      <h3 class="text-sm font-medium text-muted-foreground mb-2">Quick Invite</h3>
      <div class="space-y-2">
        {#each agents as agent}
          <button
            on:click={() => {
              selectedAgent = agent.id;
              invitationMessage = `Hey ${agent.name}, can we chat?`;
            }}
            class="w-full py-2 px-3 bg-primary/5 rounded-lg text-sm text-left hover:bg-primary/10 transition-colors"
          >
            Invite {agent.name}
          </button>
        {/each}
      </div>
    </div>
  </div>
  
  <!-- Invitations Lists -->
  <div class="flex-1 flex flex-col gap-4 overflow-hidden">
    <!-- Received Invitations -->
    <div class="flex-1 bg-secondary rounded-xl p-4 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-4 text-primary">
        Received Invitations
        {#if receivedInvitations.length > 0}
          <span class="ml-2 px-2 py-0.5 bg-primary/20 rounded-full text-xs">
            {receivedInvitations.filter(i => i.status === 'pending').length} pending
          </span>
        {/if}
      </h2>
      
      {#if isLoading}
        <div class="text-center py-4 text-muted-foreground">
          Loading...
        </div>
      {:else if receivedInvitations.length === 0}
        <div class="text-center py-4 text-muted-foreground">
          No invitations received
        </div>
      {:else}
        <div class="space-y-3">
          {#each receivedInvitations as invitation}
            <div class="p-3 bg-primary/5 rounded-lg border border-border">
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-medium text-primary">
                    From: {getAgentName(invitation.from_agent)}
                  </p>
                  <p class="text-sm text-muted-foreground mt-1">
                    {invitation.message || "No message"}
                  </p>
                  <p class="text-xs text-muted-foreground mt-1">
                    {formatDate(invitation.created_at)}
                  </p>
                </div>
                <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(invitation.status)}">
                  {invitation.status}
                </span>
              </div>
              
              {#if invitation.status === 'pending'}
                <div class="mt-3 flex gap-2">
                  <button
                    on:click={() => acceptInvitation(invitation.invitation_id)}
                    class="px-3 py-1 bg-green-500/20 text-green-600 rounded text-sm hover:bg-green-500/30 transition-colors"
                  >
                    Accept
                  </button>
                  <button
                    on:click={() => declineInvitation(invitation.invitation_id)}
                    class="px-3 py-1 bg-red-500/20 text-red-600 rounded text-sm hover:bg-red-500/30 transition-colors"
                  >
                    Decline
                  </button>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>
    
    <!-- Sent Invitations -->
    <div class="flex-1 bg-secondary rounded-xl p-4 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-4 text-primary">Sent Invitations</h2>
      
      {#if sentInvitations.length === 0}
        <div class="text-center py-4 text-muted-foreground">
          No invitations sent
        </div>
      {:else}
        <div class="space-y-3">
          {#each sentInvitations as invitation}
            <div class="p-3 bg-primary/5 rounded-lg border border-border">
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-medium text-primary">
                    To: {getAgentName(invitation.to_agent)}
                  </p>
                  <p class="text-sm text-muted-foreground mt-1">
                    {invitation.message || "No message"}
                  </p>
                  <p class="text-xs text-muted-foreground mt-1">
                    {formatDate(invitation.created_at)}
                  </p>
                </div>
                <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(invitation.status)}">
                  {invitation.status}
                </span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>