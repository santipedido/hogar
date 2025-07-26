<template>
  <div class="contact-list">
    <div class="header">
      <h3>Contactos Familiares</h3>
      <button @click="openAdd" class="add-btn">Agregar contacto</button>
    </div>

    <FamilyContactForm
      v-if="showForm"
      :modelValue="selectedContact"
      :residentId="residentId"
      :isEdit="isEdit"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <div v-if="loading" class="loader">
      <IconSpinner :size="50" />
      <p>Cargando contactos...</p>
    </div>
    <div v-else-if="error" class="error">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <p>{{ error }}</p>
      <button @click="fetchContacts" class="retry-btn">Reintentar</button>
    </div>
    <div v-else>
      <div v-if="contacts.length === 0" class="empty">
        No hay contactos familiares registrados.
      </div>
      <div v-else class="contacts">
        <div v-for="contact in contacts" :key="contact.id" class="contact-card" :class="{ 'is-primary': contact.is_primary }">
          <div class="contact-info">
            <div class="name-badge">
              <h4>{{ contact.name }}</h4>
              <span v-if="contact.is_primary" class="primary-badge">Principal</span>
            </div>
            <p class="relationship">{{ contact.relationship }}</p>
            <p class="phone">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
              {{ contact.phone }}
            </p>
            <p v-if="contact.address" class="address">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              {{ contact.address }}
            </p>
            <p v-if="contact.notes" class="notes">{{ contact.notes }}</p>
          </div>
          <div class="actions">
            <button @click="openEdit(contact)" class="edit-btn">Editar</button>
            <button @click="removeContact(contact.id)" class="delete-btn">Eliminar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FamilyContactForm from './FamilyContactForm.vue'
import IconSpinner from './icons/IconSpinner.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const contacts = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedContact = ref(null)

async function fetchContacts() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/family-contacts/resident/${props.residentId}`)
    if (!res.ok) throw new Error('No se pudieron cargar los contactos')
    contacts.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchContacts)

function openAdd() {
  selectedContact.value = null
  isEdit.value = false
  showForm.value = true
}

function openEdit(contact) {
  selectedContact.value = { ...contact }
  isEdit.value = true
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  selectedContact.value = null
}

async function handleFormSubmit(data) {
  try {
    if (isEdit.value && selectedContact.value) {
      // Editar
      const res = await fetch(import.meta.env.VITE_API_URL + `/api/family-contacts/${selectedContact.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo editar el contacto')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/api/family-contacts/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo agregar el contacto')
    }
    await fetchContacts()
    closeForm()
  } catch (e) {
    alert(e.message)
  }
}

async function removeContact(id) {
  if (!confirm('¿Seguro que deseas eliminar este contacto?')) return
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/family-contacts/${id}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('No se pudo eliminar el contacto')
    await fetchContacts()
  } catch (e) {
    alert(e.message)
  }
}
</script>

<style scoped>
.contact-list {
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

.add-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: var(--color-danger, #dc3545);
  text-align: center;
  background: var(--color-background-soft);
  border-radius: 8px;
  margin: 1rem 0;
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

.empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-light);
  background: var(--color-background-soft);
  border-radius: 8px;
}

.contacts {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.contact-card {
  background: var(--color-background-soft);
  border-radius: 10px;
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.contact-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.contact-card.is-primary {
  border: 2px solid var(--color-primary);
}

.name-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.name-badge h4 {
  margin: 0;
  color: var(--color-heading);
}

.primary-badge {
  background: var(--color-primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
}

.relationship {
  color: var(--color-text-light);
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.phone, .address {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.5rem 0;
  font-size: 0.875rem;
}

.notes {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-style: italic;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.edit-btn, .delete-btn {
  flex: 1;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
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
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
}

.delete-btn:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

@media (max-width: 640px) {
  .contacts {
    grid-template-columns: 1fr;
  }
  
  .contact-card {
    width: 100%;
  }
}
</style> 