<div
  class="flex flex-col w-20 h-dvh fixed top-0 left-0 z-10 bg-slate-950 p-4 space-y-4 items-center shadow-2xl shadow-indigo-700"
>
  <div class="p-5 rounded nav-button relative">
    <a href="/">
    <button class="text-gray-400 hover:text-white flex justify-center w-full">
      <i class="fas fa-home fa-lg"></i>
    </button>
  </a>
    <span class="tooltip">Home</span>
  </div>
  <div class="p-5 rounded nav-button relative">
    <a href="/settings">
      <button class="text-gray-400 hover:text-white flex justify-center w-full">
        <i class="fas fa-cog fa-lg"></i>
      </button>
    </a>
    <span class="tooltip">Settings</span> 
  </div>
  <div class="p-5 rounded nav-button relative">
    <button class="text-gray-400 hover:text-white flex justify-center w-full">
      <i class="fas fa-history fa-lg"></i>
    </button>
    <span class="tooltip">Logs</span>
  </div>
</div>

<style>
  .tooltip {
    visibility: hidden;
    width: 120px;
    background-color: #10172a;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px 0;
    position: absolute;
    z-index: 1;
    top: 50%;
    left: 150%;
    transform: translateY(-50%);
    opacity: 0;
    transition: opacity 0.3s;
  }

  .nav-button:hover .tooltip {
    visibility: visible;
    opacity: 1;
  }
</style>
