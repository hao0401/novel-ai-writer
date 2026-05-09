<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">AI IDEATION</div>
        <h1>AI 创意中心</h1>
        <p>
          把题材、读者、基调和关键词转成可落库的网文项目包装：书名、简介、标签、卖点、开篇钩子和核心冲突。
        </p>
        <p class="next-hint">
          如果已经建好项目，这里通常是第二步。生成结果后可以直接写回小说项目。
        </p>
      </div>
      <span class="pill">结构化输出 · 可一键写入项目</span>
    </div>

    <div class="idea-shell">
      <section class="prompt-panel paper-card">
        <div class="panel-title">
          <strong>创意简报</strong>
          <span class="muted">Brief</span>
        </div>
        <el-form :model="form" label-position="top">
          <el-form-item label="关联小说"
            ><NovelSelect v-model="form.novel_id" :novels="novels"
          /></el-form-item>
          <el-form-item label="题材方向"
            ><el-input
              v-model="form.topic"
              size="large"
              placeholder="如：都市悬疑 / 玄幻升级 / 古言权谋"
          /></el-form-item>
          <el-form-item label="核心关键词"
            ><el-input
              v-model="form.keywords"
              placeholder="如：旧稿、投稿、反转、身份秘密"
          /></el-form-item>
          <el-form-item label="目标读者"
            ><el-input
              v-model="form.target_readers"
              placeholder="如：喜欢强钩子和快节奏反转的年轻读者"
          /></el-form-item>
          <el-form-item label="故事基调"
            ><el-input
              v-model="form.tone"
              placeholder="如：紧张、爽感、克制、悬疑"
          /></el-form-item>
          <div class="toolbar">
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="generate"
              >生成创意方案</el-button
            >
            <el-button
              size="large"
              @click="saveToNovel"
              :disabled="!result.titles"
              >写入小说项目</el-button
            >
          </div>
        </el-form>
      </section>

      <section class="result-area">
        <div v-if="!result.titles" class="empty-panel">
          <div>
            <strong>等待生成创意方案</strong>
            <p>
              建议输入明确的目标读者和故事基调，AI
              会更容易生成可投稿平台使用的包装信息。
            </p>
          </div>
        </div>

        <template v-else>
          <div class="hero-result paper-card">
            <div class="eyebrow">TITLE OPTIONS</div>
            <h2>{{ result.titles?.[0] }}</h2>
            <p>{{ result.one_sentence_pitch }}</p>
            <div class="tag-row">
              <span v-for="item in result.tags" :key="item">{{ item }}</span>
            </div>
          </div>

          <div class="bento-grid">
            <div class="bento span-7">
              <div class="panel-title">
                <strong>小说简介</strong
                ><span class="pill">{{ result.category }}</span>
              </div>
              <div class="long-copy">{{ result.synopsis }}</div>
            </div>
            <div class="bento span-5">
              <div class="panel-title">
                <strong>开篇钩子</strong><span class="muted">Hook</span>
              </div>
              <div class="quote">{{ result.opening_hook }}</div>
            </div>
            <div class="bento span-12">
              <div class="panel-title">
                <strong>主要爽点 / 冲突点</strong
                ><span class="muted">Conflict Engine</span>
              </div>
              <div class="conflict-grid">
                <div v-for="item in result.conflicts" :key="item">
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import NovelSelect from "../components/NovelSelect.vue";
import { aiApi, novelApi } from "../api";

const novels = ref([]);
const result = ref({});
const loading = ref(false);
const form = reactive({
  novel_id: null,
  topic: "",
  keywords: "",
  target_readers: "",
  tone: "",
});

async function load() {
  novels.value = await novelApi.list();
  if (novels.value[0]) form.novel_id = novels.value[0].id;
}
async function generate() {
  loading.value = true;
  try {
    result.value = await aiApi.idea(form);
  } finally {
    loading.value = false;
  }
}
async function saveToNovel() {
  const target = novels.value.find((item) => item.id === form.novel_id);
  if (!target) return;
  await novelApi.update(target.id, {
    ...target,
    title: result.value.titles?.[0] || target.title,
    synopsis: result.value.synopsis,
    genre: result.value.category || target.genre,
    tags: (result.value.tags || []).join(","),
    selling_points: result.value.one_sentence_pitch,
  });
  ElMessage.success("已写入小说项目");
}
onMounted(load);
</script>

<style scoped>
.idea-shell {
  display: grid;
  grid-template-columns: 390px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
.prompt-panel {
  padding: 20px;
  position: sticky;
  top: 96px;
}
.result-area {
  min-width: 0;
}
.hero-result {
  padding: 28px;
  margin-bottom: 16px;
  background: linear-gradient(
    135deg,
    rgba(255, 253, 247, 0.98),
    rgba(230, 240, 236, 0.92)
  );
}
.hero-result h2 {
  margin: 10px 0;
  font-size: 34px;
}
.hero-result p {
  max-width: 780px;
  color: var(--ink-soft);
  line-height: 1.8;
}
.tag-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 18px;
}
.tag-row span {
  padding: 7px 10px;
  border-radius: 999px;
  background: var(--teal-soft);
  color: var(--teal);
  border: 1px solid #c7ddd7;
}
.long-copy {
  color: var(--ink-soft);
  line-height: 1.9;
  font-size: 15px;
}
.quote {
  padding-left: 14px;
  border-left: 3px solid var(--teal);
  color: var(--ink-soft);
  line-height: 1.9;
}
.conflict-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.conflict-grid div {
  min-height: 72px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbf8f1;
  color: var(--ink-soft);
}
@media (max-width: 1100px) {
  .idea-shell {
    grid-template-columns: 1fr;
  }
  .prompt-panel {
    position: static;
  }
  .conflict-grid {
    grid-template-columns: 1fr;
  }
}
</style>
