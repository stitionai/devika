<script>
  import { onMount, onDestroy } from "svelte";
  import { toast } from "svelte-sonner";
  
  import MeetingRoom from "$lib/components/MeetingRoom.svelte";
  import MeetingScheduler from "$lib/components/MeetingScheduler.svelte";
  import InvitationPanel from "$lib/components/InvitationPanel.svelte";
  import * as Tabs from "$lib/components/ui/tabs/index.js";
  
  import { serverStatus } from "$lib/store";
  import { initializeMeetingSockets, destroyMeetingSockets } from "$lib/meeting-sockets";
  import { checkServerStatus } from "$lib/api";
  
  let activeTab = "room";
  let isConnected = false;
  
  onMount(async () => {
    if (!(await checkServerStatus())) {
      toast.error("Failed to connect to server");
      return;
    }
    serverStatus.set(true);
    isConnected = true;
    await initializeMeetingSockets();
  });
  
  onDestroy(() => {
    destroyMeetingSockets();
  });
</script>

<div class="flex h-full flex-col flex-1 gap-4 p-4 overflow-hidden">
  <div class="flex items-center justify-between">
    <h1 class="text-2xl font-bold text-primary">Agent Meeting Room</h1>
    <div class="flex items-center gap-2">
      <span class="text-sm text-muted-foreground">
        {isConnected ? "Connected" : "Connecting..."}
      </span>
      <div class="w-2 h-2 rounded-full {isConnected ? 'bg-green-500' : 'bg-yellow-500'}"></div>
    </div>
  </div>
  
  <Tabs.Root value={activeTab} onValueChange={(e) => activeTab = e.value}>
    <Tabs.List class="grid w-full grid-cols-3">
      <Tabs.Trigger value="room">Meeting Room</Tabs.Trigger>
      <Tabs.Trigger value="schedule">Schedule</Tabs.Trigger>
      <Tabs.Trigger value="invitations">Invitations</Tabs.Trigger>
    </Tabs.List>
    
    <Tabs.Content value="room" class="flex-1 overflow-hidden">
      <MeetingRoom />
    </Tabs.Content>
    
    <Tabs.Content value="schedule" class="flex-1 overflow-hidden">
      <MeetingScheduler />
    </Tabs.Content>
    
    <Tabs.Content value="invitations" class="flex-1 overflow-hidden">
      <InvitationPanel />
    </Tabs.Content>
  </Tabs.Root>
</div>