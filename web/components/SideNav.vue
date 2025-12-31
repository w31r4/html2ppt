<template>
  <nav class="w-16 flex flex-col items-center py-6 border-r border-border-light dark:border-border-dark bg-card-light dark:bg-card-dark shrink-0 z-20">
    <div class="mb-8">
      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-emerald-300 flex items-center justify-center text-white font-bold text-xs shadow-md">
        H2P
      </div>
    </div>
    <div class="flex flex-col gap-6 flex-1 w-full items-center">
      <NuxtLink to="/" class="icon-btn" active-class="text-primary bg-primary/10">
        <span class="material-icons-outlined text-2xl">grid_view</span>
      </NuxtLink>
      <NuxtLink to="/history" class="icon-btn" active-class="text-primary bg-primary/10">
        <span class="material-icons-outlined text-2xl">history</span>
      </NuxtLink>
      <NuxtLink to="/settings" class="icon-btn" active-class="text-primary bg-primary/10">
        <span class="material-icons-outlined text-2xl">settings</span>
      </NuxtLink>
    </div>
    <div class="mt-auto">
      <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm">
        U
      </div>
    </div>
  </nav>
</template>
