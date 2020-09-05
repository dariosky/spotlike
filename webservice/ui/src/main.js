import { createApp } from 'vue'
// import VueMeta from 'vue-meta'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
// app.use(VueMeta)
app.mount('#app')
