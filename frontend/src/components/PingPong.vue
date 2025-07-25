<template>
  <div>
    <button @click="pingBackend">Ping</button>
    <p v-if="response">Respuesta: {{ response }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const response = ref('')

async function pingBackend() {
  try {
    const res = await fetch('http://localhost:8000/ping')
    const data = await res.json()
    response.value = data.message
  } catch (e) {
    response.value = 'Error de conexión'
  }
}
</script> 