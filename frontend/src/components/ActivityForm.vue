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
          <label for="participants">Participantes</label>
          <select v-model="form.participants" id="participants" required>
            <option value="">Selecciona participantes</option>
            <option value="Residente solo">Residente solo</option>
            <option value="Con otros residentes">Con otros residentes</option>
            <option value="Con personal">Con personal</option>
            <option value="Con familiares">Con familiares</option>
            <option value="Grupo mixto">Grupo mixto</option>
          </select>
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
  status: 'scheduled',
  is_recurring: false,
  recurrence_day: '',
  notes: '',
  registered_by: ''
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
  // Reset subtype when type changes
  form.value.subtype = ''
}

function submitForm() {
  const activityData = {
    ...form.value,
    resident_id: props.residentId
  }
  
  // Convert datetime strings to ISO format
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
  }
}, { immediate: true })

// Set default scheduled_at to current date/time
onMounted(() => {
  if (!props.modelValue) {
    const now = new Date()
    now.setMinutes(now.getMinutes() - now.getMinutes() % 30) // Round to nearest 30 minutes
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

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.cancel-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--color-background-mute);
}

.submit-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background: var(--color-primary-dark);
}

@media (max-width: 640px) {
  .modal-content {
    padding: 1rem;
    width: 95%;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>