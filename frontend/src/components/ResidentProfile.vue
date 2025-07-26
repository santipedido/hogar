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
          <p class="coming-soon">Próximamente: Registro de medicación</p>
        </div>

        <!-- Signos Vitales -->
        <div v-if="activeTab === 'vitals'" class="tab-panel">
          <p class="coming-soon">Próximamente: Registro de signos vitales</p>
        </div>

        <!-- Actividades -->
        <div v-if="activeTab === 'activities'" class="tab-panel">
          <p class="coming-soon">Próximamente: Registro de actividades</p>
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

const tabs = [
  { id: 'contacts', name: 'Contactos Familiares' },
  { id: 'medication', name: 'Medicación' },
  { id: 'vitals', name: 'Signos Vitales' },
  { id: 'activities', name: 'Actividades' }
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
    if (!res.ok) throw new Error('No se pudo cargar el perfil')
    resident.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadResident)
</script>

<style scoped>
.resident-profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.loader, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.error {
  color: var(--color-danger, #dc3545);
}

.retry-btn {
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

.basic-info {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: var(--color-background-soft);
  border-radius: 12px;
  margin-bottom: 2rem;
}

.photo-container {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  overflow: hidden;
  background: var(--color-background-mute);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--color-primary);
}

.photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  color: var(--color-text-light);
  opacity: 0.5;
}

.info {
  flex: 1;
}

.info h2 {
  margin: 0 0 0.5rem 0;
  color: var(--color-heading);
}

.status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status.independent {
  color: #10B981;
  background: rgba(16, 185, 129, 0.1);
}

.status.semi-dependent {
  color: #F59E0B;
  background: rgba(245, 158, 11, 0.1);
}

.admission-date {
  margin: 0.5rem 0 0 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.edit-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 2rem;
  overflow-x: auto;
  padding-bottom: 1px;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.875rem;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--color-primary);
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  background: var(--color-background-soft);
  border-radius: 12px;
  min-height: 400px;
}

.coming-soon {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-light);
  font-style: italic;
}

@media (max-width: 768px) {
  .basic-info {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }

  .tabs {
    padding: 0 1rem;
  }
}
</style> 