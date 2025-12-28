'use client';

import { useEffect, useState } from 'react';

interface ApiStatus {
  api: string;
  message: string;
  environment: string;
}

export default function Home() {
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApiStatus = async (): Promise<void> => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/status`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = (await response.json()) as ApiStatus;
        setApiStatus(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch API status');
        setApiStatus(null);
      } finally {
        setLoading(false);
      }
    };

    fetchApiStatus();
  }, []);

  return (
    <div className="container">
      <h1>Minecraft Server Dashboard</h1>

      <div className="card">
        <h2>Frontend Status</h2>
        <p>
          Status: <span className="status online">Online</span>
        </p>
        <p>Next.js 15 + React 19 + TypeScript</p>
      </div>

      <div className="card">
        <h2>Backend API Status</h2>
        {loading && <p>Loading...</p>}
        {error && (
          <div>
            <p>
              Status: <span className="status offline">Offline</span>
            </p>
            <p>Error: {error}</p>
          </div>
        )}
        {apiStatus && (
          <div>
            <p>
              Status:{' '}
              <span className={`status ${apiStatus.api === 'online' ? 'online' : 'offline'}`}>
                {apiStatus.api}
              </span>
            </p>
            <p>Message: {apiStatus.message}</p>
            <p>Environment: {apiStatus.environment}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h2>Development Environment</h2>
        <p>This is a minimal implementation for Docker and CI verification.</p>
        <ul>
          <li>Frontend: Next.js 15 with App Router</li>
          <li>Backend: FastAPI with Python 3.13</li>
          <li>Database: PostgreSQL 16</li>
        </ul>
      </div>
    </div>
  );
}
