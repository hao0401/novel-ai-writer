<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">PROJECT LIBRARY</div>
        <h1>小说项目管理</h1>
        <p>
          这里是作品资产库，保存题材定位、目标平台、简介、标签和卖点，后续 AI
          生成都会围绕这些信息展开。
        </p>
        <p class="next-hint">
          先在这里创建一部小说，然后去「AI 创意中心」生成包装信息。
        </p>
      </div>
      <el-button type="primary" @click="openDialog()">新建项目</el-button>
    </div>
    <div class="project-grid" v-if="list.length">
      <article
        v-for="item in list"
        :key="item.id"
        class="project-card paper-card"
      >
        <div class="panel-title">
          <span class="pill">{{ item.genre }} · {{ item.status }}</span>
          <div>
            <el-button link @click="openDialog(item)">编辑</el-button>
            <el-button link type="danger" @click="remove(item.id)"
              >删除</el-button
            >
          </div>
        </div>
        <h2>{{ item.title }}</h2>
        <p>{{ item.synopsis || "暂无简介" }}</p>
        <div class="project-meta">
          <span>风格：{{ item.style || "未设置" }}</span>
          <span>平台：{{ item.target_platform || "未设置" }}</span>
        </div>
        <div class="tag-line">{{ item.tags || "暂无标签" }}</div>
        <div class="selling">{{ item.selling_points || "暂无卖点" }}</div>
      </article>
    </div>
    <div v-else class="empty-panel">还没有小说项目，先创建一部作品。</div>

    <div class="section-card table-fallback">
      <el-table :data="list">
        <el-table-column prop="title" label="小说名称" min-width="180" />
        <el-table-column prop="genre" label="类型" width="100" />
        <el-table-column prop="style" label="风格" width="120" />
        <el-table-column prop="target_platform" label="目标平台" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="tags" label="标签" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row.id)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog
      v-model="visible"
      :title="form.id ? '编辑小说项目' : '创建小说项目'"
      width="720px"
    >
      <el-form :model="form" label-width="92px">
        <el-row :gutter="16">
          <el-col :span="12"
            ><el-form-item label="小说名称"
              ><el-input v-model="form.title" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="小说类型"
              ><el-select v-model="form.genre"
                ><el-option
                  v-for="item in genres"
                  :key="item"
                  :label="item"
                  :value="item" /></el-select></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="小说风格"
              ><el-input v-model="form.style" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="目标平台"
              ><el-input v-model="form.target_platform" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="标签"
          ><el-input v-model="form.tags" placeholder="多个标签用逗号分隔"
        /></el-form-item>
        <el-form-item label="卖点"
          ><el-input v-model="form.selling_points" type="textarea" :rows="3"
        /></el-form-item>
        <el-form-item label="简介"
          ><el-input v-model="form.synopsis" type="textarea" :rows="4"
        /></el-form-item>
        <el-form-item label="创作状态"
          ><el-select v-model="form.status"
            ><el-option
              v-for="item in statuses"
              :key="item"
              :label="item"
              :value="item" /></el-select
        ></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { novelApi } from "../api";

const genres = [
  "玄幻",
  "都市",
  "言情",
  "悬疑",
  "科幻",
  "历史",
  "仙侠",
  "游戏",
  "校园",
  "现实题材",
];
const statuses = ["构思中", "创作中", "待投稿", "已投稿", "暂停"];
const list = ref([]);
const visible = ref(false);
const form = reactive({
  id: null,
  title: "",
  genre: "都市",
  style: "",
  target_platform: "",
  synopsis: "",
  tags: "",
  selling_points: "",
  status: "构思中",
});

function reset() {
  Object.assign(form, {
    id: null,
    title: "",
    genre: "都市",
    style: "",
    target_platform: "",
    synopsis: "",
    tags: "",
    selling_points: "",
    status: "构思中",
  });
}
function openDialog(row) {
  reset();
  if (row) Object.assign(form, row);
  visible.value = true;
}
async function load() {
  list.value = await novelApi.list();
}
async function submit() {
  const payload = { ...form };
  if (form.id) await novelApi.update(form.id, payload);
  else await novelApi.create(payload);
  visible.value = false;
  load();
}
async function remove(id) {
  await novelApi.remove(id);
  load();
}
onMounted(load);
</script>

<style scoped>
.project-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
.project-card {
  padding: 20px;
}
.project-card h2 {
  margin: 12px 0 8px;
  font-size: 22px;
}
.project-card p {
  min-height: 72px;
  margin: 0;
  color: var(--muted);
  line-height: 1.75;
}
.project-meta {
  display: grid;
  gap: 6px;
  margin: 14px 0;
  color: var(--muted);
  font-size: 13px;
}
.tag-line {
  padding: 10px;
  color: var(--teal);
  background: var(--teal-soft);
  border-radius: 8px;
  font-size: 13px;
}
.selling {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  color: var(--ink-soft);
  line-height: 1.65;
}
.table-fallback {
  display: none;
  margin-top: 18px;
}
@media (max-width: 1280px) {
  .project-grid {
    grid-template-columns: 1fr;
  }
}
</style>
