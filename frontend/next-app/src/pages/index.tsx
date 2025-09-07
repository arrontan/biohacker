import React from 'react';
import dynamic from 'next/dynamic';

// load xterm component dynamically to avoid SSR issues
const Terminal = dynamic(() => import('../components/Terminal'), { ssr: false });

export default function Home() {
  return (
    <div style={{ padding: 16 }}>
      <h1>Biohacker Terminal</h1>
      <p>Connects to the backend PTY server and proxies the project's CLI.</p>
      <div style={{ border: '1px solid #ddd', borderRadius: 6, padding: 8 }}>
        <Terminal />
      </div>
    </div>
  );
}
