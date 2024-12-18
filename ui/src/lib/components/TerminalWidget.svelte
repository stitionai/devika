<script>
  import { onMount } from "svelte";
  import { Terminal } from "@xterm/xterm";
  import { FitAddon } from "@xterm/addon-fit";
  import { agentState } from "$lib/store";
  import "@xterm/xterm/css/xterm.css";

  onMount(async () => {
    const terminalBg = getComputedStyle(document.body).getPropertyValue(
      "--terminal-window-background"
    );
    const terminalFg = getComputedStyle(document.body).getPropertyValue(
      "--terminal-window-foreground"
    );

    const terminal = new Terminal({
      disableStdin: true,
      cursorBlink: true,
      convertEol: true,
      rows: 1,
      theme: {
        background: terminalBg,
        foreground: terminalFg,
        innerText: terminalFg,
        cursor: terminalFg,
        selectionForeground: terminalBg,
        selectionBackground: terminalFg
      },
    });
    const fitAddon = new FitAddon();

    terminal.loadAddon(fitAddon);
    terminal.open(document.getElementById("terminal-content"));

    fitAddon.fit();

    let previousState = {};

    agentState.subscribe((state) => {
      if (state && state.terminal_session) {
        let command = state.terminal_session.command || 'echo "Waiting..."';
        let output = state.terminal_session.output || "Waiting...";
        let title = state.terminal_session.title || "Terminal";

        if (
          command !== previousState.command ||
          output !== previousState.output ||
          title !== previousState.title
        ) {
          if (title) {
            document.getElementById("terminal-title").innerText = title;
          }
          terminal.reset();
          terminal.write(`$ ${command}\r\n\r\n${output}\r\n`);
          previousState = { command, output, title };
        }
      } else {
        terminal.reset();
      }

      fitAddon.fit();
    });
  });
</script>

<div
  class="w-full h-full flex flex-col border-[3px] overflow-hidden rounded-xl border-window-outline"
>
  <div class="flex items-center p-2 border-b bg-terminal-window-ribbon">
    <div class="flex ml-2 mr-4 space-x-2">
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
    </div>
    <span id="terminal-title" class="text-tertiary text-sm truncate">Terminal</span>
  </div>
  <div
    id="terminal-content"
    class="w-full h-full rounded-bl-lg bg-terminal-window-background overflow-x-auto"
  ></div>
</div>

<style>
  #terminal-content :global(.xterm) {
    padding: 10px;
    max-width: 100%;
  }
  #terminal-content :global(.xterm-screen) {
    width: 100% !important;
    max-width: 100vw;
  }
  #terminal-content :global(.xterm-rows) {
    width: 100% !important;
    height: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
  }
</style>
