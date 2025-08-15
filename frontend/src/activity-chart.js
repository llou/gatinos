import { createApp } from 'vue'
import ActivityChart from './components/ActivityChart.vue'

// Mount activity charts for colonies
document.querySelectorAll('.colony-activity-chart').forEach(el => {
  const app = createApp(ActivityChart, {
    entityType: 'colonia',
    entitySlug: el.dataset.coloniaSlug,
    rpcUrl: el.dataset.rpcUrl || '/rpc/',
    language: el.dataset.language || 'es'
  })
  app.mount(el)
})

// Mount activity charts for cats
document.querySelectorAll('.cat-activity-chart').forEach(el => {
  const app = createApp(ActivityChart, {
    entityType: 'gato',
    entitySlug: el.dataset.gatoSlug,
    coloniaSlug: el.dataset.coloniaSlug,
    rpcUrl: el.dataset.rpcUrl || '/rpc/',
    language: el.dataset.language || 'es'
  })
  app.mount(el)
})