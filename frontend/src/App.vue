<script setup lang="ts">
// Main layout just hosts the router view
</script>

<template>
  <router-view></router-view>
</template>

<style>
/* Global Resets */
:root {
  --primary: #00e5ff;
  --bg-dark: #121212;
  --bg-darker: #0a0a0a;
  --text-primary: #ffffff;
  --text-secondary: #a0aec0;
}

body, html {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: var(--bg-dark);
  color: var(--text-primary);
  overflow: hidden;
}

#app {
  width: 100%;
  height: 100%;
}
</style>
