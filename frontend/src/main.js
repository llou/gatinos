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
        availableUsers: [],
        currentUserId: null,
        loading: false,
        isAdmin: false,
        calendarKey: 0
      }
    },
    async mounted() {
      await this.loadFeedingDates()
    },
    methods: {
      async loadFeedingDates() {
        try {
          this.loading = true
          
          // Load feeding dates
          const datesResult = await makeRpcCall('get_feeding_dates', {
            colonia_id: this.coloniaId
          })
          
          // Load available users and admin status
          const usersResult = await makeRpcCall('get_colony_feeding_users', {
            colonia_id: this.coloniaId
          })
          
          // Store admin status and current user
          this.isAdmin = usersResult.is_admin || false
          this.currentUserId = usersResult.current_user_id
          this.availableUsers = usersResult.users || []
          
          // Process feeding dates with client-side color logic
          this.feedingDates = datesResult.dates.map(dateInfo => {
            // Determine color based on user
            let color = null
            if (dateInfo.user_id) {
              color = dateInfo.user_id === this.currentUserId ? 'red' : 'blue'
            }
            
            return {
              dates: new Date(dateInfo.date),
              dot: {
                color: color,
                class: 'feeding-date',
              },
              popover: {
                label: dateInfo.full_name || dateInfo.username,
                visibility: 'hover',
                hideIndicator: true,
                isInteractive: false
              },
              userId: dateInfo.user_id,
              username: dateInfo.username,
              fullName: dateInfo.full_name
            }
          })
          
        } catch (error) {
          console.error('Error loading feeding dates:', error)
        } finally {
          this.loading = false
        }
      },
      
      async onDayClick(day) {
        this.selectedDate = day.date
        
        const dateStr = this.formatDate(day.date)
        const currentAttribute = this.feedingDates.find(attr => 
          this.formatDate(attr.dates) === dateStr
        )
        
        let targetUserId = null
        
        if (this.isAdmin) {
          // Admin: cycle through users
          
          if (!currentAttribute || !currentAttribute.userId) {
            // No assignment, assign first user
            targetUserId = this.availableUsers.length > 0 ? this.availableUsers[0].id : null
          } else {
            // Find next user in cycle
            const currentIndex = this.availableUsers.findIndex(u => u.id === currentAttribute.userId)
            
            if (currentIndex < 0 || currentIndex >= this.availableUsers.length) {
              // Current user not in list (shouldn't happen), start with first user
              targetUserId = this.availableUsers.length > 0 ? this.availableUsers[0].id : 0
            } else if (currentIndex < this.availableUsers.length - 1) {
              // Next user
              targetUserId = this.availableUsers[currentIndex + 1].id
            } else {
              // At end of list, cycle back to unassigned (0)
              targetUserId = 0
            }
          }
        } else {
          // Normal user: check if it's someone else's assignment
          if (currentAttribute && currentAttribute.userId !== this.currentUserId) {
            return
          }
          // Toggle self - let backend handle it
          targetUserId = null
        }
        
        try {
          this.loading = true
          const result = await makeRpcCall('set_feeding_assignment', {
            date_str: dateStr,
            colonia_id: this.coloniaId,
            user_id: targetUserId
          })
          
          console.log('RPC set feeding assignment:', result)
          
          // Update the feedingDates array
          const existingIndex = this.feedingDates.findIndex(attr => 
            this.formatDate(attr.dates) === dateStr
          )
          
          if (result.assigned) {
            // Determine color based on user
            console.log("Assigning to: ", result.username);
            const color = result.user_id === this.currentUserId ? 'red' : 'blue'
            
            const newAttribute = {
              dates: day.date,
              dot: {
                color: color,
                class: 'feeding-date',
              },
              popover: {
                label: result.username,
                visibility: 'hover',
              },
              userId: result.user_id,
              username: result.username,
              fullName: result.full_name
            }

            
            if (existingIndex >= 0) {
              this.feedingDates[existingIndex] = newAttribute
            } else {
              this.feedingDates.push(newAttribute)
            }
          } else {
            // Remove the date if no longer assigned
            if (existingIndex >= 0) {
              this.feedingDates.splice(existingIndex, 1);
            }
          }
          
          // Force v-calendar to re-render by changing the key
          this.calendarKey++
        } catch (error) {
          console.error('Error toggling feeding date:', error)
          if (error.message && error.message !== 'undefined') {
            alert('Error al actualizar el calendario: ' + error.message)
          }
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

      isDark() {
    	const savedTheme = localStorage.getItem('theme') || 'light';
        return savedTheme === 'dark';
      },
      

    },
    template: `
      <div>
        <VCalendar 
          :key="calendarKey"
          locale="es"
          :attributes="feedingDates"
          @dayclick="onDayClick"
          :disabled="loading"
          :columns=2
          :is-dark="isDark"
          borderless
          is-expanded
          disable-page-swipe
          :min-page="{ month: new Date().getMonth() + 1, year: new Date().getFullYear() }"
          :max-page="{ month: new Date().getMonth() + 2, year: new Date().getFullYear() }"
        >
          <template #header>
            <!-- Hide navigation by providing empty header -->
          </template>
        </VCalendar>
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
