<template>
  <div class="layout-root">
    <SideNav />
    <main class="layout-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.layout-root {
  display: flex;
  min-height: 100vh;
}

.layout-content {
  flex: 1;
  margin-left: 240px;
  padding: 32px 40px;
  max-width: 1600px;
  width: 100%;
}

@media (max-width: 1024px) {
  .layout-content {
    padding: 24px;
  }
}
</style>