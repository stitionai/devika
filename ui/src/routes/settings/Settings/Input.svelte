<script lang="ts">
  export let type = "text";
  export let value = type === "text" ? "" : null;
  export let error = "";
  export let label = "";
  export let placeholder = "";

  function handleInput({ target: t }) {
    if (type === "number") {
      value = t.value === "" ? null : t.valueAsNumber;
    } else {
      value = t.value;
    }
  }
</script>

<label class="block">
  {#if label}
    <span class="block mb-1">{label}</span>
  {/if}
  <input
    class="block input"
    class:error
    {type}
    {placeholder}
    {value}
    on:input={handleInput}
    on:input
    on:blur
  />
  {#if error}
    <span class="block error-text">{error}</span>
  {/if}
</label>

<style>
  .input {
    border-radius: 4px;
    padding: 6px 10px;
    margin: 0;
    color: black;
    width: 100%;
  }

  .block {
    display: block;
  }

  .error {
    border-color: #f55;
  }

  .error-text {
    margin-top: 4px;
    color: #f55;
  }
</style>
