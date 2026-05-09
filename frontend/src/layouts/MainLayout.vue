<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">墨</div>
        <div>
          <strong>墨境创作台</strong>
          <span>Novel AI Studio</span>
        </div>
      </div>

      <div class="nav-group-title">核心流程</div>
      <el-menu
        router
        :default-active="$route.path"
        background-color="transparent"
      >
        <el-menu-item index="/dashboard"
          ><el-icon><EditPen /></el-icon>写作台</el-menu-item
        >
        <el-menu-item index="/novels"
          ><el-icon><Collection /></el-icon>作品</el-menu-item
        >
        <el-menu-item index="/submission"
          ><el-icon><Upload /></el-icon>投稿</el-menu-item
        >
      </el-menu>

      <el-collapse class="advanced-nav">
        <el-collapse-item title="扩展工具" name="advanced">
          <el-menu
            router
            :default-active="$route.path"
            background-color="transparent"
          >
            <el-menu-item index="/idea"
              ><el-icon><MagicStick /></el-icon>AI 创意</el-menu-item
            >
            <el-menu-item index="/characters"
              ><el-icon><UserFilled /></el-icon>人物设定</el-menu-item
            >
            <el-menu-item index="/world"
              ><el-icon><Guide /></el-icon>世界观设定</el-menu-item
            >
            <el-menu-item index="/outlines"
              ><el-icon><Tickets /></el-icon>大纲</el-menu-item
            >
            <el-menu-item index="/chapter-editor"
              ><el-icon><Document /></el-icon>章节编辑器</el-menu-item
            >
            <el-menu-item index="/chapters"
              ><el-icon><Document /></el-icon>章节管理</el-menu-item
            >
            <el-menu-item index="/knowledge"
              ><el-icon><Collection /></el-icon>素材库</el-menu-item
            >
            <el-menu-item index="/prompts"
              ><el-icon><Tickets /></el-icon>Prompt 模板</el-menu-item
            >
            <el-menu-item index="/history"
              ><el-icon><Clock /></el-icon>AI 历史</el-menu-item
            >
            <el-menu-item index="/stats"
              ><el-icon><TrendCharts /></el-icon>统计</el-menu-item
            >
          </el-menu>
        </el-collapse-item>
      </el-collapse>

      <div class="sidebar-note">
        <div class="eyebrow">工作流</div>
        <p>
          先建立作品，再生成章节，最后整理投稿内容。扩展工具用于补充设定和统计。
        </p>
      </div>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <strong>基于大模型的网络小说创作与投稿辅助系统</strong>
          <span>创意生成 · 设定管理 · 章节写作 · 投稿整理</span>
        </div>
        <div class="userbox">
          <span class="status-dot"></span>
          <span>{{ auth.user?.pen_name || auth.user?.username }}</span>
          <el-button text @click="logout">退出</el-button>
        </div>
      </header>
      <section class="content">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
function logout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 264px;
  padding: 18px 10px;
  background: rgba(251, 248, 241, 0.86);
  border-right: 1px solid var(--line);
  position: sticky;
  top: 0;
  height: 100vh;
  backdrop-filter: blur(14px);
}
.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px 14px 18px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--line);
}
.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: #fffdf7;
  background: linear-gradient(145deg, var(--teal), #143d39);
  box-shadow: 0 12px 28px rgba(29, 93, 88, 0.22);
  font-weight: 800;
}
.brand strong {
  display: block;
  font-size: 16px;
}
.brand span,
.topbar span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  margin-top: 4px;
}
.nav-group-title {
  margin: 16px 16px 6px;
  color: var(--faint);
  font-size: 12px;
}
.sidebar-note {
  margin: 18px 10px 0;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: rgba(255, 253, 247, 0.68);
}
.sidebar-note p {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.7;
}
.advanced-nav {
  margin: 14px 8px 0;
  --el-collapse-header-bg-color: transparent;
  --el-collapse-content-bg-color: transparent;
  --el-collapse-border-color: transparent;
}
.advanced-nav :deep(.el-collapse-item__header) {
  height: 34px;
  padding: 0 8px;
  color: var(--faint);
  font-size: 12px;
}
.advanced-nav :deep(.el-collapse-item__content) {
  padding-bottom: 0;
}
.workspace {
  flex: 1;
  min-width: 0;
}
.topbar {
  height: 74px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  border-bottom: 1px solid var(--line);
  background: rgba(255, 253, 247, 0.72);
  backdrop-filter: blur(14px);
  position: sticky;
  top: 0;
  z-index: 5;
}
.topbar strong {
  font-size: 16px;
}
.userbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 10px;
  color: var(--ink);
  background: rgba(255, 253, 247, 0.76);
  border: 1px solid var(--line);
  border-radius: 999px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2f9b68;
  box-shadow: 0 0 0 4px rgba(47, 155, 104, 0.12);
}
.content {
  padding: 28px 30px 36px;
}
</style>
