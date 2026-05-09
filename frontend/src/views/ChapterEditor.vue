<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">WRITING DESK</div>
        <h1>写章节</h1>
        <p>
          最简单的用法：选小说项目，点“生成正文”，满意后点“保存草稿”。右侧按钮可用于续写、润色和改写。
        </p>
        <p class="next-hint">没有大纲也可以写；有大纲时，生成效果会更稳定。</p>
      </div>
      <span class="pill"
        >{{ editor.word_count || 0 }} 字 · {{ editor.status || "草稿" }}</span
      >
    </div>
    <div class="editor-layout">
      <div class="left-col paper-card">
        <div class="panel-head">
          <strong>章节目录</strong>
          <NovelSelect v-model="novelId" :novels="novels" />
        </div>
        <div class="chapter-list">
          <button
            v-for="item in chapters"
            :key="item.id"
            :class="{ active: item.id === activeId }"
            @click="selectChapter(item)"
          >
            <span>{{ item.chapter_number }}</span>
            <strong>{{ item.title }}</strong>
            <em>{{ item.word_count }} 字 · {{ item.status }}</em>
          </button>
          <div v-if="!chapters.length" class="mini-empty">
            暂无章节，先从中间区域生成正文。
          </div>
        </div>
      </div>
      <div class="center-col paper-card">
        <div class="writing-toolbar">
          <el-select
            v-model="genForm.outline_id"
            placeholder="可选：章节大纲"
            clearable
            style="width: 220px"
          >
            <el-option
              v-for="item in outlines"
              :key="item.id"
              :label="item.chapter_title"
              :value="item.id"
            />
          </el-select>
          <el-select v-model="genForm.writing_style" style="width: 160px">
            <el-option
              v-for="item in styles"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
          <el-select v-model="genForm.word_count" style="width: 120px">
            <el-option :value="1000" label="1000字" />
            <el-option :value="2000" label="2000字" />
            <el-option :value="3000" label="3000字" />
          </el-select>
          <el-button
            type="primary"
            :loading="generating"
            @click="generateChapter"
            >生成正文</el-button
          >
          <el-button @click="saveChapter">保存草稿</el-button>
          <el-button @click="$router.push('/chapters')"
            >下一步：管理章节</el-button
          >
        </div>
        <div class="paper-editor">
          <el-input
            v-model="editor.title"
            class="title-input"
            placeholder="章节标题"
          />
          <el-input
            v-model="editor.content"
            type="textarea"
            class="editor-textarea"
          />
        </div>
      </div>
      <div class="right-col">
        <div class="paper-card assistant-card">
          <div class="panel-title">
            <strong>AI 助手</strong>
            <span class="pill">上下文写作</span>
          </div>
          <div class="action-grid">
            <el-button @click="revise('续写')">续写</el-button>
            <el-button @click="revise('润色')">润色</el-button>
            <el-button @click="revise('改写')">改写</el-button>
          </div>
          <el-input
            v-model="instruction"
            type="textarea"
            :rows="4"
            placeholder="可输入：增强冲突、优化对白、压缩冗余描写等"
          />
          <div v-if="compare.after" class="result-panel compare-panel">
            修改说明：{{ compare.summary }}

            一致性检查：{{ compare.consistency_check }}
          </div>
        </div>
        <div class="paper-card reference-card">
          <div class="panel-title">
            <strong>设定参考</strong><span class="muted">Context</span>
          </div>
          <div class="muted" style="margin: 12px 0 6px">人物</div>
          <div
            v-for="item in characters"
            :key="item.id"
            style="padding: 8px 0; border-bottom: 1px solid var(--line)"
          >
            <strong>{{ item.name }}</strong>
            <div class="muted">{{ item.identity }}</div>
          </div>
          <div class="muted" style="margin: 12px 0 6px">世界观</div>
          <div class="result-panel" style="font-size: 13px">
            {{ worlds[0]?.world_background || "暂无世界观设定" }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import NovelSelect from "../components/NovelSelect.vue";
import {
  aiApi,
  chapterApi,
  characterApi,
  novelApi,
  outlineApi,
  worldApi,
} from "../api";

const novels = ref([]);
const novelId = ref(null);
const chapters = ref([]);
const outlines = ref([]);
const characters = ref([]);
const worlds = ref([]);
const activeId = ref(null);
const generating = ref(false);
const styles = [
  "都市爽文",
  "玄幻升级流",
  "言情甜宠",
  "悬疑推理",
  "热血战斗",
  "轻松幽默",
  "现实细腻",
];
const genForm = reactive({
  novel_id: null,
  outline_id: null,
  word_count: 2000,
  writing_style: "都市爽文",
});
const editor = reactive({
  id: null,
  title: "",
  content: "",
  highlights: "",
  foreshadowing: "",
  chapter_number: 1,
  status: "草稿",
  uploaded_platform: "",
  outline_id: null,
});
const instruction = ref("");
const compare = ref({});

async function loadNovels() {
  novels.value = await novelApi.list();
  if (novels.value[0]) {
    novelId.value = novels.value[0].id;
    genForm.novel_id = novels.value[0].id;
  }
}
async function loadAll() {
  if (!novelId.value) return;
  [chapters.value, outlines.value, characters.value, worlds.value] =
    await Promise.all([
      chapterApi.list(novelId.value),
      outlineApi.list(novelId.value),
      characterApi.list(novelId.value),
      worldApi.list(novelId.value),
    ]);
}
function selectChapter(row) {
  activeId.value = row.id;
  Object.assign(editor, row);
  genForm.outline_id = row.outline_id;
}
async function generateChapter() {
  generating.value = true;
  try {
    const res = await aiApi.chapter(genForm);
    editor.title = res.chapter_title;
    editor.content = res.content;
    editor.highlights = res.highlights;
    editor.foreshadowing = res.foreshadowing;
    editor.outline_id = genForm.outline_id;
    editor.chapter_number =
      outlines.value.find((item) => item.id === genForm.outline_id)
        ?.chapter_number || chapters.value.length + 1;
  } finally {
    generating.value = false;
  }
}
async function saveChapter() {
  const payload = {
    ...editor,
    outline_id: editor.outline_id,
    title: editor.title,
    content: editor.content,
    highlights: editor.highlights,
    foreshadowing: editor.foreshadowing,
    chapter_number: editor.chapter_number,
    status: editor.status,
    uploaded_platform: editor.uploaded_platform,
  };
  if (editor.id) await chapterApi.update(editor.id, payload);
  else {
    const created = await chapterApi.create(novelId.value, payload);
    editor.id = created.id;
  }
  ElMessage.success("章节已保存");
  loadAll();
}
async function revise(mode) {
  if (!editor.id) {
    ElMessage.warning("请先保存章节");
    return;
  }
  compare.value = await aiApi.revise(editor.id, mode, {
    instruction: instruction.value,
  });
  editor.content = compare.value.after;
}
watch(novelId, async (val) => {
  genForm.novel_id = val;
  await loadAll();
});
onMounted(loadNovels);
</script>

<style scoped>
.editor-layout {
  display: grid;
  grid-template-columns: 260px 1fr 340px;
  gap: 16px;
  min-height: calc(100vh - 170px);
}
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
.left-col {
  overflow: auto;
}
.center-col {
  overflow: hidden;
}
.right-col {
  display: flex;
  flex-direction: column;
}
.panel-head {
  display: grid;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--line);
}
.chapter-list {
  padding: 10px;
}
.chapter-list button {
  width: 100%;
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 10px;
  padding: 12px;
  margin-bottom: 8px;
  text-align: left;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
}
.chapter-list button:hover,
.chapter-list button.active {
  background: var(--teal-soft);
  border-color: #c7ddd7;
}
.chapter-list span {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: var(--teal);
  background: #fffdf7;
  border: 1px solid var(--line);
}
.chapter-list strong {
  display: block;
  color: var(--ink);
  font-size: 13px;
}
.chapter-list em {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 12px;
  font-style: normal;
}
.mini-empty {
  padding: 18px;
  color: var(--muted);
  text-align: center;
}
.writing-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
  background: rgba(250, 246, 237, 0.68);
}
.paper-editor {
  padding: 18px;
}
.title-input {
  margin-bottom: 14px;
}
.title-input :deep(.el-input__wrapper) {
  min-height: 52px;
  font-size: 22px;
  font-weight: 700;
}
.assistant-card,
.reference-card {
  padding: 16px;
  margin-bottom: 16px;
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}
.action-grid .el-button {
  margin-left: 0;
}
.compare-panel {
  margin-top: 12px;
  font-size: 13px;
}
@media (max-width: 1280px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }
}
</style>
