<template>
  <div class="vital-signs-list">
    <h2>Signos Vitales</h2>
    <button @click="showForm = true" class="add-btn">Agregar signo vital</button>

    <!-- Filtros -->
    <div class="filters card">
      <div class="filter-group">
        <label for="resident-filter">Residente:</label>
        <select 
          id="resident-filter" 
          v-model="filters.resident_id"
          @change="loadVitalSigns"
        >
          <option value="">Todos los residentes</option>
          <option 
            v-for="resident in residents" 
            :key="resident.id" 
            :value="resident.id"
          >
            {{ resident.name }} {{ resident.last_name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="type-filter">Tipo:</label>
        <select 
          id="type-filter" 
          v-model="filters.type"
          @change="loadVitalSigns"
        >
          <option value="">Todos los tipos</option>
          <option value="presion">Presión Arterial</option>
          <option value="temperatura">Temperatura</option>
          <option value="fc">Frecuencia Cardíaca</option>
          <option value="saturacion">Saturación de Oxígeno</option>
          <option value="peso">Peso</option>
          <option value="altura">Altura</option>
          <option value="glucosa">Glucosa</option>
          <option value="otro">Otro</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="date-filter">Fecha:</label>
        <input 
          type="date" 
          id="date-filter" 
          v-model="filters.date"
          @change="loadVitalSigns"
        />
      </div>
    </div>

    <!-- Lista de signos vitales -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Cargando signos vitales...</p>
    </div>

    <div v-else-if="vitalSigns.length === 0" class="empty">
      No hay signos vitales registrados.
    </div>

    <div v-else>
      <div class="cards">
        <div 
          v-for="vitalSign in vitalSigns" 
          :key="vitalSign.id" 
          class="card vital-sign-card"
        >
        <div class="vital-sign-header">
          <div class="resident-info">
            <h4>{{ getResidentName(vitalSign.resident_id) }}</h4>
            <span class="type-badge" :class="getTypeClass(vitalSign.type)">
              {{ getTypeLabel(vitalSign.type) }}
            </span>
          </div>
          <div class="actions">
            <button 
              @click="editVitalSign(vitalSign)" 
              class="edit-btn"
            >
              Editar
            </button>
            <button 
              @click="deleteVitalSign(vitalSign.id)" 
              class="delete-btn"
            >
              Eliminar
            </button>
          </div>
        </div>

        <div class="vital-sign-value">
          <div v-if="vitalSign.type === 'presion'" class="pressure-value">
            <span class="value">{{ vitalSign.systolic }}/{{ vitalSign.diastolic }}</span>
            <span class="unit">mmHg</span>
          </div>
          <div v-else class="regular-value">
            <span class="value">{{ vitalSign.value }}</span>
            <span class="unit">{{ vitalSign.unit }}</span>
          </div>
        </div>

        <div class="vital-sign-details">
          <div class="detail">
            <span class="label">Fecha:</span>
            <span>{{ formatDate(vitalSign.taken_at) }}</span>
          </div>
          <div v-if="vitalSign.taken_by" class="detail">
            <span class="label">Tomado por:</span>
            <span>{{ vitalSign.taken_by }}</span>
          </div>
          <div v-if="vitalSign.notes" class="detail">
            <span class="label">Notas:</span>
            <span>{{ vitalSign.notes }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal del formulario -->
    <div v-if="showForm" class="modal-overlay" @click="closeForm">
      <div class="modal-content" @click.stop>
        <VitalSignForm 
          :vital-sign="editingVitalSign"
          :is-editing="!!editingVitalSign"
          @saved="onVitalSignSaved"
          @cancel="closeForm"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { supabase } from '../api/supabase'
import VitalSignForm from './VitalSignForm.vue'

const loading = ref(false)
const showForm = ref(false)
const editingVitalSign = ref(null)
const vitalSigns = ref([])
const residents = ref([])

const filters = reactive({
  resident_id: '',
  type: '',
  date: ''
})

const getTypeLabel = (type) => {
  const labels = {
    presion: 'Presión Arterial',
    temperatura: 'Temperatura',
    fc: 'Frecuencia Cardíaca',
    saturacion: 'Saturación O₂',
    peso: 'Peso',
    altura: 'Altura',
    glucosa: 'Glucosa',
    otro: 'Otro'
  }
  return labels[type] || type
}

const getTypeClass = (type) => {
  const classes = {
    presion: 'type-pressure',
    temperatura: 'type-temperature',
    fc: 'type-heart',
    saturacion: 'type-oxygen',
    peso: 'type-weight',
    altura: 'type-height',
    glucosa: 'type-glucose',
    otro: 'type-other'
  }
  return classes[type] || 'type-other'
}

const getResidentName = (residentId) => {
  const resident = residents.value.find(r => r.id === residentId)
  return resident ? `${resident.name} ${resident.last_name}` : 'Residente no encontrado'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadResidents = async () => {
  try {
    const { data, error } = await supabase
      .from('residents')
      .select('id, name, last_name')
      .order('name')
    
    if (error) throw error
    residents.value = data || []
  } catch (error) {
    console.error('Error cargando residentes:', error)
  }
}

const loadVitalSigns = async () => {
  loading.value = true
  
  try {
    let query = supabase
      .from('vital_signs')
      .select('*')
      .order('taken_at', { ascending: false })

    if (filters.resident_id) {
      query = query.eq('resident_id', filters.resident_id)
    }
    
    if (filters.type) {
      query = query.eq('type', filters.type)
    }
    
    if (filters.date) {
      const startDate = new Date(filters.date)
      const endDate = new Date(filters.date)
      endDate.setDate(endDate.getDate() + 1)
      
      query = query
        .gte('taken_at', startDate.toISOString())
        .lt('taken_at', endDate.toISOString())
    }

    const { data, error } = await query
    
    if (error) throw error
    vitalSigns.value = data || []
  } catch (error) {
    console.error('Error cargando signos vitales:', error)
    alert('Error al cargar los signos vitales')
  } finally {
    loading.value = false
  }
}

const editVitalSign = (vitalSign) => {
  editingVitalSign.value = vitalSign
  showForm.value = true
}

const deleteVitalSign = async (id) => {
  if (!confirm('¿Estás seguro de que quieres eliminar este signo vital?')) {
    return
  }

  try {
    const { error } = await supabase
      .from('vital_signs')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    
    await loadVitalSigns()
  } catch (error) {
    console.error('Error eliminando signo vital:', error)
    alert('Error al eliminar el signo vital')
  }
}

const onVitalSignSaved = async (vitalSign) => {
  showForm.value = false
  editingVitalSign.value = null
  await loadVitalSigns()
}

const closeForm = () => {
  showForm.value = false
  editingVitalSign.value = null
}

onMounted(() => {
  loadResidents()
  loadVitalSigns()
})
</script>

<style scoped>
.vital-signs-list {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.875rem;
}

.vital-sign-card {
  cursor: pointer;
  transition: background-color 0.2s;
}

.vital-sign-card:hover {
  background: var(--color-bg);
}

.vital-sign-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.resident-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-text);
}

.type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.type-pressure { background: var(--color-danger); }
.type-temperature { background: var(--color-accent); }
.type-heart { background: #e83e8c; }
.type-oxygen { background: var(--color-secondary); }
.type-weight { background: #6f42c1; }
.type-height { background: var(--color-primary); }
.type-glucose { background: #28a745; }
.type-other { background: #6c757d; }

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  width: 100%;
  justify-content: center;
}

.edit-btn, .delete-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s;
  flex: 1;
  max-width: 120px;
}

.edit-btn {
  background: var(--color-primary);
  color: white;
  border: none;
}

.edit-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
}

.delete-btn {
  background: transparent;
  border: 1px solid var(--color-danger);
  color: var(--color-danger);
}

.delete-btn:hover {
  background: var(--color-danger);
  color: white;
}

.vital-sign-value {
  margin-bottom: 1rem;
}

.pressure-value,
.regular-value {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.unit {
  font-size: 0.875rem;
  color: #666;
}

.vital-sign-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail {
  display: flex;
  gap: 0.5rem;
}

.label {
  font-weight: 600;
  color: var(--color-text);
  min-width: 80px;
}

.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #666;
}

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
  background: white;
  border-radius: var(--radius);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

@media (max-width: 640px) {
  .vital-signs-list {
    padding: 1rem;
  }
  
  .filters {
    grid-template-columns: 1fr;
  }
  
  .actions {
    flex-direction: column;
    width: 100%;
  }
  
  .edit-btn, .delete-btn {
    max-width: 100%;
  }
}
</style> 