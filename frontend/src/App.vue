<script setup>
import { ref } from 'vue'
import ResidentList from './components/ResidentList.vue'
import ResidentProfile from './components/ResidentProfile.vue'

const selectedResidentId = ref(null)
const showProfile = ref(false)

function handleSelectResident(resident) {
  selectedResidentId.value = resident.id
  showProfile.value = true
}

function handleBackToList() {
  showProfile.value = false
  selectedResidentId.value = null
}
</script>

<template>
  <div class="app">
    <header>
      <h1>Hogar Geriátrico</h1>
      <nav v-if="showProfile">
        <button @click="handleBackToList" class="back-btn">
          ← Volver a la lista
        </button>
      </nav>
    </header>

    <main>
      <ResidentProfile 
        v-if="showProfile && selectedResidentId"
        :residentId="selectedResidentId"
        @edit="showProfile = false"
      />
      <ResidentList 
        v-else
        @select-resident="handleSelectResident"
      />
    </main>
  </div>
</template>

<style scoped>
.app {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-heading);
}

.back-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--color-background-mute);
}

main {
  min-height: calc(100vh - 150px);
}

@media (max-width: 768px) {
  .app {
    padding: 0.5rem;
  }

  header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    margin-bottom: 1rem;
  }
}
</style>
