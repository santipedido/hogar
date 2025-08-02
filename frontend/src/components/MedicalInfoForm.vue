<template>
  <div class="medical-info-form">
    <h3>Información Médica</h3>
    
    <form @submit.prevent="handleSubmit">
      <!-- Información de identificación -->
      <div class="form-section">
        <h4>Identificación</h4>
        
        <div class="form-group">
          <label for="documentNumber">Número de Cédula</label>
          <input
            id="documentNumber"
            v-model="formData.document_number"
            type="text"
            placeholder="Ej: 1234567890"
            maxlength="15"
          >
        </div>

        <div class="form-group">
          <label for="birthDate">Fecha de Nacimiento</label>
          <input
            id="birthDate"
            v-model="formData.birth_date"
            type="date"
            :max="maxDate"
          >
        </div>

        <div class="form-group" v-if="age">
          <label>Edad</label>
          <div class="age-display">{{ age }} años</div>
        </div>
      </div>

      <!-- Información médica -->
      <div class="form-section">
        <h4>Información Médica</h4>
        
        <div class="form-group">
          <label for="bloodType">Grupo Sanguíneo</label>
          <select id="bloodType" v-model="formData.blood_type">
            <option value="">Selecciona grupo sanguíneo</option>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
          </select>
        </div>

        <div class="form-group">
          <label for="pathologies">Patologías</label>
          <div class="array-input">
            <div class="input-with-button">
              <input
                id="pathologies"
                v-model="newPathology"
                type="text"
                placeholder="Agregar patología"
                @keyup.enter="addPathology"
              >
              <button type="button" @click="addPathology" class="add-btn">+</button>
            </div>
            <div class="array-list" v-if="formData.pathologies && formData.pathologies.length > 0">
              <div 
                v-for="(pathology, index) in formData.pathologies" 
                :key="index"
                class="array-item"
              >
                <span>{{ pathology }}</span>
                <button type="button" @click="removePathology(index)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="allergies">Alergias</label>
          <div class="array-input">
            <div class="input-with-button">
              <input
                id="allergies"
                v-model="newAllergy"
                type="text"
                placeholder="Agregar alergia"
                @keyup.enter="addAllergy"
              >
              <button type="button" @click="addAllergy" class="add-btn">+</button>
            </div>
            <div class="array-list" v-if="formData.allergies && formData.allergies.length > 0">
              <div 
                v-for="(allergy, index) in formData.allergies" 
                :key="index"
                class="array-item"
              >
                <span>{{ allergy }}</span>
                <button type="button" @click="removeAllergy(index)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="medicalHistory">Historial Clínico Básico</label>
          <textarea
            id="medicalHistory"
            v-model="formData.medical_history"
            rows="4"
            placeholder="Información médica relevante, procedimientos, condiciones especiales..."
          ></textarea>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" @click="$emit('cancel')" class="cancel-btn">Cancelar</button>
        <button type="submit" class="submit-btn">{{ isEdit ? 'Actualizar' : 'Guardar' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
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

const formData = ref({
  document_number: '',
  birth_date: '',
  blood_type: '',
  pathologies: [],
  allergies: [],
  medical_history: '',
  ...props.modelValue
})

const newPathology = ref('')
const newAllergy = ref('')

// Calcular fecha máxima (hoy)
const maxDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// Calcular edad
const age = computed(() => {
  if (!formData.value.birth_date) return null
  
  const birthDate = new Date(formData.value.birth_date)
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  
  return age
})

function addPathology() {
  if (newPathology.value.trim()) {
    if (!formData.value.pathologies) {
      formData.value.pathologies = []
    }
    formData.value.pathologies.push(newPathology.value.trim())
    newPathology.value = ''
  }
}

function removePathology(index) {
  formData.value.pathologies.splice(index, 1)
}

function addAllergy() {
  if (newAllergy.value.trim()) {
    if (!formData.value.allergies) {
      formData.value.allergies = []
    }
    formData.value.allergies.push(newAllergy.value.trim())
    newAllergy.value = ''
  }
}

function removeAllergy(index) {
  formData.value.allergies.splice(index, 1)
}

function handleSubmit() {
  // Validar campos obligatorios si es necesario
  const submitData = { ...formData.value }
  
  // Limpiar arrays vacíos
  if (!submitData.pathologies || submitData.pathologies.length === 0) {
    submitData.pathologies = []
  }
  if (!submitData.allergies || submitData.allergies.length === 0) {
    submitData.allergies = []
  }
  
  // Limpiar campos vacíos
  Object.keys(submitData).forEach(key => {
    if (submitData[key] === '') {
      submitData[key] = null
    }
  })
  
  emit('submit', submitData)
}

// Watch for modelValue changes (for editing)
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    formData.value = {
      document_number: newValue.document_number || '',
      birth_date: newValue.birth_date || '',
      blood_type: newValue.blood_type || '',
      pathologies: newValue.pathologies || [],
      allergies: newValue.allergies || [],
      medical_history: newValue.medical_history || '',
      ...newValue
    }
  }
}, { immediate: true })

onMounted(async () => {
  // Si es modo edición, cargar datos médicos
  if (props.isEdit && props.residentId) {
    try {
      const response = await fetch(import.meta.env.VITE_API_URL + `/api/residents/${props.residentId}/medical-info`)
      if (response.ok) {
        const medicalData = await response.json()
        formData.value = {
          document_number: medicalData.document_number || '',
          birth_date: medicalData.birth_date || '',
          blood_type: medicalData.blood_type || '',
          pathologies: medicalData.pathologies || [],
          allergies: medicalData.allergies || [],
          medical_history: medicalData.medical_history || ''
        }
      }
    } catch (error) {
      console.error('Error loading medical info:', error)
    }
  }
})
</script>

<style scoped>
.medical-info-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.medical-info-form h3 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-heading);
}

.form-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--color-background-soft);
  border-radius: 8px;
}

.form-section h4 {
  margin: 0 0 1rem 0;
  color: var(--color-heading);
  font-size: 1.1rem;
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

.age-display {
  padding: 0.75rem;
  background: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-weight: 600;
  color: var(--color-primary);
}

.array-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-with-button {
  display: flex;
  gap: 0.5rem;
}

.input-with-button input {
  flex: 1;
}

.add-btn {
  padding: 0.75rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
}

.array-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.array-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
}

.remove-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.remove-btn:hover {
  background: rgba(255, 255, 255, 0.2);
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
  .medical-info-form {
    padding: 0.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>