<template>
  <div class="bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark font-sans h-screen flex flex-col md:flex-row overflow-hidden transition-colors duration-200">
    <!-- Mobile Header with Nav Toggle -->
    <header class="md:hidden flex items-center justify-between p-4 border-b border-border-light dark:border-border-dark bg-card-light dark:bg-card-dark shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-emerald-300 flex items-center justify-center text-white font-bold text-xs shadow-md">
          H2P
        </div>
        <span class="font-semibold text-gray-900 dark:text-white">HTML to PPT</span>
      </div>
      <button
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        @click="isMobileNavOpen = !isMobileNavOpen"
        :aria-expanded="isMobileNavOpen"
        aria-label="Toggle navigation menu"
      >
        <span class="material-symbols-rounded text-2xl text-gray-600 dark:text-gray-300">
          {{ isMobileNavOpen ? 'close' : 'menu' }}
        </span>
      </button>
    </header>

    <!-- Mobile Navigation Drawer -->
    <Transition name="slide">
      <nav
        v-if="isMobileNavOpen"
        class="md:hidden absolute top-[65px] left-0 right-0 bottom-0 bg-card-light dark:bg-card-dark border-b border-border-light dark:border-border-dark z-50 p-4"
        aria-label="Mobile navigation"
      >
        <div class="flex flex-col gap-2">
          <NuxtLink
            to="/"
            class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            :class="{ 'bg-primary/10 text-primary': $route.path === '/' }"
            @click="isMobileNavOpen = false"
          >
            <span class="material-symbols-rounded text-xl">grid_view</span>
            <span class="font-medium">Workspace</span>
          </NuxtLink>
          <NuxtLink
            to="/history"
            class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            :class="{ 'bg-primary/10 text-primary': $route.path === '/history' }"
            @click="isMobileNavOpen = false"
          >
            <span class="material-symbols-rounded text-xl">history</span>
            <span class="font-medium">History</span>
          </NuxtLink>
          <NuxtLink
            to="/settings"
            class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            :class="{ 'bg-primary/10 text-primary': $route.path === '/settings' }"
            @click="isMobileNavOpen = false"
          >
            <span class="material-symbols-rounded text-xl">settings</span>
            <span class="font-medium">Settings</span>
          </NuxtLink>
        </div>
      </nav>
    </Transition>

    <!-- Desktop Side Navigation -->
    <SideNav class="hidden md:flex" />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col md:flex-row overflow-hidden">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const isMobileNavOpen = ref(false);
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
