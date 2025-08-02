<template>
  <div class="resident-profile">
    <div v-if="loading" class="loader">
      <IconSpinner :size="50" />
      <p>Cargando perfil...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadResident" class="retry-btn">Reintentar</button>
    </div>
    <div v-else class="profile-content">
      <!-- Información básica del residente -->
      <div class="basic-info">
        <div class="photo-container">
          <img 
            v-if="resident.photo_url" 
            :src="resident.photo_url" 
            :alt="'Foto de ' + resident.name" 
            class="photo"
          />
          <IconUserPlaceholder v-else class="photo-placeholder" />
        </div>
        <div class="info">
          <h2>{{ resident.name }}</h2>
          <span :class="['status', resident.status]">
            {{ resident.status === 'independent' ? 'Independiente' : 'Semidependiente' }}
          </span>
          <p v-if="resident.admission_date" class="admission-date">
            Fecha de ingreso: {{ formatDate(resident.admission_date) }}
          </p>
        </div>
        <button @click="$emit('edit')" class="edit-btn">Editar información</button>
      </div>

      <!-- Pestañas de navegación -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- Contenido de las pestañas -->
      <div class="tab-content">
        <!-- Contactos Familiares -->
        <div v-if="activeTab === 'contacts'" class="tab-panel">
          <FamilyContactList :residentId="resident.id" />
        </div>

        <!-- Medicación -->
        <div v-if="activeTab === 'medication'" class="tab-panel">
          <MedicationList :residentId="resident.id" />
        </div>

        <!-- Signos Vitales -->
        <div v-if="activeTab === 'vitals'" class="tab-panel">
          <VitalSignsList :residentId="resident.id" />
        </div>

        <!-- Información Médica -->
        <div v-if="activeTab === 'medical'" class="tab-panel">
          <MedicalInfoView 
            v-if="!showMedicalForm"
            :residentId="resident.id"
            @edit="showMedicalForm = true"
          />
          <MedicalInfoForm
            v-else
            :residentId="resident.id"
            :isEdit="true"
            @submit="handleMedicalSubmit"
            @cancel="showMedicalForm = false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import IconSpinner from './icons/IconSpinner.vue'
import IconUserPlaceholder from './icons/IconUserPlaceholder.vue'
import FamilyContactList from './FamilyContactList.vue'
import MedicationList from './MedicationList.vue'
import VitalSignsList from './VitalSignsList.vue'
import MedicalInfoView from './MedicalInfoView.vue'
import MedicalInfoForm from './MedicalInfoForm.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['edit'])

const resident = ref({})
const loading = ref(true)
const error = ref('')
const activeTab = ref('contacts')
const showMedicalForm = ref(false)

const tabs = [
  { id: 'contacts', name: 'Contactos Familiares' },
  { id: 'medication', name: 'Medicación' },
  { id: 'vitals', name: 'Signos Vitales' },
  { id: 'medical', name: 'Información Médica' }
]

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(date)
}

async function loadResident() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/residents/${props.residentId}`)
    if (!res.ok) throw new Error('No se pudo cargar el residente')
    resident.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleMedicalSubmit(medicalData) {
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/residents/${props.residentId}/medical-info`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(medicalData)
    })
    
    if (!res.ok) throw new Error('No se pudo actualizar la información médica')
    
    showMedicalForm.value = false
    // Recargar el residente para actualizar los datos
    await loadResident()
  } catch (e) {
    alert(e.message)
  }
}

onMounted(loadResident)
</script>

<style scoped>
.resident-profile {
  max-width: 1200px;
  margin: 0 auto;
}

.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
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

.retry-btn:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

.profile-content {
  background: var(--color-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.basic-info {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
}

.photo-container {
  position: relative;
}

.photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--color-background);
  box-shadow: var(--shadow-md);
}

.photo-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--color-background-mute);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid var(--color-background);
  box-shadow: var(--shadow-md);
}

.info {
  flex: 1;
}

.info h2 {
  margin: 0 0 0.5rem 0;
  color: var(--color-heading);
  font-size: 1.75rem;
}

.status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.status.independent {
  background: var(--color-success, #28a745);
  color: white;
}

.status.semidependent {
  background: var(--color-warning, #ffc107);
  color: var(--color-text-dark);
}

.admission-date {
  margin: 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.edit-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
}

.tabs {
  display: flex;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  flex: 1;
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  color: var(--color-text-light);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.tab-btn:hover {
  background: var(--color-background-mute);
  color: var(--color-text);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  background: var(--color-background-soft);
}

.tab-content {
  min-height: 400px;
}

.tab-panel {
  padding: 0;
}

.coming-soon {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text-light);
  font-style: italic;
}

@media (max-width: 768px) {
  .basic-info {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    text-align: center;
  }
}
</style> 