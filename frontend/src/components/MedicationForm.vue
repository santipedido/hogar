<template>
  <div class="medication-form">
    <h3>{{ isEdit ? 'Editar' : 'Nueva' }} Medicación</h3>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="med_name">Nombre del medicamento *</label>
        <input
          id="med_name"
          v-model="formData.med_name"
          type="text"
          required
          placeholder="Nombre del medicamento"
        >
      </div>

      <div class="form-group">
        <label for="dosage">Dosis *</label>
        <input
          id="dosage"
          v-model="formData.dosage"
          type="text"
          required
          placeholder="Ej: 1 tableta, 5ml, etc."
        >
      </div>

      <div class="form-group">
        <label for="frequency">Frecuencia *</label>
        <select 
          id="frequency" 
          v-model="formData.frequency" 
          required
        >
          <option value="">Seleccionar frecuencia</option>
          <option value="una vez al día">Una vez al día</option>
          <option value="dos veces al día">Dos veces al día</option>
          <option value="tres veces al día">Tres veces al día</option>
          <option value="cada 8 horas">Cada 8 horas</option>
          <option value="cada 12 horas">Cada 12 horas</option>
          <option value="según necesidad">Según necesidad</option>
          <option value="otro">Otro</option>
        </select>
      </div>

      <div class="form-group">
        <label for="scheduled_time">Hora programada</label>
        <input 
          id="scheduled_time" 
          v-model="formData.scheduled_time" 
          type="time"
        >
      </div>

      <div class="form-group">
        <label for="notes">Notas</label>
        <textarea 
          id="notes" 
          v-model="formData.notes"
          rows="3"
          placeholder="Instrucciones especiales, efectos secundarios, etc."
        ></textarea>
      </div>

      <div class="actions">
        <button type="submit">{{ isEdit ? 'Guardar cambios' : 'Agregar' }}</button>
        <button type="button" class="secondary" @click="closeForm">Cancelar</button>
      </div>
    </form>
  </div>
</template>
 
<script setup>
import { ref } from 'vue'

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

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const formData = ref({
  med_name: '',
  dosage: '',
  frequency: '',
  scheduled_time: '',
  notes: '',
  resident_id: props.residentId,
  ...props.modelValue
})

function handleSubmit() {
  emit('submit', { ...formData.value })
}

function closeForm() {
  emit('cancel')
}
</script> 

<style scoped>
.medication-form {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-background-soft);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
}

.medication-form h3 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-text-dark);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--color-text-dark);
  font-weight: 500;
}

input, select, textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-text-dark);
  background-color: var(--color-background-soft);
  transition: border-color 0.2s;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.2);
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

button {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

button[type="submit"] {
  background: var(--color-primary);
  color: white;
}

button[type="submit"]:hover {
  background: var(--color-primary-dark, #3b82f6);
}

button.secondary {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

button.secondary:hover {
  background: var(--color-background-mute);
}
</style> 