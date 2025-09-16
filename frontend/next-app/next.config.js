/**
 * Next.js config: add rewrites so the dev server proxies upload and file requests
 * to the local backend. This makes the browser requests same-origin and avoids
 * CORS and mixed-content issues during development.
 */
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:3001';

/**
 * Next.js config: rewrites use BACKEND_URL so the dev server can proxy to the
 * correct backend depending on environment. In Docker we set BACKEND_URL to
 * the compose service name (http://backend:3001) so the frontend container can
 * reach the backend over the internal network.
 */
module.exports = {
	async rewrites() {
		return [
			{ source: '/api/upload', destination: `${BACKEND_URL}/upload` },
			{ source: '/api/uploads', destination: `${BACKEND_URL}/uploads` },
			{ source: '/files/:path*', destination: `${BACKEND_URL}/files/:path*` },
		];
	},
};
