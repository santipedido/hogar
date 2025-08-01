<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h3>{{ isEdit ? 'Editar' : 'Agregar' }} Actividad</h3>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="type">Tipo de Actividad</label>
          <select v-model="form.type" id="type" required @change="onTypeChange">
            <option value="">Selecciona tipo</option>
            <option value="Físicas">Físicas</option>
            <option value="Recreativas">Recreativas</option>
            <option value="Sociales">Sociales</option>
            <option value="Terapéuticas">Terapéuticas</option>
          </select>
        </div>

        <div class="form-group">
          <label for="subtype">Subcategoría</label>
          <select v-model="form.subtype" id="subtype" required>
            <option value="">Selecciona subcategoría</option>
            <option v-for="subtype in availableSubtypes" :key="subtype" :value="subtype">
              {{ subtype }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="title">Título de la Actividad</label>
          <input type="text" v-model="form.title" id="title" required placeholder="Ej: Ejercicios de fisioterapia" />
        </div>

        <div class="form-group">
          <label for="description">Descripción</label>
          <textarea v-model="form.description" id="description" rows="3" placeholder="Descripción detallada de la actividad"></textarea>
        </div>

        <div class="form-group">
          <label for="scheduled_at">Fecha y Hora Programada</label>
          <input type="datetime-local" v-model="form.scheduled_at" id="scheduled_at" required />
        </div>

        <div class="form-group">
          <label for="participants">Tipo de Participación</label>
          <select v-model="form.participants" id="participants" required @change="onParticipantsTypeChange">
            <option value="">Selecciona tipo de participación</option>
            <option value="Residente solo">Residente solo</option>
            <option value="Con personal">Con personal</option>
            <option value="Con familiares">Con familiares</option>
            <option value="Grupo mixto">Grupo mixto</option>
          </select>
        </div>

        <!-- Selección de participantes específicos -->
        <div class="form-group" v-if="showParticipantsSelection">
          <label>Seleccionar Participantes</label>
          
          <!-- Personal -->
          <div class="participants-section" v-if="showStaffSelection">
            <h4>Personal</h4>
            <div class="participants-list">
              <div class="add-participant">
                <input 
                  type="text" 
                  v-model="newStaffName" 
                  placeholder="Nombre del personal"
                  @keyup.enter="addStaffMember"
                />
                <button type="button" @click="addStaffMember" class="add-btn-small">Agregar</button>
              </div>
              <label 
                v-for="(staff, index) in staffMembers" 
                :key="index"
                class="participant-item"
              >
                <input 
                  type="checkbox" 
                  :value="{ type: 'staff', name: staff }"
                  v-model="selectedParticipants"
                  @change="updateParticipantsData"
                />
                <span>{{ staff }}</span>
                <button type="button" @click="removeStaffMember(index)" class="remove-btn">×</button>
              </label>
            </div>
          </div>

          <!-- Familiares -->
          <div class="participants-section" v-if="showFamilySelection">
            <h4>Familiares</h4>
            <div class="participants-list">
              <div class="add-participant">
                <input 
                  type="text" 
                  v-model="newFamilyName" 
                  placeholder="Nombre del familiar"
                  @keyup.enter="addFamilyMember"
                />
                <button type="button" @click="addFamilyMember" class="add-btn-small">Agregar</button>
              </div>
              <label 
                v-for="(family, index) in familyMembers" 
                :key="index"
                class="participant-item"
              >
                <input 
                  type="checkbox" 
                  :value="{ type: 'family', name: family }"
                  v-model="selectedParticipants"
                  @change="updateParticipantsData"
                />
                <span>{{ family }}</span>
                <button type="button" @click="removeFamilyMember(index)" class="remove-btn">×</button>
              </label>
            </div>
          </div>

          <!-- Resumen de participantes seleccionados -->
          <div class="selected-participants" v-if="selectedParticipants.length > 0">
            <h4>Participantes Seleccionados:</h4>
            <div class="participants-summary">
              <span 
                v-for="participant in selectedParticipants" 
                :key="`${participant.type}-${participant.id || participant.name}`"
                class="participant-tag"
              >
                {{ participant.name }}
                <button type="button" @click="removeParticipant(participant)" class="remove-tag">×</button>
              </span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="status">Estado</label>
          <select v-model="form.status" id="status" required>
            <option value="scheduled">Programada</option>
            <option value="completed">Completada</option>
            <option value="cancelled">Cancelada</option>
          </select>
        </div>

        <div class="form-group" v-if="form.status === 'completed'">
          <label for="completed_at">Fecha y Hora de Realización</label>
          <input type="datetime-local" v-model="form.completed_at" id="completed_at" />
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.is_recurring" />
            Actividad Semanal Recurrente
          </label>
        </div>

        <div class="form-group" v-if="form.is_recurring">
          <label for="recurrence_day">Día de la Semana</label>
          <select v-model="form.recurrence_day" id="recurrence_day" required>
            <option value="">Selecciona día</option>
            <option value="monday">Lunes</option>
            <option value="tuesday">Martes</option>
            <option value="wednesday">Miércoles</option>
            <option value="thursday">Jueves</option>
            <option value="friday">Viernes</option>
            <option value="saturday">Sábado</option>
            <option value="sunday">Domingo</option>
          </select>
        </div>

        <div class="form-group">
          <label for="notes">Notas Adicionales</label>
          <textarea v-model="form.notes" id="notes" rows="3" placeholder="Notas adicionales sobre la actividad"></textarea>
        </div>

        <div class="form-group">
          <label for="registered_by">Registrado por</label>
          <input type="text" v-model="form.registered_by" id="registered_by" placeholder="Nombre de quien registra" />
        </div>

        <div class="form-actions">
          <button type="button" @click="$emit('cancel')" class="cancel-btn">Cancelar</button>
          <button type="submit" class="submit-btn">{{ isEdit ? 'Actualizar' : 'Crear' }} Actividad</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  },
  residentId: {
    type: String,
    required: true
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const form = ref({
  type: '',
  subtype: '',
  title: '',
  description: '',
  scheduled_at: '',
  completed_at: '',
  participants: '',
  participants_data: [],
  status: 'scheduled',
  is_recurring: false,
  recurrence_day: '',
  notes: '',
  registered_by: ''
})

// Datos para la selección de participantes
const selectedParticipants = ref([])
const staffMembers = ref([])
const familyMembers = ref([])
const newStaffName = ref('')
const newFamilyName = ref('')

// Computed para mostrar/ocultar secciones
const showParticipantsSelection = computed(() => {
  return form.value.participants && form.value.participants !== 'Residente solo'
})

const showStaffSelection = computed(() => {
  return ['Con personal', 'Grupo mixto'].includes(form.value.participants)
})

const showFamilySelection = computed(() => {
  return ['Con familiares', 'Grupo mixto'].includes(form.value.participants)
})

// Subcategorías por tipo de actividad
const subtypesByType = {
  'Físicas': ['Ejercicios', 'Caminatas', 'Yoga', 'Baile', 'Natación', 'Ejercicios de resistencia', 'Estiramientos'],
  'Recreativas': ['Juegos', 'Manualidades', 'Pintura', 'Música', 'Lectura', 'Puzzles', 'Jardinería', 'Cocina'],
  'Sociales': ['Visitas familiares', 'Eventos', 'Celebraciones', 'Grupos de conversación', 'Actividades comunitarias'],
  'Terapéuticas': ['Fisioterapia', 'Terapia ocupacional', 'Terapia del habla', 'Terapia cognitiva', 'Terapia emocional']
}

const availableSubtypes = computed(() => {
  return subtypesByType[form.value.type] || []
})

function onTypeChange() {
  form.value.subtype = ''
}

function onParticipantsTypeChange() {
  selectedParticipants.value = []
  form.value.participants_data = []
  
  if (form.value.participants === 'Residente solo') {
    selectedParticipants.value = [{ type: 'resident', id: props.residentId, name: 'Residente actual' }]
    updateParticipantsData()
  }
}

function addStaffMember() {
  if (newStaffName.value.trim()) {
    staffMembers.value.push(newStaffName.value.trim())
    newStaffName.value = ''
  }
}

function removeStaffMember(index) {
  const staffName = staffMembers.value[index]
  staffMembers.value.splice(index, 1)
  selectedParticipants.value = selectedParticipants.value.filter(p => 
    !(p.type === 'staff' && p.name === staffName)
  )
  updateParticipantsData()
}

function addFamilyMember() {
  if (newFamilyName.value.trim()) {
    familyMembers.value.push(newFamilyName.value.trim())
    newFamilyName.value = ''
  }
}

function removeFamilyMember(index) {
  const familyName = familyMembers.value[index]
  familyMembers.value.splice(index, 1)
  selectedParticipants.value = selectedParticipants.value.filter(p => 
    !(p.type === 'family' && p.name === familyName)
  )
  updateParticipantsData()
}

function removeParticipant(participant) {
  const index = selectedParticipants.value.findIndex(p => 
    p.type === participant.type && 
    (p.id === participant.id || p.name === participant.name)
  )
  if (index > -1) {
    selectedParticipants.value.splice(index, 1)
    updateParticipantsData()
  }
}

function updateParticipantsData() {
  form.value.participants_data = selectedParticipants.value
}

function submitForm() {
  // Validar campos obligatorios
  if (!form.value.type) {
    alert('Por favor selecciona un tipo de actividad')
    return
  }
  
  if (!form.value.subtype) {
    alert('Por favor selecciona una subcategoría')
    return
  }
  
  if (!form.value.title || form.value.title.trim() === '') {
    alert('Por favor ingresa un título para la actividad')
    return
  }
  
  if (!form.value.scheduled_at) {
    alert('Por favor selecciona una fecha y hora para la actividad')
    return
  }
  
  if (!form.value.participants) {
    alert('Por favor selecciona el tipo de participación')
    return
  }
  
  // Si es actividad recurrente, validar el día
  if (form.value.is_recurring && !form.value.recurrence_day) {
    alert('Por favor selecciona un día de la semana para actividades recurrentes')
    return
  }

  const activityData = {
    ...form.value,
    resident_id: props.residentId
  }
  
  // Limpiar campos opcionales vacíos
  if (!activityData.description || activityData.description.trim() === '') {
    activityData.description = null
  }
  
  if (!activityData.notes || activityData.notes.trim() === '') {
    activityData.notes = null
  }
  
  if (!activityData.registered_by || activityData.registered_by.trim() === '') {
    activityData.registered_by = null
  }
  
  if (activityData.scheduled_at) {
    activityData.scheduled_at = new Date(activityData.scheduled_at).toISOString()
  }
  
  if (activityData.completed_at) {
    activityData.completed_at = new Date(activityData.completed_at).toISOString()
  }
  
  emit('submit', activityData)
}

// Watch for modelValue changes (for editing)
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    form.value = {
      type: newValue.type || '',
      subtype: newValue.subtype || '',
      title: newValue.title || '',
      description: newValue.description || '',
      scheduled_at: newValue.scheduled_at ? newValue.scheduled_at.slice(0, 16) : '',
      completed_at: newValue.completed_at ? newValue.completed_at.slice(0, 16) : '',
      participants: newValue.participants || '',
      status: newValue.status || 'scheduled',
      is_recurring: newValue.is_recurring || false,
      recurrence_day: newValue.recurrence_day || '',
      notes: newValue.notes || '',
      registered_by: newValue.registered_by || ''
    }
    
    if (newValue.participants_data) {
      selectedParticipants.value = [...newValue.participants_data]
      
      staffMembers.value = selectedParticipants.value
        .filter(p => p.type === 'staff')
        .map(p => p.name)
      
      familyMembers.value = selectedParticipants.value
        .filter(p => p.type === 'family')
        .map(p => p.name)
    }
  }
}, { immediate: true })

onMounted(() => {
  if (!props.modelValue) {
    const now = new Date()
    now.setMinutes(now.getMinutes() - now.getMinutes() % 30)
    form.value.scheduled_at = now.toISOString().slice(0, 16)
  }
})
</script>

<style scoped>
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
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 2rem;
}

.modal-content h3 {
  margin: 0 0 1.5rem 0;
  color: var(--color-heading);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-dark);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--color-primary);
  outline: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.participants-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-background-soft);
  border-radius: 8px;
}

.participants-section h4 {
  margin: 0 0 1rem 0;
  color: var(--color-heading);
}

.participants-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.add-participant {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.add-participant input {
  flex: 1;
}

.add-btn-small {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--color-background);
  border-radius: 4px;
  cursor: pointer;
}

.participant-item input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.remove-btn {
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  font-size: 12px;
  margin-left: auto;
}

.selected-participants {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--color-background-mute);
  border-radius: 8px;
}

.selected-participants h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-heading);
}

.participants-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.participant-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 4px;
  font-size: 0.875rem;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 12px;
  padding: 0;
  margin-left: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--color-background-mute);
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .modal-content {
    padding: 1rem;
    width: 95%;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>