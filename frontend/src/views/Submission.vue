<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">SUBMISSION OPS</div>
        <h1>投稿整理</h1>
        <p>
          这里不替你自动上传平台，只帮你把书名、简介、标签和章节正文整理好，方便复制或导出。
        </p>
        <p class="next-hint">
          点“生成投稿预览”，确认内容后复制或导出 TXT/DOCX。
        </p>
      </div>
      <div class="toolbar">
        <NovelSelect v-model="novelId" :novels="novels" />
        <el-button @click="loadPreview">生成投稿预览</el-button>
        <el-button type="primary" @click="openDialog()">新增投稿记录</el-button>
        <el-button @click="$router.push('/stats')">查看统计</el-button>
      </div>
    </div>
    <div class="bento-grid">
      <div class="bento span-7 manuscript-panel">
        <div class="panel-title">
          <strong>投稿内容整理</strong>
          <div class="toolbar">
            <el-button @click="copyText">复制内容</el-button>
            <el-button @click="download('txt')">导出 TXT</el-button>
            <el-button @click="download('docx')">导出 DOCX</el-button>
          </div>
        </div>
        <div class="manuscript-preview">{{ previewText }}</div>
      </div>
      <div class="bento span-5">
        <div class="panel-title">
          <strong>投稿记录</strong>
          <span class="pill">{{ records.length }} 条记录</span>
        </div>
        <el-table :data="records" style="margin-top: 14px">
          <el-table-column prop="platform" label="平台" width="120" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column
            prop="platform_link"
            label="平台链接"
            min-width="140"
            show-overflow-tooltip
          />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link @click="openDialog(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <el-dialog v-model="visible" width="720px" title="投稿记录">
      <el-form :model="form" label-width="90px">
        <el-form-item label="小说项目"
          ><NovelSelect v-model="form.novel_id" :novels="novels"
        /></el-form-item>
        <el-form-item label="目标平台"
          ><el-select v-model="form.platform"
            ><el-option
              v-for="item in platforms"
              :key="item"
              :label="item"
              :value="item" /></el-select
        ></el-form-item>
        <el-form-item label="投稿状态"
          ><el-select v-model="form.status"
            ><el-option
              v-for="item in statuses"
              :key="item"
              :label="item"
              :value="item" /></el-select
        ></el-form-item>
        <el-form-item label="平台链接"
          ><el-input v-model="form.platform_link"
        /></el-form-item>
        <el-form-item label="备注"
          ><el-input v-model="form.remarks" type="textarea" :rows="3"
        /></el-form-item>
        <el-form-item label="整理内容"
          ><el-input v-model="form.compiled_content" type="textarea" :rows="5"
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
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import axios from "axios";
import NovelSelect from "../components/NovelSelect.vue";
import { novelApi, submissionApi } from "../api";

const novels = ref([]);
const novelId = ref(null);
const preview = ref(null);
const records = ref([]);
const visible = ref(false);
const platforms = [
  "番茄小说",
  "起点中文网",
  "七猫小说",
  "晋江文学城",
  "纵横中文网",
  "其他平台",
];
const statuses = ["未整理", "待上传", "已上传", "已退回", "已发布"];
const form = reactive({
  id: null,
  novel_id: null,
  chapter_id: null,
  platform: "番茄小说",
  status: "未整理",
  uploaded_at: null,
  platform_link: "",
  remarks: "",
  compiled_content: "",
});

const previewText = computed(() => {
  if (!preview.value) return "请先选择小说项目并生成投稿预览。";
  return [
    `书名：${preview.value.title}`,
    `作者名：${preview.value.author_name}`,
    `小说简介：${preview.value.synopsis}`,
    `小说分类：${preview.value.category}`,
    `小说标签：${preview.value.tags}`,
    "",
    ...(preview.value.chapters || []).map(
      (item) => `${item.title}\n${item.content}`,
    ),
  ].join("\n\n");
});

async function loadBase() {
  novels.value = await novelApi.list();
  records.value = await submissionApi.list();
  if (novels.value[0]) {
    novelId.value = novels.value[0].id;
    form.novel_id = novels.value[0].id;
  }
}
async function loadPreview() {
  preview.value = await submissionApi.preview(novelId.value);
}
async function copyText() {
  await navigator.clipboard.writeText(previewText.value);
  ElMessage.success("已复制投稿内容");
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
function openDialog(row) {
  Object.assign(form, {
    id: null,
    novel_id: novelId.value,
    chapter_id: null,
    platform: "番茄小说",
    status: "未整理",
    uploaded_at: null,
    platform_link: "",
    remarks: "",
    compiled_content: previewText.value,
  });
  if (row) Object.assign(form, row);
  visible.value = true;
}
async function submit() {
  if (form.id) await submissionApi.update(form.id, form);
  else await submissionApi.create(form);
  visible.value = false;
  records.value = await submissionApi.list();
}
onMounted(loadBase);
</script>

<style scoped>
.manuscript-panel {
  min-height: 680px;
}
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
.manuscript-preview {
  min-height: 560px;
  max-height: 680px;
  overflow: auto;
  margin-top: 14px;
  padding: 30px 34px;
  color: var(--ink-soft);
  background:
    linear-gradient(to bottom, rgba(31, 35, 32, 0.045) 1px, transparent 1px),
    #fffef8;
  background-size:
    100% 34px,
    auto;
  border: 1px solid var(--line);
  border-radius: 10px;
  white-space: pre-wrap;
  line-height: 2;
  font-family: "Source Han Serif SC", "Songti SC", SimSun, serif;
}
</style>
