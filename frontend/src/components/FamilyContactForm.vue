<template>
  <div class="contact-form">
    <h3>{{ isEdit ? 'Editar' : 'Nuevo' }} Contacto Familiar</h3>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">Nombre completo *</label>
        <input
          id="name"
          v-model="formData.name"
          type="text"
          required
          placeholder="Nombre y apellidos"
        >
      </div>

      <div class="form-group">
        <label for="relationship">Parentesco *</label>
        <select 
          id="relationship" 
          v-model="formData.relationship" 
          required
        >
          <option value="hijo/a">Hijo/a</option>
          <option value="esposo/a">Esposo/a</option>
          <option value="hermano/a">Hermano/a</option>
          <option value="sobrino/a">Sobrino/a</option>
          <option value="nieto/a">Nieto/a</option>
          <option value="otro">Otro</option>
        </select>
      </div>

      <div class="form-group">
        <label for="phone">Teléfono *</label>
        <input 
          id="phone" 
          v-model="formData.phone" 
          type="tel"
          required
          placeholder="Número de teléfono"
        >
      </div>

      <div class="form-group">
        <label for="address">Dirección</label>
        <input 
          id="address" 
          v-model="formData.address" 
          type="text"
          placeholder="Dirección completa"
        >
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            v-model="formData.is_primary"
          >
          Contacto principal
        </label>
      </div>

      <div class="form-group">
        <label for="notes">Notas</label>
        <textarea 
          id="notes" 
          v-model="formData.notes"
          rows="3"
          placeholder="Información adicional"
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
  name: '',
  relationship: '',
  phone: '',
  address: '',
  is_primary: false,
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
.contact-form {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-background-soft);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
}

.contact-form h3 {
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

input[type="checkbox"] {
  width: auto;
  margin: 0;
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