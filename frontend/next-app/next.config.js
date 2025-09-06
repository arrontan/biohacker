/**
 * Next.js config: add rewrites so the dev server proxies upload and file requests
 * to the local backend. This makes the browser requests same-origin and avoids
 * CORS and mixed-content issues during development.
 */
module.exports = {
	async rewrites() {
		return [
			{ source: '/api/upload', destination: 'http://127.0.0.1:3001/upload' },
			{ source: '/api/uploads', destination: 'http://127.0.0.1:3001/uploads' },
			{ source: '/files/:path*', destination: 'http://127.0.0.1:3001/files/:path*' },
			// leave room for other proxy rules
		];
	},
};
