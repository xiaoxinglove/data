<script setup>
const areas = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/knowledge', label: 'Knowledge' },
  { to: '/workflow', label: 'Workflow' },
  { to: '/evaluation', label: 'Evaluation' },
]
</script>

<template>
  <div class="layout">
    <nav>
      <RouterLink v-for="area in areas" :key="area.to" :to="area.to">
        {{ area.label }}
      </RouterLink>
    </nav>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style>
:root {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #1f2933;
}
body {
  margin: 0;
}
.layout {
  display: flex;
  min-height: 100vh;
}
nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  min-width: 160px;
  border-right: 1px solid #e4e7eb;
}
nav a {
  color: #52606d;
  text-decoration: none;
}
nav a.router-link-active {
  color: #1f2933;
  font-weight: 600;
}
main {
  padding: 24px;
}
</style>
