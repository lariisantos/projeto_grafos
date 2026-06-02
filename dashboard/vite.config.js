import { defineConfig } from 'vite'

export default defineConfig({
  base: './',
  build: {
    rolldownOptions: {
      moduleTypes: { '.js': 'jsx' },
    },
  },
})
