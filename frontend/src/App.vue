<template>
  <div id="app" class="app-shell">
    <header class="app-header">
      <div class="brand">Data Platform Console</div>
      <nav class="app-nav">
        <router-link to="/">Home</router-link>
        <router-link to="/upload">Upload</router-link>
        <router-link to="/files">Files</router-link>
        <router-link to="/metrics">Metrics</router-link>
        <router-link to="/reports">Reports</router-link>
        <span v-if="isAuthenticated" class="user-info">
          {{ currentUser ? currentUser.username : 'User' }}
          <el-button type="text" size="mini" @click="logout" style="color: #f56c6c">登出</el-button>
        </span>
        <router-link v-else to="/login">Login</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'App',
  computed: {
    ...mapGetters(['isAuthenticated', 'currentUser'])
  },
  methods: {
    logout() {
      this.$store.dispatch('logout');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: #e2e8f0;
  font-family: 'Space Grotesk', 'Inter', 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(6px);
}

.brand {
  font-weight: 700;
  letter-spacing: 0.5px;
}

.app-nav a {
  color: #e2e8f0;
  text-decoration: none;
  margin-left: 16px;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background 0.2s ease, color 0.2s ease;
}

.app-nav a.router-link-exact-active {
  background: rgba(255, 255, 255, 0.08);
  color: #38bdf8;
}

.user-info {
  color: #94a3b8;
  margin-left: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-main {
  flex: 1;
  padding: 24px;
}
</style>
