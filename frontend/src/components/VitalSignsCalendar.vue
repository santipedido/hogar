<template>
  <div class="vital-signs-calendar">
    <div class="calendar-header">
      <h3>Calendario de Signos Vitales</h3>
      <div class="calendar-controls">
        <button @click="previousMonth" class="nav-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15,18 9,12 15,6"></polyline>
          </svg>
        </button>
        <span class="current-month">{{ currentMonthName }} {{ currentYear }}</span>
        <button @click="nextMonth" class="nav-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9,18 15,12 9,6"></polyline>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loader">
      <IconSpinner :size="30" />
      <p>Cargando calendario...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCalendarData" class="retry-btn">Reintentar</button>
    </div>

    <div v-else class="calendar-container">
      <!-- Días de la semana -->
      <div class="calendar-weekdays">
        <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
      </div>

      <!-- Días del mes -->
      <div class="calendar-grid">
        <div 
          v-for="day in calendarDays" 
          :key="day.date" 
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'has-vital-signs': day.vitalSigns && day.vitalSigns.length > 0
          }"
          @click="day.isCurrentMonth && day.vitalSigns && day.vitalSigns.length > 0 ? showDayDetails(day) : null"
        >
          <span class="day-number">{{ day.dayNumber }}</span>
          <div v-if="day.vitalSigns && day.vitalSigns.length > 0" class="vital-signs-indicators">
            <div 
              v-for="vitalSign in day.vitalSigns.slice(0, 3)" 
              :key="vitalSign.id"
              class="vital-sign-dot"
              :class="getVitalSignColor(vitalSign.type)"
              :title="`${vitalSign.type}: ${formatVitalSignValue(vitalSign)}`"
            ></div>
            <span v-if="day.vitalSigns.length > 3" class="more-indicator">+{{ day.vitalSigns.length - 3 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalles del día -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>{{ selectedDay?.date ? formatDate(selectedDay.date) : '' }}</h4>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedDay?.vitalSigns && selectedDay.vitalSigns.length > 0" class="day-vital-signs">
            <div v-for="vitalSign in selectedDay.vitalSigns" :key="vitalSign.id" class="vital-sign-item">
              <div class="vital-sign-info">
                <h5>{{ vitalSign.type }}</h5>
                <p class="value">{{ formatVitalSignValue(vitalSign) }}</p>
                <p class="time">{{ formatTime(vitalSign.taken_at) }}</p>
                <p v-if="vitalSign.notes" class="notes">{{ vitalSign.notes }}</p>
                <p v-if="vitalSign.taken_by" class="taken-by">Tomado por: {{ vitalSign.taken_by }}</p>
              </div>
            </div>
          </div>
          <div v-else class="no-vital-signs">
            No hay signos vitales registrados para este día.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import IconSpinner from './icons/IconSpinner.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const loading = ref(false)
const error = ref('')
const calendarData = ref({ vital_signs: [], calendar_data: {} })
const showModal = ref(false)
const selectedDay = ref(null)

const weekDays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

const currentMonthName = computed(() => {
  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  return months[currentMonth.value - 1]
})

const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    
    const dateKey = date.toISOString().split('T')[0]
    const isCurrentMonth = date.getMonth() === currentMonth.value - 1
    const isToday = date.getTime() === today.getTime()
    
    days.push({
      date: dateKey,
      dayNumber: date.getDate(),
      isCurrentMonth,
      isToday,
      vitalSigns: calendarData.value.calendar_data[dateKey] || []
    })
  }
  
  return days
})

