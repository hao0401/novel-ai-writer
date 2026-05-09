<template>
  <div class="auth-shell">
    <div class="auth-card paper-card">
      <div class="ink-note">创建作者账号</div>
      <h1>注册</h1>
      <p>系统默认只提供普通作者身份，注册后即可进入工作台。</p>
      <el-form :model="form" @submit.prevent="submit" label-position="top">
        <el-form-item label="用户名"
          ><el-input v-model="form.username"
        /></el-form-item>
        <el-form-item label="笔名"
          ><el-input v-model="form.pen_name"
        /></el-form-item>
        <el-form-item label="密码"
          ><el-input v-model="form.password" type="password" show-password
        /></el-form-item>
        <el-button type="primary" style="width: 100%" @click="submit"
          >注册并进入系统</el-button
        >
        <div class="jump">
          已有账号？<router-link to="/login">登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const form = reactive({ username: "", pen_name: "", password: "" });
async function submit() {
  await auth.register(form);
  router.push("/dashboard");
}
</script>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}
.auth-card {
  width: 430px;
  padding: 34px;
}
.ink-note {
  color: var(--teal);
  font-weight: 700;
  margin-bottom: 10px;
}
h1 {
  margin: 0;
  font-size: 32px;
}
p {
  color: var(--muted);
  line-height: 1.8;
  margin: 12px 0 24px;
}
.jump {
  text-align: center;
  margin-top: 18px;
  color: var(--muted);
}
</style>
