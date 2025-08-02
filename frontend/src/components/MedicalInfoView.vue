<template>
  <div class="medical-info-view">
    <div class="header">
      <h3>Información Médica</h3>
      <button @click="$emit('edit')" class="edit-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        Editar
      </button>
    </div>

    <div v-if="loading" class="loader">
      <IconSpinner :size="30" />
      <p>Cargando información médica...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadMedicalInfo" class="retry-btn">Reintentar</button>
    </div>

    <div v-else class="medical-content">
      <!-- Información de identificación -->
      <div class="info-section">
        <h4>Identificación</h4>
        <div class="info-grid">
          <div class="info-item" v-if="medicalData.document_number">
            <label>Cédula:</label>
            <span>{{ medicalData.document_number }}</span>
          </div>
          <div class="info-item" v-if="medicalData.birth_date">
            <label>Fecha de Nacimiento:</label>
            <span>{{ formatDate(medicalData.birth_date) }}</span>
          </div>
          <div class="info-item" v-if="age">
            <label>Edad:</label>
            <span>{{ age }} años</span>
          </div>
        </div>
      </div>

      <!-- Información médica -->
      <div class="info-section">
        <h4>Información Médica</h4>
        <div class="info-grid">
          <div class="info-item" v-if="medicalData.blood_type">
            <label>Grupo Sanguíneo:</label>
            <span class="blood-type">{{ medicalData.blood_type }}</span>
          </div>
        </div>

        <!-- Patologías -->
        <div class="info-item" v-if="medicalData.pathologies && medicalData.pathologies.length > 0">
          <label>Patologías:</label>
          <div class="tags-list">
            <span 
              v-for="pathology in medicalData.pathologies" 
              :key="pathology"
              class="tag pathology"
            >
              {{ pathology }}
            </span>
          </div>
        </div>

        <!-- Alergias -->
        <div class="info-item" v-if="medicalData.allergies && medicalData.allergies.length > 0">
          <label>Alergias:</label>
          <div class="tags-list">
            <span 
              v-for="allergy in medicalData.allergies" 
              :key="allergy"
              class="tag allergy"
            >
              {{ allergy }}
            </span>
          </div>
        </div>

        <!-- Historial clínico -->
        <div class="info-item" v-if="medicalData.medical_history">
          <label>Historial Clínico:</label>
          <div class="medical-history">
            {{ medicalData.medical_history }}
          </div>
        </div>
      </div>

      <!-- Mensaje si no hay información -->
      <div v-if="!hasMedicalInfo" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14,2 14,8 20,8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10,9 9,9 8,9"></polyline>
        </svg>
        <h4>Sin información médica</h4>
        <p>No se ha registrado información médica para este residente.</p>
        <button @click="$emit('edit')" class="add-btn">Agregar información médica</button>
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

const emit = defineEmits(['edit'])

const medicalData = ref({})
const loading = ref(true)
const error = ref('')

const age = computed(() => {
  if (!medicalData.value.birth_date) return null
  
  const birthDate = new Date(medicalData.value.birth_date)
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  
  return age
})

const hasMedicalInfo = computed(() => {
  return medicalData.value.document_number || 
         medicalData.value.birth_date || 
         medicalData.value.blood_type || 
         (medicalData.value.pathologies && medicalData.value.pathologies.length > 0) ||
         (medicalData.value.allergies && medicalData.value.allergies.length > 0) ||
         medicalData.value.medical_history
})

async function loadMedicalInfo() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(import.meta.env.VITE_API_URL + `/api/residents/${props.residentId}/medical-info`)
    if (!response.ok) throw new Error('No se pudo cargar la información médica')
    medicalData.value = await response.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(date)
}

onMounted(loadMedicalInfo)
</script>

<style scoped>
.medical-info-view {
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h3 {
  margin: 0;
  color: var(--color-heading);
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.edit-btn:hover {
  opacity: 0.9;
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

.medical-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.info-section {
  background: var(--color-background-soft);
  border-radius: 8px;
  padding: 1.5rem;
}

.info-section h4 {
  margin: 0 0 1rem 0;
  color: var(--color-heading);
  font-size: 1.1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-weight: 600;
  color: var(--color-text-dark);
  font-size: 0.875rem;
}

.info-item span {
  color: var(--color-text);
}

.blood-type {
  font-weight: 600;
  color: var(--color-primary);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.tag.pathology {
  background: var(--color-primary);
  color: white;
}

.tag.allergy {
  background: var(--color-danger, #dc3545);
  color: white;
}

.medical-history {
  background: var(--color-background-mute);
  padding: 1rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  white-space: pre-wrap;
  line-height: 1.5;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-light);
}

.empty-state svg {
  color: var(--color-text-light);
  margin-bottom: 1rem;
}

.empty-state h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-heading);
}

.empty-state p {
  margin: 0 0 1.5rem 0;
}

.add-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.add-btn:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>