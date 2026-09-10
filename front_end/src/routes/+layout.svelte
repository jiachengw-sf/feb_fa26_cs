<script lang="ts">
  let { children } = $props();
</script>

<nav>
  <a href="/">Home</a>
  <a href="/upload">Upload</a>
</nav>

<main>
  {@render children()}
</main>

<style>
  nav {
    display: flex;
    gap: 1.5rem;
    padding: 1rem;
    border-bottom: 1px solid #ccc;
    margin-bottom: 1.5rem;
  }

  nav a {
    text-decoration: none;
    font-weight: 600;
    color: #333;
  }

  nav a:hover {
    text-decoration: underline;
  }
</style>