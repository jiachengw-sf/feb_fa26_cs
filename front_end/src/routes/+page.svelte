<script lang="ts">
  import { onMount } from 'svelte';

  let runs: { id: number; filename: string; uploaded_at: string }[] = $state([]);

  onMount(async () => {
    const res = await fetch('http://127.0.0.1:8000/runs');
    runs = await res.json();
  });
</script>

<h1>Telemetry Runs</h1>

<ul>
  {#each runs as run}
    <li><a href="/runs/{run.id}">{run.filename} — uploaded {run.uploaded_at}</a></li>
  {/each}
</ul>