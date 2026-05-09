<template>
  <div>
    <section class="quick-hero paper-card">
      <div>
        <div class="eyebrow">QUICK WRITE</div>
        <h1>直接写，不用先研究系统</h1>
        <p>
          这个页面覆盖最常用流程：选择小说 → 生成一章 → 修改保存 →
          导出投稿。人物、大纲、世界观以后需要时再补。
        </p>
      </div>
      <div class="hero-metrics">
        <div v-for="item in metrics" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </section>

    <section class="quick-workbench">
      <aside class="paper-card setup-panel">
        <div class="panel-title">
          <strong>1. 选择作品</strong>
          <el-button link @click="showQuickNovel = true">新建</el-button>
        </div>
        <NovelSelect v-if="novels.length" v-model="novelId" :novels="novels" />
        <div v-else class="empty-inline">
          还没有作品，先输入一个书名即可开始。
          <el-button type="primary" link @click="showQuickNovel = true"
            >马上创建</el-button
          >
        </div>
        <div class="helper-text">
          不用填完所有设定。先有一个作品名，就可以生成章节。
        </div>

        <div class="panel-title mt">
          <strong>2. 生成设置</strong>
          <span class="muted">可不填复杂设定</span>
        </div>
        <el-form label-position="top">
          <el-form-item label="章节标题">
            <el-input v-model="draft.title" placeholder="不填则由 AI 生成" />
          </el-form-item>
          <el-form-item label="写作风格">
            <el-select v-model="form.writing_style" style="width: 100%">
              <el-option
                v-for="item in styles"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="生成字数">
            <el-select v-model="form.word_count" style="width: 100%">
              <el-option :value="1000" label="1000 字" />
              <el-option :value="2000" label="2000 字" />
              <el-option :value="3000" label="3000 字" />
            </el-select>
          </el-form-item>
          <el-form-item label="补充要求">
            <el-input
              v-model="form.instruction"
              type="textarea"
              :rows="4"
              placeholder="例如：开头更抓人、冲突更强、对白更多"
            />
          </el-form-item>
        </el-form>

        <div class="action-stack">
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            @click="generate"
            >生成这一章</el-button
          >
          <el-button
            size="large"
            :disabled="!draft.content"
            @click="saveDraft"
            >{{ savedChapterId ? "更新草稿" : "保存为草稿" }}</el-button
          >
        </div>
      </aside>

      <main class="paper-card writing-panel">
        <div class="panel-title">
          <strong>3. 修改正文</strong>
          <span class="pill"
            >{{ savedChapterId ? "已保存" : "未保存" }} ·
            {{ wordCount }} 字</span
          >
        </div>
        <el-input
          v-model="draft.title"
          class="chapter-title"
          placeholder="章节标题"
        />
        <el-input
          v-model="draft.content"
          type="textarea"
          class="quick-editor"
          placeholder="生成后的章节正文会出现在这里，也可以直接手写。"
        />
        <div class="writer-actions">
          <el-button :disabled="!savedChapterId" @click="revise('续写')"
            >续写</el-button
          >
          <el-button :disabled="!savedChapterId" @click="revise('润色')"
            >润色</el-button
          >
          <el-button :disabled="!savedChapterId" @click="revise('改写')"
            >改写</el-button
          >
          <el-button
            type="primary"
            :disabled="!novelId"
            @click="download('docx')"
            >导出 DOCX</el-button
          >
          <el-button :disabled="!novelId" @click="download('txt')"
            >导出 TXT</el-button
          >
        </div>
      </main>
    </section>

    <section class="paper-card bottom-note">
      <strong>觉得生成效果不稳定？</strong>
      <span
        >再去补「人物设定」「世界观」「大纲」，AI
        会有更多上下文。只是想快速演示或写一章，停留在本页就够了。</span
      >
    </section>

    <el-dialog v-model="showQuickNovel" width="520px" title="快速创建作品">
      <el-form label-position="top">
        <el-form-item label="小说名称">
          <el-input v-model="quickNovel.title" placeholder="例如：深青档案" />
        </el-form-item>
        <el-form-item label="一句话简介">
          <el-input
            v-model="quickNovel.synopsis"
            type="textarea"
            :rows="3"
            placeholder="可以先简单写，后面再完善"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showQuickNovel = false">取消</el-button>
        <el-button type="primary" @click="createQuickNovel"
          >创建并开始写</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import NovelSelect from "../components/NovelSelect.vue";
import { aiApi, chapterApi, dashboardApi, novelApi } from "../api";

const novels = ref([]);
const novelId = ref(null);
const chapters = ref([]);
const dashboard = ref({ overview: {} });
const generating = ref(false);
const savedChapterId = ref(null);
const showQuickNovel = ref(false);
const styles = [
  "都市爽文",
  "玄幻升级流",
  "言情甜宠",
  "悬疑推理",
  "热血战斗",
  "轻松幽默",
  "现实细腻",
];
const form = reactive({
  word_count: 2000,
  writing_style: "都市爽文",
  instruction: "",
});
const draft = reactive({
  title: "",
  content: "",
  highlights: "",
  foreshadowing: "",
});
const quickNovel = reactive({ title: "", synopsis: "" });

