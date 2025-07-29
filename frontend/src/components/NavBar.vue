<template>
  <nav class="navbar">
    <div class="nav-brand">
      <h1>🏥 Hogar Geriátrico</h1>
    </div>
    
    <div class="nav-menu">
      <router-link 
        to="/" 
        class="nav-link"
        :class="{ active: $route.path === '/' }"
      >
        <span class="nav-icon">🏠</span>
        Inicio
      </router-link>
      
      <router-link 
        to="/residents" 
        class="nav-link"
        :class="{ active: $route.path === '/residents' }"
      >
        <span class="nav-icon">👥</span>
        Residentes
      </router-link>
      
      <router-link 
        to="/vital-signs" 
        class="nav-link"
        :class="{ active: $route.path === '/vital-signs' }"
      >
        <span class="nav-icon">❤️</span>
        Signos Vitales
      </router-link>
      
      <router-link 
        to="/medications" 
        class="nav-link"
        :class="{ active: $route.path === '/medications' }"
      >
        <span class="nav-icon">💊</span>
        Medicamentos
      </router-link>
      
      <router-link 
        to="/family-contacts" 
        class="nav-link"
        :class="{ active: $route.path === '/family-contacts' }"
      >
        <span class="nav-icon">👨‍👩‍👧‍👦</span>
        Contactos Familiares
      </router-link>
    </div>
  </nav>
</template>

<script setup>
// No necesitamos lógica adicional por ahora
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.nav-menu {
  display: flex;
  gap: 10px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  text-decoration: none;
  color: #666;
  border-radius: 6px;
  transition: all 0.3s;
  font-weight: 500;
}

.nav-link:hover {
  background: #f8f9fa;
  color: #333;
}

.nav-link.active {
  background: #007bff;
  color: white;
}

.nav-icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    padding: 10px 20px;
    gap: 15px;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-link {
    padding: 8px 12px;
    font-size: 14px;
  }
}
</style> 