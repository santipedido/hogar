<template>
  <div class="vital-signs-view">
    <div class="header">
      <h2>Gestión de Signos Vitales</h2>
    </div>

    <div class="content">
      <div class="resident-selector">
        <h3>Seleccionar Residente</h3>
        <div v-if="loadingResidents" class="loader">
          <IconSpinner :size="30" />
          <span>Cargando residentes...</span>
        </div>
        <div v-else-if="residentsError" class="error">
          <p>{{ residentsError }}</p>
          <button @click="fetchResidents" class="retry-btn">Reintentar</button>
        </div>
        <div v-else>
          <select v-model="selectedResidentId" @change="onResidentChange" class="resident-select">
            <option value="">Selecciona un residente</option>
            <option v-for="resident in residents" :key="resident.id" :value="resident.id">
              {{ resident.name }}
            </option>
          </select>
        </div>
      </div>

      <div v-if="selectedResidentId" class="vital-signs-section">
        <VitalSignsList :residentId="selectedResidentId" />
      </div>

      <div v-else class="no-selection">
        <p>Selecciona un residente para ver y gestionar sus signos vitales.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VitalSignsList from '../components/VitalSignsList.vue'
import IconSpinner from '../components/icons/IconSpinner.vue'

const residents = ref([])
const loadingResidents = ref(true)
const residentsError = ref('')
const selectedResidentId = ref('')

async function fetchResidents() {
  loadingResidents.value = true
  residentsError.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + '/api/residents/')
    if (!res.ok) throw new Error('No se pudo cargar la lista de residentes')
    residents.value = await res.json()
  } catch (e) {
    residentsError.value = e.message
  } finally {
    loadingResidents.value = false
  }
}

function onResidentChange() {
  // El componente VitalSignsList se encargará de cargar los datos del nuevo residente
}

onMounted(fetchResidents)
</script>

<style scoped>
.vital-signs-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
  text-align: center;
}

.header h2 {
  color: #2c3e50;
  font-size: 2rem;
  margin: 0;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.resident-selector {
  background: #fff;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.resident-selector h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.loader {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
}

.error {
  color: #e74c3c;
}

.retry-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  margin-left: 1rem;
}

.retry-btn:hover {
  background: #2980b9;
}

.resident-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
}

.resident-select:focus {
  outline: none;
  border-color: #3498db;
}

.vital-signs-section {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
}

.no-selection {
  text-align: center;
  padding: 3rem;
  color: #666;
  background: #f8f9fa;
  border-radius: 10px;
  border: 2px dashed #ddd;
}

@media (max-width: 768px) {
  .vital-signs-view {
    padding: 1rem;
  }
  
  .header h2 {
    font-size: 1.5rem;
  }
}
</style> 