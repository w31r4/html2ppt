export default defineNuxtConfig({
  modules: ['@pinia/nuxt', '@unocss/nuxt'],
  css: ['@/assets/styles/main.css'],
  compatibilityDate: '2025-12-31',
  app: {
    baseURL: process.env.NUXT_APP_BASE_URL || '/agent/',
    head: {
      title: 'HTML2PPT Agent',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Agent workspace for generating Slidev decks with live preview.' }
      ],
      link: [
        // Material Symbols for icons (rounded variant)
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap'
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
