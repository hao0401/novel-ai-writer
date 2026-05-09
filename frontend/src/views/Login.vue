<template>
  <div class="auth-shell">
    <section class="auth-copy">
      <div class="eyebrow">AI NOVEL STUDIO</div>
      <h1>把灵感、设定、正文和投稿整理放进同一个写作工作台。</h1>
      <p>
        面向网文作者的沉浸式创作工具：从创意钩子到章节正文，从世界观约束到平台投稿记录，保持同一套创作上下文。
      </p>
      <div class="feature-row">
        <span>创意策划</span>
        <span>章节生成</span>
        <span>投稿导出</span>
      </div>
    </section>
    <section class="auth-card paper-card">
      <div class="panel-title">
        <div>
          <div class="eyebrow">WELCOME BACK</div>
          <h2>登录创作工作台</h2>
        </div>
        <span class="pill">DeepSeek 接入</span>
      </div>
      <el-form :model="form" @submit.prevent="submit" label-position="top">
        <el-form-item label="用户名"
          ><el-input v-model="form.username" size="large"
        /></el-form-item>
        <el-form-item label="密码"
          ><el-input
            v-model="form.password"
            type="password"
            show-password
            size="large"
        /></el-form-item>
        <el-button
          type="primary"
          size="large"
          style="width: 100%"
          @click="submit"
          >进入工作台</el-button
        >
        <div class="jump">
          还没有账号？<router-link to="/register">注册作者账号</router-link>
        </div>
      </el-form>
    </section>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const form = reactive({ username: "demo", password: "123456" });
async function submit() {
  await auth.login(form);
  router.push("/dashboard");
}
</script>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) 430px;
  gap: 44px;
  align-items: center;
  max-width: 1180px;
  margin: 0 auto;
  padding: 42px;
}
.auth-copy h1 {
  max-width: 720px;
  margin: 14px 0;
  color: var(--ink);
  font-size: 48px;
  line-height: 1.16;
  letter-spacing: 0;
}
.auth-copy p {
  max-width: 620px;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.9;
}
.feature-row {
  display: flex;
  gap: 10px;
  margin-top: 26px;
}
.feature-row span {
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 253, 247, 0.62);
  color: var(--ink-soft);
}
.auth-card {
  padding: 30px;
}
h2 {
  margin: 6px 0 0;
  font-size: 24px;
}
.jump {
  text-align: center;
  margin-top: 18px;
  color: var(--muted);
}
@media (max-width: 900px) {
  .auth-shell {
    grid-template-columns: 1fr;
    padding: 24px;
  }
  .auth-copy h1 {
    font-size: 34px;
  }
}
</style>
