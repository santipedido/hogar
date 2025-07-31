<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h3>{{ isEdit ? 'Editar' : 'Agregar' }} Signo Vital</h3>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="type">Tipo</label>
          <select v-model="form.type" id="type" required @change="onTypeChange">
            <option value="">Selecciona tipo</option>
            <option value="Temperatura">Temperatura</option>
            <option value="Frecuencia Cardíaca">Frecuencia Cardíaca</option>
            <option value="Frecuencia Respiratoria">Frecuencia Respiratoria</option>
            <option value="Presión Arterial">Presión Arterial</option>
            <option value="Saturación O2">Saturación O2</option>
            <option value="Glucemia">Glucemia</option>
          </select>
        </div>
        <div class="form-group" v-if="form.type === 'Presión Arterial'">
          <label for="systolic">Sistólica</label>
          <input type="number" step="0.1" v-model.number="form.systolic" id="systolic" required />
          <label for="diastolic">Diastólica</label>
          <input type="number" step="0.1" v-model.number="form.diastolic" id="diastolic" required />
          <label for="unit">Unidad</label>
          <input type="text" v-model="form.unit" id="unit" placeholder="mmHg" />
        </div>
        <div class="form-group" v-else>
          <label for="value">Valor</label>
          <input type="number" step="0.1" v-model.number="form.value" id="value" required />
          <label for="unit">Unidad</label>
          <input type="text" v-model="form.unit" id="unit" placeholder="Ej: °C, bpm, %" />
        </div>
        <div class="form-group">
          <label for="taken_at">Fecha y hora</label>
          <input type="datetime-local" v-model="form.taken_at" id="taken_at" required />
        </div>
        <div class="form-group">
          <label for="taken_by">Responsable</label>
          <input type="text" v-model="form.taken_by" id="taken_by" />
        </div>
        <div class="form-group">
          <label for="notes">Notas</label>
          <textarea v-model="form.notes" id="notes" rows="2"></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="save-btn">Guardar</button>
          <button type="button" @click="$emit('cancel')" class="cancel-btn">Cancelar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

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

const defaultForm = {
  type: '',
  value: null,
  unit: '',
  systolic: null,
  diastolic: null,
  taken_at: '',
  notes: '',
  taken_by: ''
}

const form = ref({ ...defaultForm })

watch(() => props.modelValue, (val) => {
  if (val) {
    form.value = { ...defaultForm, ...val }
    if (val.taken_at) {
      // Formatear a local para input type="datetime-local"
      form.value.taken_at = val.taken_at.slice(0, 16)
    }
  } else {
    form.value = { ...defaultForm }
  }
}, { immediate: true })

function onTypeChange() {
  if (form.value.type !== 'Presión Arterial') {
    form.value.systolic = null
    form.value.diastolic = null
  } else {
    form.value.value = null
  }
}

function submitForm() {
  // Validación básica
  if (!form.value.type || !form.value.taken_at) return
  if (form.value.type === 'Presión Arterial') {
    if (!form.value.systolic || !form.value.diastolic) return
  } else {
    if (form.value.value === null || form.value.value === undefined) return
  }
  // Formatear fecha a ISO
  const data = { ...form.value, taken_at: new Date(form.value.taken_at).toISOString() }
  emit('submit', data)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  padding: 2rem;
  border-radius: 10px;
  min-width: 320px;
  max-width: 90vw;
  box-shadow: 0 2px 16px rgba(0,0,0,0.15);
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.3rem;
  font-weight: 500;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
.save-btn {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
.cancel-btn {
  background: #eee;
  color: #333;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
}
</style> 