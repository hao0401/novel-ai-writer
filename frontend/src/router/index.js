import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "../layouts/MainLayout.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Dashboard from "../views/Dashboard.vue";
import Novels from "../views/Novels.vue";
import Idea from "../views/Idea.vue";
import Characters from "../views/Characters.vue";
import World from "../views/World.vue";
import Outlines from "../views/Outlines.vue";
import ChapterEditor from "../views/ChapterEditor.vue";
import Chapters from "../views/Chapters.vue";
import Submission from "../views/Submission.vue";
import History from "../views/History.vue";
import Stats from "../views/Stats.vue";
import Knowledge from "../views/Knowledge.vue";
import Prompts from "../views/Prompts.vue";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "dashboard", component: Dashboard },
      { path: "novels", component: Novels },
      { path: "idea", component: Idea },
      { path: "characters", component: Characters },
      { path: "world", component: World },
      { path: "outlines", component: Outlines },
      { path: "chapter-editor", component: ChapterEditor },
      { path: "chapters", component: Chapters },
      { path: "knowledge", component: Knowledge },
      { path: "prompts", component: Prompts },
      { path: "submission", component: Submission },
      { path: "history", component: History },
      { path: "stats", component: Stats },
    ],
  },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem("token")) return "/login";
  if (
    (to.path === "/login" || to.path === "/register") &&
    localStorage.getItem("token")
  )
    return "/dashboard";
});

export default router;
