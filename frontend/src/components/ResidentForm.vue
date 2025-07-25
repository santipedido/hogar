<template>
  <form class="card form" @submit.prevent="handleSubmit">
    <h2>{{ isEdit ? 'Editar residente' : 'Agregar residente' }}</h2>
    <label>Nombre
      <input v-model="form.name" required />
    </label>
    <label>Estado
      <select v-model="form.status" required>
        <option value="independent">Independiente</option>
        <option value="semidependent">Semidependiente</option>
      </select>
    </label>
    <label>Foto (URL)
      <input v-model="form.photo_url" type="url" placeholder="https://..." />
    </label>
    <label>Contacto de emergencia
      <input v-model="form.emergency_contact_name" />
    </label>
    <label>Teléfono de emergencia
      <input v-model="form.emergency_contact_phone" />
    </label>
    <label>Fecha de ingreso
      <input v-model="form.admission_date" type="date" required />
    </label>
    <label>Fecha de egreso
      <input v-model="form.discharge_date" type="date" />
    </label>
    <div class="actions">
      <button type="submit">{{ isEdit ? 'Guardar cambios' : 'Agregar' }}</button>
      <button type="button" @click="$emit('cancel')" class="secondary">Cancelar</button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </form>
</template>

<script setup>
import { reactive, toRefs, watch, ref } from 'vue'

const props = defineProps({
  modelValue: Object,
  isEdit: Boolean
})
const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  name: '',
  status: 'independent',
  photo_url: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  admission_date: '',
  discharge_date: ''
})
const error = ref('')

watch(() => props.modelValue, (val) => {
  if (val) Object.assign(form, val)
}, { immediate: true })

function handleSubmit() {
  error.value = ''
  if (!form.name || !form.status || !form.admission_date) {
    error.value = 'Completa los campos obligatorios.'
    return
  }
  emit('submit', { ...form })
}
</script>

<style scoped>
.form {
  max-width: 400px;
  margin: 2rem auto;
}
.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}
button.secondary {
  background: #eee;
  color: #333;
}
.error {
  color: #c00;
  margin-top: 1rem;
  text-align: center;
}
</style> 