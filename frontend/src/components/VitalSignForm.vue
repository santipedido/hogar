<template>
  <div class="card vital-sign-form">
    <h2>{{ isEditing ? 'Editar' : 'Registrar' }} Signo Vital</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="resident">Residente *</label>
        <select 
          id="resident" 
          v-model="form.resident_id" 
          required
          class="form-control"
          :disabled="isEditing"
        >
          <option value="">Seleccionar residente</option>
          <option 
            v-for="resident in residents" 
            :key="resident.id" 
            :value="resident.id"
          >
            {{ resident.name }} {{ resident.last_name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="type">Tipo de Signo Vital *</label>
        <select 
          id="type" 
          v-model="form.type" 
          required
          class="form-control"
          @change="handleTypeChange"
        >
          <option value="">Seleccionar tipo</option>
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

      <!-- Campos específicos para presión arterial -->
      <div v-if="form.type === 'presion'" class="pressure-fields">
        <div class="form-row">
          <div class="form-group">
            <label for="systolic">Presión Sistólica (mmHg) *</label>
            <input 
              type="number" 
              id="systolic" 
              v-model="form.systolic" 
              required
              min="50" 
              max="300"
              class="form-control"
              placeholder="120"
            />
          </div>
          <div class="form-group">
            <label for="diastolic">Presión Diastólica (mmHg) *</label>
            <input 
              type="number" 
              id="diastolic" 
              v-model="form.diastolic" 
              required
              min="30" 
              max="200"
              class="form-control"
              placeholder="80"
            />
          </div>
        </div>
      </div>

      <!-- Campo de valor para otros tipos -->
      <div v-else-if="form.type && form.type !== 'presion'" class="form-group">
        <label for="value">Valor *</label>
        <div class="value-input-group">
          <input 
            type="number" 
            id="value" 
            v-model="form.value" 
            required
            step="0.1"
            class="form-control"
            :placeholder="getPlaceholder()"
          />
          <input 
            type="text" 
            v-model="form.unit" 
            class="form-control unit-input"
            :placeholder="getUnit()"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="taken_at">Fecha y Hora de Toma *</label>
        <input 
          type="datetime-local" 
          id="taken_at" 
          v-model="form.taken_at" 
          required
          class="form-control"
        />
      </div>

      <div class="form-group">
        <label for="taken_by">Tomado por</label>
        <input 
          type="text" 
          id="taken_by" 
          v-model="form.taken_by" 
          class="form-control"
          placeholder="Nombre del personal"
        />
      </div>

      <div class="form-group">
        <label for="notes">Notas</label>
        <textarea 
          id="notes" 
          v-model="form.notes" 
          class="form-control"
          rows="3"
          placeholder="Observaciones adicionales..."
        ></textarea>
      </div>

      <div class="form-actions">
        <button 
          type="button" 
          @click="$emit('cancel')" 
          class="secondary"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          :disabled="loading"
        >
          <span v-if="loading">Guardando...</span>
          <span v-else>{{ isEditing ? 'Actualizar' : 'Guardar' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { supabase } from '../api/supabase'

const props = defineProps({
  vitalSign: {
    type: Object,
    default: null
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['saved', 'cancel'])

const loading = ref(false)
const residents = ref([])

const form = reactive({
  resident_id: '',
  type: '',
  value: null,
  unit: '',
  systolic: null,
  diastolic: null,
  taken_at: '',
  notes: '',
  taken_by: ''
})

const getPlaceholder = () => {
  const placeholders = {
    temperatura: '36.5',
    fc: '72',
    saturacion: '98',
    peso: '70',
    altura: '165',
    glucosa: '120',
    otro: 'Valor'
  }
  return placeholders[form.type] || 'Valor'
}

const getUnit = () => {
  const units = {
    temperatura: '°C',
    fc: 'lpm',
    saturacion: '%',
    peso: 'kg',
    altura: 'cm',
    glucosa: 'mg/dL',
    otro: 'unidad'
  }
  return units[form.type] || 'unidad'
}

const handleTypeChange = () => {
  // Limpiar campos específicos al cambiar tipo
  form.value = null
  form.unit = ''
  form.systolic = null
  form.diastolic = null
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

const handleSubmit = async () => {
  loading.value = true
  
  try {
    const formData = { ...form }
    
    // Limpiar campos no necesarios según el tipo
    if (form.type === 'presion') {
      delete formData.value
      delete formData.unit
    } else {
      delete formData.systolic
      delete formData.diastolic
    }

    // Convertir fecha a ISO string
    if (formData.taken_at) {
      formData.taken_at = new Date(formData.taken_at).toISOString()
    }

    let result
    if (props.isEditing && props.vitalSign) {
      const { data, error } = await supabase
        .from('vital_signs')
        .update(formData)
        .eq('id', props.vitalSign.id)
        .select()
        .single()
      
      if (error) throw error
      result = data
    } else {
      const { data, error } = await supabase
        .from('vital_signs')
        .insert(formData)
        .select()
        .single()
      
      if (error) throw error
      result = data
    }

    emit('saved', result)
  } catch (error) {
    console.error('Error guardando signo vital:', error)
    alert('Error al guardar el signo vital')
  } finally {
    loading.value = false
  }
}

const initializeForm = () => {
  if (props.isEditing && props.vitalSign) {
    Object.assign(form, {
      resident_id: props.vitalSign.resident_id,
      type: props.vitalSign.type,
      value: props.vitalSign.value,
      unit: props.vitalSign.unit,
      systolic: props.vitalSign.systolic,
      diastolic: props.vitalSign.diastolic,
      taken_at: props.vitalSign.taken_at ? new Date(props.vitalSign.taken_at).toISOString().slice(0, 16) : '',
      notes: props.vitalSign.notes || '',
      taken_by: props.vitalSign.taken_by || ''
    })
  } else {
    // Formulario nuevo - establecer fecha actual
    form.taken_at = new Date().toISOString().slice(0, 16)
  }
}

onMounted(() => {
  loadResidents()
  initializeForm()
})
</script>

<style scoped>
.vital-sign-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text);
}

.value-input-group {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
}

.unit-input {
  min-width: 80px;
}

.pressure-fields {
  background: var(--color-bg);
  padding: 1rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .value-input-group {
    grid-template-columns: 1fr;
  }
}
</style> 