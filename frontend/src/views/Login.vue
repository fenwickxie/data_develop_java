<template>
  <div class="auth">
    <el-card class="card" shadow="hover">
      <h2>登录</h2>
      <el-form :model="form" @submit.native.prevent="submit" :disabled="loading">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="submit">登录</el-button>
        <div class="error" v-if="error">{{ error }}</div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  data() {
    return {
      form: { username: '', password: '' },
      loading: false,
      error: ''
    };
  },
  methods: {
    async submit() {
      this.loading = true;
      this.error = '';
      try {
        await this.$store.dispatch('login', this.form);
        this.$router.push('/');
      } catch (err) {
        this.error = err?.response?.status === 401 ? '用户名或密码错误' : (err?.message || '登录失败');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.auth {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
.card {
  width: 360px;
}
.error {
  color: #f56c6c;
  margin-top: 8px;
}
</style>