const metrics = computed(() => [
  { label: "小说", value: dashboard.value.overview?.novel_count || 0 },
  { label: "章节", value: dashboard.value.overview?.chapter_count || 0 },
  {
    label: "待上传",
    value: dashboard.value.overview?.pending_upload_count || 0,
  },
]);
const wordCount = computed(
  () => (draft.content || "").replace(/\s/g, "").length,
);

async function load() {
  novels.value = await novelApi.list();
  dashboard.value = await dashboardApi.dashboard();
  if (!novelId.value && novels.value[0]) novelId.value = novels.value[0].id;
}
async function loadChapters() {
  if (!novelId.value) return;
  chapters.value = await chapterApi.list(novelId.value);
}
async function generate() {
  if (!novelId.value) {
    ElMessage.warning("请先选择或创建小说项目");
    return;
  }
  generating.value = true;
  try {
    const res = await aiApi.chapter({
      novel_id: novelId.value,
      word_count: form.word_count,
      writing_style: form.writing_style,
      instruction: form.instruction,
    });
    draft.title = draft.title || res.chapter_title;
    draft.content = res.content;
    draft.highlights = res.highlights;
    draft.foreshadowing = res.foreshadowing;
    savedChapterId.value = null;
  } finally {
    generating.value = false;
  }
}
async function saveDraft() {
  if (!novelId.value || !draft.content) return;
  const isUpdate = Boolean(savedChapterId.value);
  const payload = {
    outline_id: null,
    chapter_number: chapters.value.length + 1,
    title: draft.title || `第${chapters.value.length + 1}章 未命名章节`,
    content: draft.content,
    highlights: draft.highlights,
    foreshadowing: draft.foreshadowing,
    status: "草稿",
    uploaded_platform: "",
  };
  if (savedChapterId.value) {
    await chapterApi.update(savedChapterId.value, payload);
  } else {
    const created = await chapterApi.create(novelId.value, payload);
    savedChapterId.value = created.id;
  }
  await loadChapters();
  dashboard.value = await dashboardApi.dashboard();
  ElMessage.success(isUpdate ? "草稿已更新" : "已保存为章节草稿");
}
async function revise(mode) {
  if (!savedChapterId.value) return;
  const res = await aiApi.revise(savedChapterId.value, mode, {
    instruction: form.instruction,
  });
  draft.content = res.after;
  ElMessage.success(`${mode}完成`);
}
async function download(type) {
  const token = localStorage.getItem("token");
  const response = await axios.get(`/api/exports/${novelId.value}/${type}`, {
    responseType: "blob",
    headers: { Authorization: `Bearer ${token}` },
  });
  const blob = new Blob([response.data]);
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.download = type === "txt" ? "投稿稿件.txt" : "投稿稿件.docx";
  link.click();
  URL.revokeObjectURL(url);
}
async function createQuickNovel() {
  if (!quickNovel.title.trim()) {
    ElMessage.warning("请先填写小说名称");
    return;
  }
  const created = await novelApi.create({
    title: quickNovel.title.trim(),
    genre: "都市",
    style: "",
    target_platform: "",
    synopsis: quickNovel.synopsis,
    tags: "",
    selling_points: "",
    status: "创作中",
  });
  showQuickNovel.value = false;
  quickNovel.title = "";
  quickNovel.synopsis = "";
  await load();
  novelId.value = created.id;
  ElMessage.success("作品已创建，可以开始写章节");
}

watch(novelId, loadChapters);
onMounted(load);
</script>

<style scoped>
.quick-hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  padding: 30px;
  margin-bottom: 16px;
}
.quick-hero h1 {
  margin: 8px 0;
  font-size: 34px;
}
.quick-hero p {
  max-width: 760px;
  margin: 0;
  color: var(--muted);
  line-height: 1.75;
}
.hero-metrics {
  display: flex;
  gap: 10px;
}
.hero-metrics div {
  min-width: 88px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #fbf8f1;
}
.hero-metrics span {
  display: block;
  color: var(--muted);
  font-size: 12px;
}
.hero-metrics strong {
  display: block;
  margin-top: 6px;
  color: var(--teal);
  font-size: 24px;
}
.quick-workbench {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  gap: 16px;
}
.setup-panel,
.writing-panel {
  padding: 18px;
}
.helper-text {
  margin-top: 10px;
  color: var(--muted);
  line-height: 1.65;
  font-size: 13px;
}
.empty-inline {
  padding: 14px;
  color: var(--muted);
  border: 1px dashed var(--line-strong);
  border-radius: 10px;
  background: #fbf8f1;
  line-height: 1.7;
}
.mt {
  margin-top: 22px;
}
.action-stack {
  display: grid;
  gap: 10px;
}
.chapter-title {
  margin-bottom: 12px;
}
.chapter-title :deep(.el-input__wrapper) {
  min-height: 48px;
  font-size: 20px;
  font-weight: 700;
}
.quick-editor :deep(textarea) {
  min-height: 540px;
  padding: 28px 34px;
  line-height: 2;
  font-size: 16px;
  font-family: "Source Han Serif SC", "Songti SC", SimSun, serif;
  background: #fffef8;
}
.writer-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
  margin-top: 12px;
}
.bottom-note {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 16px;
  padding: 16px 18px;
  color: var(--muted);
}
.bottom-note strong {
  color: var(--ink);
}
@media (max-width: 1100px) {
  .quick-hero,
  .bottom-note {
    flex-direction: column;
    align-items: flex-start;
  }
  .quick-workbench {
    grid-template-columns: 1fr;
  }
}
</style>
