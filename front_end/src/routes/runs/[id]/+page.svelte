<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  let runId = $page.params.id;
  let availableSignals: string[] = $state([]);
  let selectedSignal = $state('');
  let canvasEl: HTMLCanvasElement;
  let chart: Chart | null = null;
  let stats: { min: number; max: number; mean: number; std: number; count: number } | null = $state(null);
  let anomalyCount: number = $state(0);

  onMount(async () => {
    const res = await fetch(`http://127.0.0.1:8000/runs/${runId}/signals`);
    const result = await res.json();
    availableSignals = result.available_signals;
  });

  async function loadSignal() {
    if (!selectedSignal) return;

    const [dataRes, statsRes, anomalyRes] = await Promise.all([
      fetch(`http://127.0.0.1:8000/runs/${runId}/signals?signal_name=${selectedSignal}`),
      fetch(`http://127.0.0.1:8000/runs/${runId}/signals/${selectedSignal}/stats`),
      fetch(`http://127.0.0.1:8000/runs/${runId}/signals/${selectedSignal}/anomalies`)
    ]);

    const data: { timestamp_ms: number; value: number }[] = await dataRes.json();
    stats = await statsRes.json();
    const anomalyResult = await anomalyRes.json();
    anomalyCount = anomalyResult.anomaly_count ?? 0;

    if (chart) chart.destroy();

    chart = new Chart(canvasEl, {
      type: 'line',
      data: {
        labels: data.map(d => d.timestamp_ms),
        datasets: [{ label: selectedSignal, data: data.map(d => d.value) }]
      }
    });
  }
</script>

<h1>Run #{runId}</h1>

<select bind:value={selectedSignal} onchange={loadSignal}>
  <option value="">Choose a signal...</option>
  {#each availableSignals as signal}
    <option value={signal}>{signal}</option>
  {/each}
</select>

<div style="width: 800px; height: 400px;">
  <canvas bind:this={canvasEl}></canvas>
</div>

{#if stats}
  <div style="margin-top: 1rem;">
    <p><strong>Stats:</strong> min {stats.min}, max {stats.max}, mean {stats.mean}, std {stats.std} ({stats.count} readings)</p>
    <p><strong>Anomalies detected:</strong> {anomalyCount} points beyond 2 standard deviations from the mean</p>
  </div>
{/if}