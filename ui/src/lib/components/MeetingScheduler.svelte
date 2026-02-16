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
  
  // Meeting form
  let title = "";
  let scheduledDate = "";
  let scheduledTime = "";
  let duration = 30;
  let selectedAgents = [];
  let agenda = "";
  let recurrence = "";
  
  // Scheduled meetings
  let meetings = [];
  let isLoading = false;
  
  // Recurrence options
  const recurrenceOptions = [
    { value: "", label: "One-time" },
    { value: "0 9 * * *", label: "Daily at 9 AM" },
    { value: "0 9 * * 1", label: "Weekly (Monday 9 AM)" },
    { value: "0 9 * * 1,3,5", label: "Mon/Wed/Fri 9 AM" },
    { value: "0 10 1 * *", label: "Monthly (1st at 10 AM)" }
  ];
  
  function toggleAgent(agentId) {
    if (selectedAgents.includes(agentId)) {
      selectedAgents = selectedAgents.filter(id => id !== agentId);
    } else {
      selectedAgents = [...selectedAgents, agentId];
    }
  }
  
  function createMeeting() {
    if (!title || !scheduledDate || !scheduledTime || selectedAgents.length === 0) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    const scheduledDateTime = `${scheduledDate}T${scheduledTime}:00`;
    
    socket.emit("meeting-create", {
      title,
      scheduled_time: scheduledDateTime,
      duration_minutes: duration,
      organizer: "user",
      attendees: selectedAgents,
      agenda: agenda.split("\n").filter(a => a.trim()),
      recurrence
    });
    
    // Reset form
    title = "";
    scheduledDate = "";
    scheduledTime = "";
    duration = 30;
    selectedAgents = [];
    agenda = "";
    recurrence = "";
    
    toast.success("Meeting created successfully");
  }
  
  function loadMeetings() {
    isLoading = true;
    socket.emit("meeting-list", { upcoming_only: true });
  }
  
  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleString();
  }
  
  function getStatusBadgeClass(status) {
    const classes = {
      'scheduled': 'bg-blue-500/20 text-blue-600',
      'in_progress': 'bg-green-500/20 text-green-600',
      'completed': 'bg-gray-500/20 text-gray-600',
      'cancelled': 'bg-red-500/20 text-red-600'
    };
    return classes[status] || 'bg-gray-500/20 text-gray-600';
  }
  
  onMount(() => {
    loadMeetings();
    
    socket.on("meeting-list-response", (data) => {
      meetings = data.meetings || [];
      isLoading = false;
    });
    
    socket.on("meeting-created", (data) => {
      meetings = [data.meeting, ...meetings];
    });
  });
</script>

<div class="flex h-full gap-4">
  <!-- Create Meeting Form -->
  <div class="w-1/3 bg-secondary rounded-xl p-4 overflow-y-auto">
    <h2 class="text-lg font-semibold mb-4 text-primary">Schedule Meeting</h2>
    
    <div class="space-y-4">
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Meeting Title *
        </label>
        <input
          type="text"
          bind:value={title}
          placeholder="Daily Standup"
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
      
      <!-- Date & Time -->
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-sm font-medium text-muted-foreground mb-1">
            Date *
          </label>
          <input
            type="date"
            bind:value={scheduledDate}
            class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-muted-foreground mb-1">
            Time *
          </label>
          <input
            type="time"
            bind:value={scheduledTime}
            class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>
      
      <!-- Duration -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Duration (minutes)
        </label>
        <select
          bind:value={duration}
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value={15}>15 minutes</option>
          <option value={30}>30 minutes</option>
          <option value={45}>45 minutes</option>
          <option value={60}>1 hour</option>
          <option value={90}>1.5 hours</option>
          <option value={120}>2 hours</option>
        </select>
      </div>
      
      <!-- Attendees -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-2">
          Attendees *
        </label>
        <div class="space-y-2">
          {#each agents as agent}
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedAgents.includes(agent.id)}
                on:change={() => toggleAgent(agent.id)}
                class="w-4 h-4 rounded border-border"
              />
              <span class="text-sm">{agent.name}</span>
              <span class="text-xs text-muted-foreground">({agent.role})</span>
            </label>
          {/each}
        </div>
      </div>
      
      <!-- Agenda -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Agenda (one item per line)
        </label>
        <textarea
          bind:value={agenda}
          placeholder="Status updates&#10;Blockers&#10;Next steps"
          rows="3"
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary resize-none"
        ></textarea>
      </div>
      
      <!-- Recurrence -->
      <div>
        <label class="block text-sm font-medium text-muted-foreground mb-1">
          Recurrence
        </label>
        <select
          bind:value={recurrence}
          class="w-full px-3 py-2 bg-primary/10 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {#each recurrenceOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
      </div>
      
      <!-- Submit -->
      <button
        on:click={createMeeting}
        class="w-full py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
      >
        Create Meeting
      </button>
    </div>
  </div>
  
  <!-- Scheduled Meetings List -->
  <div class="flex-1 bg-secondary rounded-xl p-4 overflow-y-auto">
    <h2 class="text-lg font-semibold mb-4 text-primary">Upcoming Meetings</h2>
    
    {#if isLoading}
      <div class="text-center py-8 text-muted-foreground">
        Loading meetings...
      </div>
    {:else if meetings.length === 0}
      <div class="text-center py-8 text-muted-foreground">
        No upcoming meetings. Schedule one to get started!
      </div>
    {:else}
      <div class="space-y-3">
        {#each meetings as meeting}
          <div class="p-4 bg-primary/5 rounded-lg border border-border">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-medium text-primary">{meeting.title}</h3>
                <p class="text-sm text-muted-foreground mt-1">
                  {formatDate(meeting.scheduled_time)}
                </p>
                <p class="text-sm text-muted-foreground">
                  Duration: {meeting.duration_minutes} min
                </p>
              </div>
              <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(meeting.status)}">
                {meeting.status}
              </span>
            </div>
            
            <!-- Attendees -->
            <div class="mt-2 flex flex-wrap gap-1">
              {#each meeting.attendees as attendeeId}
                {#each agents as agent}
                  {#if agent.id === attendeeId}
                    <span class="px-2 py-0.5 bg-primary/10 rounded text-xs">
                      {agent.name}
                    </span>
                  {/if}
                {/each}
              {/each}
            </div>
            
            <!-- Agenda -->
            {#if meeting.agenda && meeting.agenda.length > 0}
              <div class="mt-2">
                <p class="text-xs text-muted-foreground">Agenda:</p>
                <ul class="text-xs text-muted-foreground list-disc list-inside">
                  {#each meeting.agenda as item}
                    <li>{item}</li>
                  {/each}
                </ul>
              </div>
            {/if}
            
            <!-- Recurrence -->
            {#if meeting.recurrence}
              <div class="mt-2">
                <span class="px-2 py-0.5 bg-purple-500/20 text-purple-600 rounded text-xs">
                  Recurring
                </span>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>