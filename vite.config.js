// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: true, // exposes server to network
    port: 5173,
    allowedHosts: [
      'ec2-98-84-179-217.compute-1.amazonaws.com' // replace with your EC2 DNS
    ]
  }
})
