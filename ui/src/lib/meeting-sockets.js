import { socket } from "./api";
import { agentPresence, meetingMessages, roomState, meetings, invitations } from "./store";
import { toast } from "svelte-sonner";
import { get } from "svelte/store";

let prevSpeakingAgent = null;

export function initializeMeetingSockets() {
  socket.connect();
  
  // Connection
  socket.emit("meeting-connect", { data: "meeting frontend connected!" });
  
  // ============ Presence Events ============
  
  // Agent presence update
  socket.on("agent-presence", function (data) {
    agentPresence.update(presence => {
      const index = presence.findIndex(p => p.agent_id === data.agent_id);
      if (index >= 0) {
        presence[index] = data;
      } else {
        presence.push(data);
      }
      return presence;
    });
  });
  
  // Agent joined room
  socket.on("agent-joined", function (data) {
    agentPresence.update(presence => {
      const index = presence.findIndex(p => p.agent_id === data.agent_id);
      if (index >= 0) {
        presence[index] = data.presence;
      } else {
        presence.push(data.presence);
      }
      return presence;
    });
    
    roomState.update(state => ({
      ...state,
      ...data.room_state
    }));
    
    toast.success(`${data.presence.agent_name} joined the room`);
  });
  
  // Agent left room
  socket.on("agent-left", function (data) {
    agentPresence.update(presence => {
      const index = presence.findIndex(p => p.agent_id === data.agent_id);
      if (index >= 0) {
        presence[index].status = 'offline';
      }
      return presence;
    });
    
    roomState.update(state => ({
      ...state,
      ...data.room_state
    }));
  });
  
  // Agent typing indicator
  socket.on("agent-typing", function (data) {
    // This is handled by individual components
  });
  
  // ============ Message Events ============
  
  // Agent speaking (new message)
  socket.on("agent-speaking", function (data) {
    meetingMessages.update(msgs => [...msgs, data.message]);
    
    // Show toast for new message
    if (data.message.agent_id !== 'user') {
      toast(`${data.message.agent_name}: ${data.message.content.substring(0, 50)}...`);
    }
  });
  
  // ============ Meeting Events ============
  
  // Meeting started
  socket.on("meeting-started", function (data) {
    roomState.update(state => ({
      ...state,
      active_meeting_id: data.meeting.meeting_id
    }));
    
    meetings.update(meetings => {
      const index = meetings.findIndex(m => m.meeting_id === data.meeting.meeting_id);
      if (index >= 0) {
        meetings[index] = data.meeting;
      }
      return meetings;
    });
    
    toast.success(`Meeting "${data.meeting.title}" has started!`);
  });
  
  // Meeting ended
  socket.on("meeting-ended", function (data) {
    roomState.update(state => ({
      ...state,
      active_meeting_id: null
    }));
    
    meetings.update(meetings => {
      const index = meetings.findIndex(m => m.meeting_id === data.meeting.meeting_id);
      if (index >= 0) {
        meetings[index] = data.meeting;
      }
      return meetings;
    });
    
    toast.info(`Meeting "${data.meeting.title}" has ended`);
  });
  
  // Meeting created
  socket.on("meeting-created", function (data) {
    meetings.update(meetings => [data.meeting, ...meetings]);
  });
  
  // Meeting list response
  socket.on("meeting-list-response", function (data) {
    meetings.set(data.meetings || []);
  });
  
  // ============ Invitation Events ============
  
  // Invitation received
  socket.on("invitation-received", function (data) {
    invitations.update(invs => ({
      ...invs,
      received: [data, ...(invs.received || [])]
    }));
    
    toast.info(`New invitation from ${data.from_agent}`);
  });
  
  // Invitation list response
  socket.on("invitation-list-response", function (data) {
    invitations.set({
      sent: data.sent || [],
      received: data.received || []
    });
  });
  
  // Invitation updated
  socket.on("invitation-updated", function (data) {
    invitations.update(invs => ({
      ...invs,
      sent: invs.sent.map(inv => 
        inv.invitation_id === data.invitation_id ? data : inv
      )
    }));
  });
  
  // ============ Room State Events ============
  
  // Initial room state
  socket.on("room-state", function (data) {
    roomState.set(data);
  });
  
  // Initial presence
  socket.on("initial-presence", function (data) {
    agentPresence.set(data);
  });
}

export function destroyMeetingSockets() {
  if (socket.connected) {
    socket.off("agent-presence");
    socket.off("agent-joined");
    socket.off("agent-left");
    socket.off("agent-typing");
    socket.off("agent-speaking");
    socket.off("meeting-started");
    socket.off("meeting-ended");
    socket.off("meeting-created");
    socket.off("meeting-list-response");
    socket.off("invitation-received");
    socket.off("invitation-list-response");
    socket.off("invitation-updated");
    socket.off("room-state");
    socket.off("initial-presence");
  }
}

export function emitMeetingEvent(channel, message) {
  socket.emit(channel, message);
}

export function socketMeetingListener(channel, callback) {
  socket.on(channel, callback);
}