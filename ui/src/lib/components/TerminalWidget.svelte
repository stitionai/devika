<script>
  import { onMount } from "svelte";
  import "xterm/css/xterm.css";
  import { agentState } from "$lib/store";

  let terminalElement;
  let terminal;
  let fitAddon;
  // agentState.subscribe((value) => {
  //   $agentState = value;
  // });

  onMount(async () => {
    let xterm = await import('xterm');
    let xtermAddonFit = await import('xterm-addon-fit')

    const terminalBg = getComputedStyle(document.body).getPropertyValue('--terminal-window-background');
    const terminalFg = getComputedStyle(document.body).getPropertyValue('--terminal-window-foreground');

    terminal = new xterm.Terminal({
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
    fitAddon = new xtermAddonFit.FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(terminalElement);
    fitAddon.fit();

    let previousState = {};

    agentState.subscribe((state) => {
      if (state && state.terminal_session) {
        let command = state.terminal_session.command || 'echo "Waiting..."';
        let output = state.terminal_session.output || "Waiting...";
        let title = state.terminal_session.title || "Terminal";

        // Check if the current state is different from the previous state
        if (
          command !== previousState.command ||
          output !== previousState.output ||
          title !== previousState.title
        ) {
          addCommandAndOutput(command, output, title);

          // Update the previous state
          previousState = { command, output, title };
        }
      }
      else {
        // Reset the terminal
        terminal.reset();
      }

      fitAddon.fit();
    });
  });

  function addCommandAndOutput(command, output, title) {
    if (title) {
      document.getElementById("terminal-title").innerText = title;
    }
    terminal.reset();
    terminal.write(`$ ${command}\r\n\r\n${output}\r\n`);
  }
</script>

<div class="w-full h-full flex flex-col border-[4px] overflow-hidden rounded-3xl border-window-outline">
  <div class="flex items-center p-2 py-3 border-b bg-terminal-window-ribbon">
    <div class="flex ml-2 mr-4 space-x-2">
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
    </div>
    <span id="terminal-title" class="text-tertiary">Terminal</span>
  </div>
  <div
    id="terminal-content"
    class="w-full h-full rounded-bl-lg bg-terminal-window-background"
    bind:this={terminalElement}
  ></div>
</div>

<style>
  #terminal-content :global(.xterm) {
    padding: 10px;
    height: 100%; /* Ensure terminal content height is fixed */
  }

  #terminal-content :global(.xterm-viewport) {
    overflow-y: auto !important;
    height: 100%;
  }
  
</style>
