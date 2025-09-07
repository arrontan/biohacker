import React from 'react';
import dynamic from 'next/dynamic';
import Sidebar from '../components/Sidebar';

// load xterm component dynamically to avoid SSR issues
const Terminal = dynamic(() => import('../components/Terminal'), { ssr: false });

export default function Home() {
  return (
    <div className="app-wrapper">
      <header className="app-header">
        <span className="emoji" role="img" aria-label="dna">🧬</span>
        <span className="brand">biohacker</span>
      </header>

      <p className="subtitle">a project by Arron and Madhu</p>

      <div className="terminal-card">
        <Terminal />
      </div>

      <Sidebar onUpload={(info) => { console.log('uploaded', info); }} />
    </div>
  );
}
