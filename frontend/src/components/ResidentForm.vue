<template>
  <div class="resident-form">
    <h3>{{ isEdit ? 'Editar' : 'Nuevo' }} Residente</h3>
    <form @submit.prevent="handleSubmit">
      <div class="photo-upload">
        <div class="preview-container">
          <img 
            v-if="photoPreview || formData.photo_url" 
            :src="photoPreview || formData.photo_url" 
            alt="Vista previa" 
            class="photo-preview"
          />
          <IconUserPlaceholder v-else class="photo-placeholder" />
        </div>
        <div class="upload-controls">
          <label class="upload-btn">
            <input 
              type="file" 
              accept="image/*"
              @change="handlePhotoChange" 
              class="hidden"
            >
            <span>{{ formData.photo_url ? 'Cambiar foto' : 'Subir foto' }}</span>
          </label>
          <button 
            v-if="photoPreview || formData.photo_url" 
            type="button" 
            class="remove-photo" 
            @click="removePhoto"
          >
            Eliminar foto
          </button>
        </div>
      </div>

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
        <label for="status">Estado *</label>
        <select 
          id="status" 
          v-model="formData.status" 
          required
        >
          <option value="independent">Independiente</option>
          <option value="semidependent">Semidependiente</option>
        </select>
      </div>

      <div class="form-group">
        <label for="emergencyContactName">Contacto de emergencia</label>
        <input 
          id="emergencyContactName" 
          v-model="formData.emergency_contact_name" 
          type="text"
          placeholder="Nombre del contacto"
        >
      </div>

      <div class="form-group">
        <label for="emergencyContactPhone">Teléfono de emergencia</label>
        <input 
          id="emergencyContactPhone" 
          v-model="formData.emergency_contact_phone" 
          type="tel"
          placeholder="Número de teléfono"
        >
      </div>

      <div class="form-group">
        <label for="admissionDate">Fecha de ingreso *</label>
        <input 
          id="admissionDate" 
          v-model="formData.admission_date" 
          type="date" 
          required
        >
      </div>

      <div class="form-group">
        <label for="dischargeDate">Fecha de egreso</label>
        <input 
          id="dischargeDate" 
          v-model="formData.discharge_date" 
          type="date"
        >
      </div>

      <div class="actions">
        <button type="submit">{{ isEdit ? 'Guardar cambios' : 'Agregar' }}</button>
        <button type="button" class="secondary" @click="closeForm">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import IconUserPlaceholder from './icons/IconUserPlaceholder.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const formData = ref({
  name: '',
  status: 'independent',
  photo_url: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  admission_date: '',
  discharge_date: '',
  ...props.modelValue
})

const photoPreview = ref(null)
const photoFile = ref(null)

async function handlePhotoChange(event) {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) { // 5MB limit
    alert('La imagen es demasiado grande. El tamaño máximo es 5MB.')
    event.target.value = ''
    return
  }

  photoFile.value = file
  photoPreview.value = URL.createObjectURL(file)
}

function removePhoto() {
  photoFile.value = null
  photoPreview.value = null
  formData.value.photo_url = ''
}

async function uploadPhoto() {
  if (!photoFile.value) return null

  const formData = new FormData()
  formData.append('file', photoFile.value)

  try {
    const response = await fetch(import.meta.env.VITE_API_URL + '/api/upload/', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) throw new Error('Error al subir la imagen')
    
    const data = await response.json()
    return data.url
  } catch (error) {
    console.error('Error uploading photo:', error)
    throw new Error('No se pudo subir la imagen')
  }
}

function cleanResidentData(data) {
  const cleaned = { ...data }
  
  // Convertir fechas a formato ISO string
  if (cleaned.admission_date) {
    cleaned.admission_date = new Date(cleaned.admission_date).toISOString().split('T')[0]
  }
  if (cleaned.discharge_date) {
    cleaned.discharge_date = new Date(cleaned.discharge_date).toISOString().split('T')[0]
  }

  // Limpiar campos vacíos
  Object.keys(cleaned).forEach(key => {
    if (cleaned[key] === '') cleaned[key] = null
  })

  return cleaned
}

async function handleSubmit() {
  try {
    // Primero subir la foto si hay una nueva
    if (photoFile.value) {
      const photoUrl = await uploadPhoto()
      formData.value.photo_url = photoUrl
    }

    // Limpiar y preparar los datos
    const cleanedData = cleanResidentData(formData.value)

    // Emitir los datos limpios
    emit('submit', cleanedData)
  } catch (e) {
    alert(e.message)
  }
}

function closeForm() {
  emit('cancel')
}
</script>

<style scoped>
.resident-form {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-background-soft);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
}

.resident-form h3 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-text-dark);
}

.photo-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.preview-container {
  width: 150px;
  height: 150px;
  border-radius: 75px;
  overflow: hidden;
  background: var(--color-background-mute);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--color-primary);
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  color: var(--color-text-light);
  opacity: 0.5;
  width: 80px;
  height: 80px;
}

.upload-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.upload-btn {
  background: var(--color-primary);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.upload-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
}

.remove-photo {
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.remove-photo:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

.hidden {
  display: none;
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

input, select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-text-dark);
  background-color: var(--color-background-soft);
  transition: border-color 0.2s;
}

input:focus, select:focus {
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