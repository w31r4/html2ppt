<template>
  <nav class="w-16 flex flex-col items-center py-6 border-r border-border-light dark:border-border-dark bg-card-light dark:bg-card-dark shrink-0 z-20" aria-label="Main navigation">
    <div class="mb-8">
      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-emerald-300 flex items-center justify-center text-white font-bold text-xs shadow-md" aria-label="HTML to PPT">
        H2P
      </div>
    </div>
    <div class="flex flex-col gap-6 flex-1 w-full items-center" role="list">
      <NuxtLink to="/" class="icon-btn" active-class="text-primary bg-primary/10" aria-label="Workspace" title="Workspace">
        <span class="material-icons-outlined text-2xl" aria-hidden="true">grid_view</span>
      </NuxtLink>
      <NuxtLink to="/history" class="icon-btn" active-class="text-primary bg-primary/10" aria-label="History" title="History">
        <span class="material-icons-outlined text-2xl" aria-hidden="true">history</span>
      </NuxtLink>
      <NuxtLink to="/settings" class="icon-btn" active-class="text-primary bg-primary/10" aria-label="Settings" title="Settings">
        <span class="material-icons-outlined text-2xl" aria-hidden="true">settings</span>
      </NuxtLink>
    </div>
    <div class="mt-auto">
      <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm" aria-label="User profile" role="img">
        U
      </div>
    </div>
  </nav>
</template>
