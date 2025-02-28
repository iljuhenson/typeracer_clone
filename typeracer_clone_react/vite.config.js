import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],
	server: {
		proxy: {
			// string shorthand for simple case
			//'/api': 'http://localhost:3000/api',
			//'^/api/.*': {
			//	target: 'http://localhost:3000/api',
			//	changeOrigin: true,
			//	secure: false,
			//	rewrite: (path) => path.replace(/^\/api/, ''),
			//},
			'/ws': {
				target: 'ws://127.0.0.1:8000/',
				ws: true,
				changeOrigin: true,
				secure: false,
			},

			'/api': {
				target: "http://127.0.0.1:8000/",
				changeOrigin: true,
				secure: false,
			},

			//'/api': {
			//	target: "http://localhost:80/",
			//	changeOrigin: true,
			//	secure: false,
			//},
			//
			//// Proxying websockets or socket.io
			//'/ws': {
			//	target: 'ws://localhost:80/',
			//	ws: true,
			//	changeOrigin: true,
			//}
		}
	}
})
