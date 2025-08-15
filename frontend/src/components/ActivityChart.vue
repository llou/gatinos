<template>
  <div class="activity-chart-container">
    <div v-if="loading" class="loading-placeholder">
      <span>Cargando actividad...</span>
    </div>
    <div v-else class="activity-chart" ref="chartContainer">
      <svg :width="width" :height="height">
        <!-- Month labels -->
        <g class="months">
          <text
            v-for="(month, index) in monthLabels"
            :key="`month-${index}`"
            :x="month.x"
            :y="20"
            class="month-label"
            :fill="textColor"
          >
            {{ month.name }}
          </text>
        </g>
        
        <!-- Day labels -->
        <g class="days">
          <text
            v-for="(day, index) in weekDays"
            :key="`day-${index}`"
            :x="10"
            :y="getWeekdayY(index) + cellSize / 2 + 3"
            class="day-label"
            :fill="textColor"
          >
            {{ day }}
          </text>
        </g>
        
        <!-- Activity cells -->
        <g class="cells" transform="translate(40, 30)">
          <rect
            v-for="(cell, index) in cells"
            :key="`cell-${index}`"
            :x="cell.x"
            :y="cell.y"
            :width="cellSize"
            :height="cellSize"
            :fill="getCellColor(cell.count)"
            :stroke="borderColor"
            stroke-width="1"
            @mouseover="showTooltip($event, cell)"
            @mouseout="hideTooltip"
          >
            <title>{{ cell.date }}: {{ cell.count }} actividades</title>
          </rect>
        </g>
      </svg>
      
      <!-- Tooltip -->
      <div
        v-if="tooltip.visible"
        class="activity-tooltip"
        :style="{
          left: tooltip.x + 'px',
          top: tooltip.y + 'px'
        }"
      >
        {{ tooltip.text }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'ActivityChart',
  props: {
    entityType: {
      type: String,
      required: true,
      validator: (value) => ['colonia', 'gato'].includes(value)
    },
    entityId: {
      type: [String, Number],
      required: false
    },
    entitySlug: {
      type: String,
      required: false
    },
    coloniaSlug: {
      type: String,
      required: false
    },
    rpcUrl: {
      type: String,
      default: '/rpc/'
    },
    language: {
      type: String,
      default: 'es'
    }
  },
  setup(props) {
    const activityData = ref([])
    const loading = ref(false)
    const error = ref(null)
    const isDarkMode = ref(false)
    const cellSize = 12
    const cellSpacing = 2
    const width = 850
    const height = 150
    
    const tooltip = ref({
      visible: false,
      x: 0,
      y: 0,
      text: ''
    })
    
    // Dark mode detection
    const checkDarkMode = () => {
      isDarkMode.value = document.documentElement.getAttribute('data-theme') === 'dark'
    }
    
    // Computed colors based on dark mode
    const borderColor = computed(() => {
      return isDarkMode.value ? '#30363d' : '#e1e4e8'
    })
    
    const textColor = computed(() => {
      return isDarkMode.value ? '#8b949e' : '#586069'
    })
    
    const bgColor = computed(() => {
      return 'transparent'
    })
    
    // Localized labels
    const weekDays = computed(() => {
      if (props.language === 'es') {
        return ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom']
      }
      return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    })
    
    const monthLabels = computed(() => {
      const labels = []
      const monthNames = props.language === 'es' 
        ? ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
        : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      
      if (cells.value.length === 0) return labels
      
      // Track which months we've already added
      const addedMonths = new Set()
      let lastMonth = -1
      
      // Go through cells to find month boundaries
      cells.value.forEach(cell => {
        const date = new Date(cell.date)
        const month = date.getMonth()
        const monthYear = `${month}-${date.getFullYear()}`
        
        // Add label when month changes and we haven't added this month-year combo yet
        if (month !== lastMonth && !addedMonths.has(monthYear)) {
          labels.push({
            name: monthNames[month],
            x: cell.x + 40, // Offset for day labels
            week: cell.week
          })
          addedMonths.add(monthYear)
          lastMonth = month
        }
      })
      
      return labels
    })
    
    // Generate cells for the activity chart
    const cells = computed(() => {
      const today = new Date()
      const oneYearAgo = new Date(today)
      oneYearAgo.setFullYear(today.getFullYear() - 1)
      
      const cellData = []
      const activityMap = new Map()
      
      // Build activity map from data
      activityData.value.forEach(date => {
        const dateStr = date.split('T')[0]
        activityMap.set(dateStr, (activityMap.get(dateStr) || 0) + 1)
      })
      
      // Generate cells for each day in the past year
      let currentDate = new Date(oneYearAgo)
      let week = 0
      let startDay = currentDate.getDay()
      
      // Adjust for Monday start (0 = Monday, 6 = Sunday)
      startDay = startDay === 0 ? 6 : startDay - 1
      
      while (currentDate <= today) {
        const dayOfWeek = currentDate.getDay()
        const adjustedDay = dayOfWeek === 0 ? 6 : dayOfWeek - 1
        const dateStr = currentDate.toISOString().split('T')[0]
        const count = activityMap.get(dateStr) || 0
        
        cellData.push({
          date: dateStr,
          x: week * (cellSize + cellSpacing),
          y: adjustedDay * (cellSize + cellSpacing),
          count: count,
          weekday: adjustedDay,
          week: week
        })
        
        currentDate.setDate(currentDate.getDate() + 1)
        
        // Move to next week column on Monday
        if (currentDate.getDay() === 1) {
          week++
        }
      }
      
      return cellData
    })
    
    // Get cell color based on activity count
    const getCellColor = (count) => {
      if (isDarkMode.value) {
        // Dark mode colors (similar to GitHub dark theme)
        if (count === 0) return '#161b22'
        if (count === 1) return '#0e4429'
        if (count === 2) return '#006d32'
        if (count === 3) return '#26a641'
        return '#39d353'
      } else {
        // Light mode colors
        if (count === 0) return '#ebedf0'
        if (count === 1) return '#9be9a8'
        if (count === 2) return '#40c463'
        if (count === 3) return '#30a14e'
        return '#216e39'
      }
    }
    
    // Get weekday label position
    const getWeekdayY = (index) => {
      return 30 + (index * (cellSize + cellSpacing))
    }
    
    // Tooltip functions
    const showTooltip = (event, cell) => {
      const rect = event.target.getBoundingClientRect()
      const containerRect = event.target.closest('.activity-chart-container').getBoundingClientRect()
      
      tooltip.value = {
        visible: true,
        x: rect.left - containerRect.left + cellSize / 2,
        y: rect.top - containerRect.top - 30,
        text: `${cell.date}: ${cell.count} ${cell.count === 1 ? 'actividad' : 'actividades'}`
      }
    }
    
    const hideTooltip = () => {
      tooltip.value.visible = false
    }
    
    // Fetch activity data via RPC
    const fetchActivityData = async () => {
      loading.value = true
      error.value = null
      
      try {
        let method = ''
        let params = {}
        
        if (props.entityType === 'colonia') {
          method = 'get_colony_activity'
          params = {
            colonia_slug: props.entitySlug || props.coloniaSlug
          }
        } else if (props.entityType === 'gato') {
          method = 'get_cat_activity'
          params = {
            colonia_slug: props.coloniaSlug,
            gato_slug: props.entitySlug
          }
        } else {
          throw new Error(`Unsupported entity type: ${props.entityType}`)
        }
        
        const payload = {
          jsonrpc: '2.0',
          method: method,
          params: params,
          id: Date.now()
        }
        
        const response = await fetch(props.rpcUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          credentials: 'same-origin',
          body: JSON.stringify(payload)
        })
        
        const data = await response.json()
        
        if (data.error) {
          throw new Error(data.error.message || 'Error fetching activity data')
        }
        
        activityData.value = data.result.dates || []
      } catch (err) {
        error.value = err.message
        console.error('Error fetching activity data:', err)
      } finally {
        loading.value = false
      }
    }
    
    // Get CSRF token from cookies
    const getCookie = (name) => {
      let cookieValue = null
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim()
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          }
        }
      }
      return cookieValue
    }
    
    // Fetch data on mount and setup dark mode observer
    onMounted(() => {
      checkDarkMode()
      fetchActivityData()
      
      // Watch for dark mode changes
      const observer = new MutationObserver(() => {
        checkDarkMode()
      })
      
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
      })
      
      // Store observer for cleanup
      onUnmounted(() => {
        observer.disconnect()
      })
    })
    
    // Re-fetch if props change
    watch(
      () => [props.entityType, props.entityId, props.entitySlug],
      () => {
        fetchActivityData()
      }
    )
    
    return {
      cells,
      weekDays,
      monthLabels,
      cellSize,
      width,
      height,
      borderColor,
      textColor,
      bgColor,
      tooltip,
      loading,
      error,
      getCellColor,
      getWeekdayY,
      showTooltip,
      hideTooltip,
      isDarkMode
    }
  }
}
</script>

<style scoped>
.activity-chart-container {
  position: relative;
  padding: 10px;
  background: v-bind(bgColor);
  border-radius: 6px;
  overflow: visible;
  box-sizing: border-box;
}

.activity-chart {
  position: relative;
  width: 850px;
  height: 150px;
}

.activity-chart svg {
  display: block;
}

.month-label,
.day-label {
  font-size: 11px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}

.day-label {
  text-anchor: middle;
}

.activity-tooltip {
  position: absolute;
  padding: 5px 8px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 12px;
  border-radius: 3px;
  pointer-events: none;
  white-space: nowrap;
  z-index: 1000;
}

.activity-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.8);
}

.loading-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 850px;
  height: 150px;
  color: v-bind(textColor);
  font-size: 14px;
}
</style>