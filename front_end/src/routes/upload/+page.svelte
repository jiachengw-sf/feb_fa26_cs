<script lang="ts">
  let selectedFile: File | null = $state(null);
  let uploadResult: { filename: string; run_id: number; rows_inserted: number } | null = $state(null);
  let uploading = $state(false);

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    selectedFile = input.files?.[0] ?? null;
    console.log('File selected:', selectedFile);
  }

  async function handleUpload() {
    if (!selectedFile) return;

    uploading = true;
    const formData = new FormData();
    formData.append('file', selectedFile);

    const res = await fetch('http://127.0.0.1:8000/upload', {
      method: 'POST',
      body: formData
    });
    uploadResult = await res.json();
    uploading = false;
  }
</script>

<h1>Upload Telemetry CSV</h1>

<input type="file" accept=".csv" onchange={handleFileChange} />
<button onclick={handleUpload} disabled={!selectedFile || uploading}>
  {uploading ? 'Uploading...' : 'Upload'}
</button>

{#if uploadResult}
  <p>Uploaded {uploadResult.filename} — {uploadResult.rows_inserted} rows inserted (run #{uploadResult.run_id})</p>
{/if}