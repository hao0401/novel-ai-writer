<template>
  <div>
    <div class="page-title">
      <div>
        <h1>大纲生成</h1>
        <p>支持全书、分卷和章节大纲生成，并可批量写入数据库。</p>
        <p class="next-hint">
          先生成并保存章节大纲，再去「章节写作台」生成正文。
        </p>
      </div>
    </div>
    <div class="bento-grid">
      <div class="bento span-4">
        <el-form :model="form" label-position="top">
          <el-form-item label="小说项目"
            ><NovelSelect v-model="form.novel_id" :novels="novels"
          /></el-form-item>
          <el-form-item label="章节数"
            ><el-input-number v-model="form.outline_count" :min="3" :max="30"
          /></el-form-item>
          <el-button type="primary" @click="generate">AI 生成大纲</el-button>
          <el-button @click="saveBatch" :disabled="!generated.chapters"
            >批量保存章节大纲</el-button
          >
          <el-button @click="$router.push('/chapter-editor')"
            >下一步：写章节</el-button
          >
        </el-form>
        <div
          class="result-panel"
          v-if="generated.full_outline"
          style="margin-top: 16px"
        >
          全书大纲：
          {{ generated.full_outline }}

          分卷大纲：
          {{ generated.volume_outline }}
        </div>
      </div>
      <div class="bento span-8">
        <strong>章节大纲列表</strong>
        <el-table :data="generated.chapters || list" style="margin-top: 14px">
          <el-table-column prop="chapter_number" label="章序" width="80" />
          <el-table-column
            prop="chapter_title"
            label="章节标题"
            min-width="160"
          />
          <el-table-column
            prop="chapter_goal"
            label="本章目标"
            min-width="160"
            show-overflow-tooltip
          />
          <el-table-column
            prop="conflict"
            label="冲突点"
            min-width="160"
            show-overflow-tooltip
          />
          <el-table-column
            prop="highlight"
            label="爽点"
            min-width="140"
            show-overflow-tooltip
          />
          <el-table-column prop="expected_words" label="预计字数" width="110" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import NovelSelect from "../components/NovelSelect.vue";
import { aiApi, novelApi, outlineApi } from "../api";

const novels = ref([]);
const list = ref([]);
const generated = ref({});
const form = reactive({ novel_id: null, outline_count: 6 });

async function loadNovels() {
  novels.value = await novelApi.list();
  if (novels.value[0]) form.novel_id = novels.value[0].id;
}
async function loadList() {
  if (form.novel_id) list.value = await outlineApi.list(form.novel_id);
}
async function generate() {
  generated.value = await aiApi.outlines(form);
}
async function saveBatch() {
  await outlineApi.batch(form.novel_id, generated.value.chapters);
  ElMessage.success("已批量保存大纲");
  loadList();
}
watch(() => form.novel_id, loadList);
onMounted(loadNovels);
</script>

<style scoped>
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
</style>
