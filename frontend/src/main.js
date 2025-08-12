// Main entry point for frontend modules
import { createApp } from 'vue'
import VCalendar from 'v-calendar'
import 'v-calendar/style.css'

// RPC helper functions
function getCsrfToken() {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrftoken') {
      return value
    }
  }
  // Try to get from meta tag if cookie not found
  const metaTag = document.querySelector('[name=csrf-token]')
  return metaTag ? metaTag.content : ''
}

async function makeRpcCall(method, params = {}) {
  const payload = {
    jsonrpc: '2.0',
    method: method,
    params: params,
    id: Date.now()
  }

  const response = await fetch('/rpc/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  
  if (data.error) {
    throw new Error(data.error.message || JSON.stringify(data.error))
  }

  return data.result
}

// Export function to create the calendar app
export function createCalendarApp(coloniaId) {
  console.log('Creating calendar app for colonia:', coloniaId)
  
  const app = createApp({
    data() {
      return {
        coloniaId,
        selectedDate: new Date(),
        feedingDates: [],
        loading: false
      }
    },
    async mounted() {
      await this.loadFeedingDates()
    },
    methods: {
      async loadFeedingDates() {
        try {
          this.loading = true
          const result = await makeRpcCall('get_feeding_dates', {
            colonia_id: this.coloniaId
          })
          
          this.feedingDates = result.dates.map(dateInfo => ({
            dates: new Date(dateInfo.date),
            dot: {
              color: this.getColorCode(dateInfo.color),
              class: 'feeding-date'
            },
            popover: {
              label: `Alimentación: ${dateInfo.user || 'Sin asignar'}`
            }
          }))
          
          console.log('Loaded feeding dates:', this.feedingDates)
        } catch (error) {
          console.error('Error loading feeding dates:', error)
        } finally {
          this.loading = false
        }
      },
      
      async onDayClick(day) {
        console.log('Day clicked:', day)
        this.selectedDate = day.date
        
        const dateStr = this.formatDate(day.date)
        const currentAttribute = this.feedingDates.find(attr => 
          this.formatDate(attr.dates) === dateStr
        )
        
        const currentColor = currentAttribute ? 
          this.getColorName(currentAttribute.dot.color) : null
        
        try {
          this.loading = true
          const result = await makeRpcCall('toggle_feeding_date', {
            date_str: dateStr,
            colonia_id: this.coloniaId,
            current_color: currentColor
          })
          
          console.log('RPC result:', result)
          
          // Update the feedingDates array
          const existingIndex = this.feedingDates.findIndex(attr => 
            this.formatDate(attr.dates) === dateStr
          )
          
          if (result.assigned) {
            const newAttribute = {
              dates: day.date,
              dot: {
                color: this.getColorCode(result.color),
                class: 'feeding-date'
              },
              popover: {
                label: 'Alimentación asignada'
              }
            }
            
            if (existingIndex >= 0) {
              this.feedingDates[existingIndex] = newAttribute
            } else {
              this.feedingDates.push(newAttribute)
            }
          } else {
            // Remove the date if no longer assigned
            if (existingIndex >= 0) {
              this.feedingDates.splice(existingIndex, 1)
            }
          }
          
        } catch (error) {
          console.error('Error toggling feeding date:', error)
          alert('Error al actualizar el calendario: ' + error.message)
        } finally {
          this.loading = false
        }
      },
      
      formatDate(date) {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      },
      
      getColorCode(colorName) {
        const colorMap = {
          'green': '#4CAF50',
          'blue': '#2196F3',
          'red': '#F44336',
          'orange': '#FF9800'
        }
        return colorMap[colorName] || '#4CAF50'
      },
      
      getColorName(colorCode) {
        const nameMap = {
          '#4CAF50': 'green',
          '#2196F3': 'blue',
          '#F44336': 'red',
          '#FF9800': 'orange'
        }
        return nameMap[colorCode] || 'green'
      }
    },
    template: `
      <div>
        <VCalendar 
          :attributes="feedingDates"
          @dayclick="onDayClick"
          :disabled="loading"
          columns=2
          borderless
          is-expanded
        />
        <p v-if="selectedDate" style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
          Última fecha seleccionada: {{ selectedDate.toLocaleDateString('es-ES') }}
        </p>
      </div>
    `
  })
  
  // Install VCalendar plugin
  app.use(VCalendar)
  
  return app
}

// Make it available globally if needed
if (typeof window !== 'undefined') {
  window.createCalendarApp = createCalendarApp
}
