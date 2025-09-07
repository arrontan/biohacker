import React, { useState, useEffect } from 'react';

export default function Sidebar({ onUpload }: { onUpload?: (info: any) => void }) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [uploads, setUploads] = useState<Array<{filename:string,path:string}>>([]);

  async function fetchUploads() {
    try {
      const res = await fetch('/api/uploads');
      if (!res.ok) throw new Error('failed to fetch uploads: ' + res.status);
      const data = await res.json();
      setUploads(data.files || []);
    } catch (e: any) {
      console.error('fetchUploads failed', e);
      setStatus('Failed to fetch uploads: ' + (e && e.message));
    }
  }

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
    } catch (e: any) {
      console.error('upload failed', e);
      setStatus('Upload failed: ' + (e && e.message));
    }
  }

  useEffect(() => {
    fetchUploads();
  }, []);

  return (
    <div className={`sidebar ${open ? 'open' : ''}`}>
      <button className="sidebar-toggle" onClick={() => setOpen(!open)} aria-label="Toggle uploads panel">{open ? '\u27e8' : '\u27e9'}</button>
      <h3 className="sidebar-title">Uploads</h3>
      <label className="file-input-label">
        <input className="file-input" type="file" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} />
      </label>
      <div className="sidebar-actions">
        <button onClick={handleUpload} className="btn">Upload</button>
        <button onClick={fetchUploads} className="btn btn-ghost">Refresh</button>
      </div>

      <div className="sidebar-files">
        <strong>Files:</strong>
        <div className="files-list">
          {uploads.length === 0 ? <div className="no-files">No files</div> : uploads.map(u => (
            <div key={u.filename} className="file-row">
              <a href={u.path} target="_blank" rel="noreferrer">{u.filename}</a>
            </div>
          ))}
        </div>
      </div>
      {status && <div className="sidebar-status">{status}</div>}
    </div>
  );
}
