import { socket } from "./api";
import { messages, agentState, isSending, tokenUsage } from "./store";
import { toast } from "svelte-sonner";
import { get } from "svelte/store";

let prevMonologue = null;

export function initializeSockets() {

  socket.connect();
  
  let state = get(agentState);
  prevMonologue = state?.internal_monologue;

  socket.emit("socket_connect", { data: "frontend connected!" });
  socket.on("socket_response", function (msg) {
    console.log(msg);
  });

  socket.on("server-message", function (data) {
    console.log(data)
    messages.update((msgs) => [...msgs, data["messages"]]);
  });

  socket.on("agent-state", function (state) {
    const lastState = state[state.length - 1];
    agentState.set(lastState);
    if (lastState.completed) {
      isSending.set(false);
    }
  });

  socket.on("tokens", function (tokens) {
    tokenUsage.set(tokens["token_usage"]);
  });

  socket.on("inference", function (error) {
    if (error["type"] == "error") {
      toast.error(error["message"]);
      isSending.set(false);
    } else if (error["type"] == "warning") {
      toast.warning(error["message"]);
    }
  });

  socket.on("info", function (info) {
    if (info["type"] == "error") {
      toast.error(info["message"]);
      isSending.set(false);
    } else if (info["type"] == "warning") {
      toast.warning(info["message"]);
    } else if (info["type"] == "info") {
      toast.info(info["message"]);
    }
  });

  
  agentState.subscribe((state) => {
    function handleMonologueChange(newValue) {
      if (newValue) {
        toast(newValue);
      }
    }
    if (
      state &&
      state.internal_monologue &&
      state.internal_monologue !== prevMonologue
    ) {
      handleMonologueChange(state.internal_monologue);
      prevMonologue = state.internal_monologue;
    }
  });
}

export function destroySockets() {
  if (socket.connected) {
    socket.off("socket_response");
    socket.off("server-message");
    socket.off("agent-state");
    socket.off("tokens");
    socket.off("inference");
    socket.off("info");
  }
}

export function emitMessage(channel, message) {
  socket.emit(channel, message);
}

export function socketListener(channel, callback) {
  socket.on(channel, callback);
}
