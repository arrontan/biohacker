import React, { useState, useEffect } from 'react';

export default function Sidebar({ onUpload }: { onUpload?: (info: any) => void }) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [uploads, setUploads] = useState<Array<{filename:string,path:string}>>([]);

  async function handleUpload() {
    if (!file) { setStatus('No file selected'); return; }
    setStatus('Uploading...');
    const fd = new FormData();
    fd.append('file', file);
    try {
  // use same-origin proxy path; Next dev server rewrites /api/upload to the
  // backend at http://127.0.0.1:3001/upload. This avoids CORS and mixed-content.
  const url = '/api/upload';
  const res = await fetch(url, { method: 'POST', body: fd });
      const data = await res.json();
      if (res.ok) {
        setStatus('Uploaded: ' + data.filename);
        if (onUpload) onUpload(data);
        // refresh uploads list after a successful upload
        fetchUploads();
      } else {
        setStatus('Upload error: ' + (data && data.error));
        console.warn('upload error details', { url, status: res.status, body: data });
      }
    } catch (e) {
      // show fuller error info in console to help diagnose network/CORS/mixed-content
      console.error('upload failed', e);
      setStatus('Upload failed: ' + (e && e.message));
    }
  }

  useEffect(() => {
    // fetch list on mount
    fetchUploads();
  }, []);

  async function fetchUploads() {
    try {
      const res = await fetch('/api/uploads');
      if (!res.ok) throw new Error('failed to fetch uploads: ' + res.status);
      const data = await res.json();
      setUploads(data.files || []);
    } catch (e) {
      console.error('fetchUploads failed', e);
      setStatus('Failed to fetch uploads: ' + (e && e.message));
    }
  }

  return (
    <div style={{ position: 'fixed', right: open ? 0 : -320, top: 80, width: 320, height: '70vh', background: '#f6f6f6', borderLeft: '1px solid #ddd', padding: 12, transition: 'right 240ms ease' }}>
      <button onClick={() => setOpen(!open)} style={{ position: 'absolute', left: -40, top: 10, width: 36, height: 36 }}>{open ? '⟨' : '⟩'}</button>
      <h3>Uploads</h3>
      <input type="file" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} />
      <div style={{ marginTop: 8 }}>
        <button onClick={handleUpload}>Upload</button>
        <button onClick={fetchUploads} style={{ marginLeft: 8 }}>Refresh</button>
      </div>
      <div style={{ marginTop: 10 }}>
        <strong>Files:</strong>
        <div style={{ maxHeight: 160, overflow: 'auto', marginTop: 6, fontSize: 13 }}>
          {uploads.length === 0 ? <div style={{ color: '#666' }}>No files</div> : uploads.map(u => (
            <div key={u.filename} style={{ marginBottom: 6 }}>
              <a href={u.path} target="_blank" rel="noreferrer">{u.filename}</a>
            </div>
          ))}
        </div>
      </div>
      {status && <div style={{ marginTop: 8, fontSize: 13 }}>{status}</div>}
    </div>
  );
}
