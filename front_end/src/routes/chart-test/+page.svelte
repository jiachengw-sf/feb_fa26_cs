<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  let canvasEl: HTMLCanvasElement;

  onMount(async () => {
    const res = await fetch('http://127.0.0.1:8000/runs/4/signals?signal_name=bms_state');
    const data: { timestamp_ms: number; value: number; physical_value: string }[] = await res.json();

    new Chart(canvasEl, {
      type: 'line',
      data: {
        labels: data.map(d => d.timestamp_ms),
        datasets: [{
          label: 'bms_state',
          data: data.map(d => d.value)
        }]
      }
    });
  });
</script>

<h1>Chart Test</h1>
<div style="width: 800px; height: 400px;">
  <canvas bind:this={canvasEl}></canvas>
</div>