<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">MANUSCRIPT PIPELINE</div>
        <h1>章节管理</h1>
        <p>
          用稿件流水线视角管理章节状态、字数和平台去向，让章节从草稿到投稿的推进过程可追踪、可批量操作。
        </p>
      </div>
      <div class="toolbar">
        <NovelSelect v-model="novelId" :novels="novels" />
        <el-button type="primary" @click="$router.push('/chapter-editor')"
          >前往写作台</el-button
        >
        <el-button @click="$router.push('/submission')"
          >下一步：投稿整理</el-button
        >
      </div>
    </div>

    <div class="bento-grid">
      <div class="bento span-3" v-for="item in pipelineStats" :key="item.label">
        <div class="muted">{{ item.label }}</div>
        <div class="metric">{{ item.value }}</div>
        <div class="metric-caption">{{ item.caption }}</div>
      </div>
    </div>

    <div class="pipeline-shell">
      <section
        class="stage-panel paper-card"
        v-for="status in statuses"
        :key="status"
      >
        <div class="panel-title">
          <strong>{{ status }}</strong>
          <span class="pill">{{ stageItems(status).length }} 章</span>
        </div>
        <div v-if="!stageItems(status).length" class="mini-empty">暂无章节</div>
        <div
          v-for="item in stageItems(status)"
          :key="item.id"
          class="chapter-tile"
        >
          <div>
            <h3>{{ item.chapter_number }}. {{ item.title }}</h3>
            <p>
              {{ item.word_count }} 字 ·
              {{ item.uploaded_platform || "未填写平台" }}
            </p>
          </div>
          <div class="tile-actions">
            <el-button link @click="openDialog(item)">编辑</el-button>
            <el-dropdown @command="(command) => copyStatus(item, command)">
              <el-button link>变更状态</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="s in statuses"
                    :key="s"
                    :command="s"
                    >{{ s }}</el-dropdown-item
                  >
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </section>
    </div>

    <div class="section-card">
      <div class="panel-title">
        <strong>章节总表</strong>
        <span class="muted">便于快速查找与批量巡检</span>
      </div>
      <el-table :data="list">
        <el-table-column prop="chapter_number" label="序号" width="80" />
        <el-table-column prop="title" label="章节标题" min-width="220" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column prop="word_count" label="字数" width="100" />
        <el-table-column
          prop="uploaded_platform"
          label="上传平台"
          width="140"
        />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button link @click="openDialog(row)">编辑</el-button>
            <el-button link @click="copyStatus(row, '待上传')"
              >标记待上传</el-button
            >
            <el-button link type="danger" @click="remove(row.id)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="visible" width="820px" title="编辑章节">
      <el-form :model="form" label-width="96px">
        <el-form-item label="章节标题"
          ><el-input v-model="form.title"
        /></el-form-item>
        <el-form-item label="章节序号"
          ><el-input-number v-model="form.chapter_number" :min="1"
        /></el-form-item>
        <el-form-item label="章节状态">
          <el-select v-model="form.status">
            <el-option
              v-for="item in statuses"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="上传平台"
          ><el-input v-model="form.uploaded_platform"
        /></el-form-item>
        <el-form-item label="正文"
          ><el-input v-model="form.content" type="textarea" :rows="12"
        /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import NovelSelect from "../components/NovelSelect.vue";
import { chapterApi, novelApi } from "../api";

const novels = ref([]);
const novelId = ref(null);
const list = ref([]);
const visible = ref(false);
const statuses = ["草稿", "已润色", "待上传", "已上传"];
const form = reactive({
  id: null,
  outline_id: null,
  chapter_number: 1,
  title: "",
  content: "",
  highlights: "",
  foreshadowing: "",
  status: "草稿",
  uploaded_platform: "",
});

const pipelineStats = computed(() => [
  { label: "章节总数", value: list.value.length, caption: "当前项目全部章节" },
  {
    label: "草稿",
    value: stageItems("草稿").length,
    caption: "待继续写作或完善",
  },
  {
    label: "待上传",
    value: stageItems("待上传").length,
    caption: "需整理投稿信息",
  },
  {
    label: "已上传",
    value: stageItems("已上传").length,
    caption: "已有平台投递记录",
  },
]);

function stageItems(status) {
  return list.value.filter((item) => item.status === status);
}
async function loadNovels() {
  novels.value = await novelApi.list();
  if (novels.value[0]) novelId.value = novels.value[0].id;
}
async function loadList() {
  if (novelId.value) list.value = await chapterApi.list(novelId.value);
}
function openDialog(row) {
  Object.assign(form, row);
  visible.value = true;
}
async function submit() {
  await chapterApi.update(form.id, form);
  visible.value = false;
  loadList();
}
async function copyStatus(row, status) {
  await chapterApi.update(row.id, { ...row, status });
  loadList();
}
async function remove(id) {
  await chapterApi.remove(id);
  loadList();
}
watch(novelId, loadList);
onMounted(loadNovels);
</script>

<style scoped>
.pipeline-shell {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 18px 0;
}
.stage-panel {
  padding: 16px;
  min-height: 320px;
}
.chapter-tile {
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}
.chapter-tile h3 {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
}
.chapter-tile p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 13px;
}
.tile-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.mini-empty {
  padding: 18px 0;
  color: var(--muted);
  text-align: center;
}
@media (max-width: 1280px) {
  .pipeline-shell {
    grid-template-columns: 1fr;
  }
}
</style>
