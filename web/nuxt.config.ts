export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  css: ['@/assets/styles/main.css'],
  app: {
    baseURL: process.env.NUXT_APP_BASE_URL || '/agent/',
    head: {
      title: 'HTML2PPT Agent',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Agent workspace for generating Slidev decks with live preview.' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap'
        }
      ]
    }
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
      previewBase: process.env.NUXT_PUBLIC_PREVIEW_BASE || '/preview'
    }
  },
  devtools: { enabled: false }
});
