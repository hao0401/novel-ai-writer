<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">RAG MEMORY</div>
        <h1>素材库 / 设定库</h1>
        <p>
          这里保存角色卡、平台规则、伏笔、参考资料和设定补丁。生成章节时系统会按小说、大纲和指令自动检索相关素材并注入上下文。
        </p>
      </div>
      <el-button type="primary" @click="openDialog()">新增素材</el-button>
    </div>

    <div class="section-card">
      <div class="toolbar-row">
        <NovelSelect v-model="novelId" :novels="novels" />
        <span class="muted">当前作品素材 {{ list.length }} 条</span>
      </div>
    </div>

    <div v-if="list.length" class="knowledge-grid">
      <article
        v-for="item in list"
        :key="item.id"
        class="paper-card knowledge-card"
      >
        <div class="panel-title">
          <span class="pill">{{ item.item_type }}</span>
          <div>
            <el-button link @click="openDialog(item)">编辑</el-button>
            <el-button link type="danger" @click="remove(item.id)"
              >删除</el-button
            >
          </div>
        </div>
        <h2>{{ item.title }}</h2>
        <div class="tag-line">{{ item.keywords || "未设置关键词" }}</div>
        <p>{{ item.content }}</p>
      </article>
    </div>
    <div v-else class="empty-panel">
      暂无素材。建议先补充人物隐藏动机、世界规则、平台投稿要求或长线伏笔。
    </div>

    <el-dialog
      v-model="visible"
      :title="form.id ? '编辑素材' : '新增素材'"
      width="720px"
    >
      <el-form :model="form" label-width="86px">
        <el-row :gutter="14">
          <el-col :span="14"
            ><el-form-item label="标题"
              ><el-input v-model="form.title" /></el-form-item
          ></el-col>
          <el-col :span="10">
            <el-form-item label="类型">
              <el-select v-model="form.item_type">
                <el-option label="设定" value="设定" />
                <el-option label="角色卡" value="角色卡" />
                <el-option label="伏笔" value="伏笔" />
                <el-option label="参考资料" value="参考资料" />
                <el-option label="平台规则" value="平台规则" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关键词"
          ><el-input
            v-model="form.keywords"
            placeholder="用逗号分隔，生成时用于检索"
        /></el-form-item>
        <el-form-item label="内容"
          ><el-input v-model="form.content" type="textarea" :rows="9"
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
import { onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import NovelSelect from "../components/NovelSelect.vue";
import { knowledgeApi, novelApi } from "../api";

const novels = ref([]);
const novelId = ref(null);
const list = ref([]);
const visible = ref(false);
const form = reactive({
  id: null,
  novel_id: null,
  title: "",
  item_type: "设定",
  keywords: "",
  content: "",
});

function reset() {
  Object.assign(form, {
    id: null,
    novel_id: novelId.value,
    title: "",
    item_type: "设定",
    keywords: "",
    content: "",
  });
}

function openDialog(row) {
  reset();
  if (row) Object.assign(form, row);
  visible.value = true;
}

async function loadNovels() {
  novels.value = await novelApi.list();
  if (!novelId.value && novels.value[0]) novelId.value = novels.value[0].id;
}

async function loadList() {
  if (!novelId.value) return;
  list.value = await knowledgeApi.list(novelId.value);
}

async function submit() {
  if (!form.title || !form.content)
    return ElMessage.warning("请填写标题和内容");
  if (form.id) await knowledgeApi.update(form.id, form);
  else await knowledgeApi.create(novelId.value, form);
  visible.value = false;
  ElMessage.success("已保存素材");
  await loadList();
}

async function remove(id) {
  await knowledgeApi.remove(id);
  ElMessage.success("已删除");
  await loadList();
}

watch(novelId, loadList);
onMounted(async () => {
  await loadNovels();
  await loadList();
});
</script>

<style scoped>
.toolbar-row {
  display: flex;
  align-items: center;
  gap: 14px;
}
.muted {
  color: var(--muted);
  font-size: 13px;
}
.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.knowledge-card h2 {
  margin: 12px 0 8px;
  font-size: 18px;
}
.knowledge-card p {
  color: var(--muted);
  line-height: 1.8;
  white-space: pre-wrap;
}
@media (max-width: 1000px) {
  .knowledge-grid {
    grid-template-columns: 1fr;
  }
}
</style>
