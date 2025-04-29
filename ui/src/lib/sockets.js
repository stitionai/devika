import { socket } from "./api";
import { messages, agentState, isSending, tokenUsage } from "./store";
import { toast } from "svelte-sonner";
import { get } from "svelte/store";

let prevMonologue = null;

/**
 * Initializes socket connections and event listeners for handling various server responses.
 *
 * This function sets up the initial connection to the server and defines several event handlers
 * to manage different types of messages received from the server, such as agent state updates,
 * token usage notifications, inference errors, information messages, and internal monologue changes.
 */
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
    /**
     * Handles the change event of a monologue by displaying a toast notification.
     *
     * @function handleMonologueChange
     * @param {string} newValue - The new value of the monologue that triggered the change event.
     */
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

/**
 * Removes event listeners from the socket if it is connected.
 *
 * This function checks if the socket is currently connected and then
 * removes all relevant event listeners to prevent memory leaks or unexpected
 * behavior when the socket connection is closed or reused.
 */
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

/**
 * Emits a message to a specified channel using a socket connection.
 *
 * @param {string} channel - The name of the channel to which the message will be sent.
 * @param {*} message - The message data to send. Can be any type that is serializable by the socket library.
 */
export function emitMessage(channel, message) {
  socket.emit(channel, message);
}

/**
 * Registers an event listener on a specified socket channel.
 *
 * @param {string} channel - The name of the channel to listen for events on.
 * @param {Function} callback - The function to be called when an event is received on the specified channel.
 *   This callback function should accept any arguments that are sent with the event from the server.
 *
 * @example
 * // Example usage:
 * socketListener('message', (data) => {
 *   console.log('Received message:', data);
 * });
 */
export function socketListener(channel, callback) {
  socket.on(channel, callback);
}