async function fetchCalendarData() {
  console.log('VITE_API_URL:', import.meta.env.VITE_API_URL)
  console.log('Fetching calendar data for resident:', props.residentId, 'year:', currentYear.value, 'month:', currentMonth.value)
  loading.value = true
  error.value = ''
  try {
    const url = `${import.meta.env.VITE_API_URL}/api/vital-signs/calendar/${props.residentId}?year=${currentYear.value}&month=${currentMonth.value}`
    console.log('Fetching URL:', url)
    const res = await fetch(url)
    console.log('Response status:', res.status)
    if (!res.ok) throw new Error('No se pudo cargar el calendario')
    const data = await res.json()
    console.log('Calendar data received:', data)
    calendarData.value = data
  } catch (e) {
    console.error('Error fetching calendar data:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function previousMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  fetchCalendarData()
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  fetchCalendarData()
}

function showDayDetails(day) {
  selectedDay.value = day
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedDay.value = null
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

function formatTime(dateTimeString) {
  const date = new Date(dateTimeString)
  return new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function formatVitalSignValue(vitalSign) {
  if (vitalSign.type === 'Presión Arterial') {
    return `${vitalSign.systolic}/${vitalSign.diastolic} ${vitalSign.unit || 'mmHg'}`
  }
  return `${vitalSign.value} ${vitalSign.unit || ''}`
}

function getVitalSignColor(type) {
  const colors = {
    'Temperatura': 'temperature',
    'Frecuencia Cardíaca': 'heart-rate',
    'Frecuencia Respiratoria': 'respiratory',
    'Presión Arterial': 'blood-pressure',
    'Saturación O2': 'oxygen',
    'Glucemia': 'glucose'
  }
  return colors[type] || 'default'
}

onMounted(() => {
  console.log('VitalSignsCalendar montado, residentId:', props.residentId)
  fetchCalendarData()
})
</script>

<style scoped>
.vital-signs-calendar {
  padding: 1rem;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.calendar-header h3 {
  margin: 0;
  color: var(--color-heading);
}

.calendar-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: var(--color-background-mute);
}

.current-month {
  font-weight: 600;
  color: var(--color-text-dark);
  min-width: 120px;
  text-align: center;
}

.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: var(--color-text-light);
}

.error {
  text-align: center;
  padding: 2rem;
  color: var(--color-danger, #dc3545);
  background: var(--color-background-soft);
  border-radius: 8px;
}

.retry-btn {
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.calendar-container {
  background: var(--color-background-soft);
  border-radius: 10px;
  overflow: hidden;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--color-background-mute);
}

.weekday {
  padding: 1rem 0.5rem;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-dark);
  font-size: 0.875rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.calendar-day {
  min-height: 80px;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.calendar-day:hover {
  background: var(--color-background-mute);
}

.calendar-day.other-month {
  background: var(--color-background-mute);
  color: var(--color-text-light);
}

.calendar-day.today {
  background: var(--color-primary);
  color: white;
}

.calendar-day.has-vital-signs {
  background: rgba(52, 152, 219, 0.1);
}

.day-number {
  font-weight: 600;
  font-size: 0.875rem;
}

.vital-signs-indicators {
  position: absolute;
  bottom: 0.25rem;
  left: 0.25rem;
  right: 0.25rem;
  display: flex;
  gap: 0.125rem;
  flex-wrap: wrap;
}

.vital-sign-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.vital-sign-dot.temperature { background: #e74c3c; }
.vital-sign-dot.heart-rate { background: #e91e63; }
.vital-sign-dot.respiratory { background: #3498db; }
.vital-sign-dot.blood-pressure { background: #9b59b6; }
.vital-sign-dot.oxygen { background: #1abc9c; }
.vital-sign-dot.glucose { background: #f39c12; }
.vital-sign-dot.default { background: #95a5a6; }

.more-indicator {
  font-size: 0.625rem;
  color: var(--color-text-light);
  margin-left: 0.25rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-background);
  border-radius: 10px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h4 {
  margin: 0;
  color: var(--color-heading);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-light);
}

.modal-body {
  padding: 1.5rem;
}

.day-vital-signs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.vital-sign-item {
  background: var(--color-background-soft);
  border-radius: 8px;
  padding: 1rem;
}

.vital-sign-info h5 {
  margin: 0 0 0.5rem 0;
  color: var(--color-heading);
}

.value {
  margin: 0.25rem 0;
  color: var(--color-text);
  font-weight: 500;
  font-size: 1.1rem;
}

.time {
  margin: 0.25rem 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.notes {
  margin: 0.5rem 0 0 0;
  color: var(--color-text-light);
  font-style: italic;
  font-size: 0.875rem;
}

.taken-by {
  margin: 0.25rem 0 0 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.no-vital-signs {
  text-align: center;
  color: var(--color-text-light);
  padding: 2rem;
}

@media (max-width: 640px) {
  .calendar-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .calendar-day {
    min-height: 60px;
    padding: 0.25rem;
  }
  
  .day-number {
    font-size: 0.75rem;
  }
  
  .vital-sign-dot {
    width: 4px;
    height: 4px;
  }
}
</style>