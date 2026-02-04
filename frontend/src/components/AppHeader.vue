<template>
  <header class="app-header">
    <div class="header-top">
      <h1>Literary Essays</h1>
      <nav class="header-nav">
        <router-link to="/">Home</router-link>
        <router-link to="/about">How It Works</router-link>
        <router-link to="/cost">Hosting Cost</router-link>
      </nav>
    </div>
    <p>Search Project Gutenberg, generate theme-based literary analysis with AI.</p>
  </header>
</template>

<style scoped>
.app-header {
  padding: 32px 24px 8px;
  color: #f7f3ec;
}
.header-top {
  display: flex;
  align-items: baseline;
  gap: 24px;
  flex-wrap: wrap;
}
.app-header h1 {
  margin: 0 0 8px;
  font-family: "Fraunces", serif;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.header-nav {
  display: flex;
  gap: 16px;
}
.header-nav a {
  color: #d6d1c5;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s;
}
.header-nav a:hover,
.header-nav a.router-link-exact-active {
  color: var(--accent-2);
}
.app-header p {
  margin: 0;
  color: #d6d1c5;
}
</style>
