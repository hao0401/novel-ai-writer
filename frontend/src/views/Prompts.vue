<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">PROMPT OPS</div>
        <h1>Prompt 模板管理</h1>
        <p>
          按创作任务维护提示词模板。章节生成会优先使用“章节正文”模板，并动态注入小说设定、人物、世界观、历史摘要和素材库。
        </p>
      </div>
      <el-button type="primary" @click="openDialog()">新增模板</el-button>
    </div>

    <div class="section-card">
      <el-table :data="list">
        <el-table-column prop="task_type" label="任务类型" width="130" />
        <el-table-column prop="name" label="模板名称" width="150" />
        <el-table-column prop="genre" label="题材" width="100">
          <template #default="{ row }">{{ row.genre || "通用" }}</template>
        </el-table-column>
        <el-table-column
          prop="system_prompt"
          label="系统提示词"
          min-width="280"
          show-overflow-tooltip
        />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"
            ><el-tag :type="row.enabled ? 'success' : 'info'">{{
              row.enabled ? "启用" : "停用"
            }}</el-tag></template
          >
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }"
            ><el-button link @click="openDialog(row)">编辑</el-button></template
          >
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="visible"
      :title="form.id ? '编辑 Prompt 模板' : '新增 Prompt 模板'"
      width="780px"
    >
      <el-form :model="form" label-width="100px">
        <el-row :gutter="14">
          <el-col :span="8"
            ><el-form-item label="任务类型"
              ><el-input v-model="form.task_type" /></el-form-item
          ></el-col>
          <el-col :span="8"
            ><el-form-item label="模板名称"
              ><el-input v-model="form.name" /></el-form-item
          ></el-col>
          <el-col :span="8"
            ><el-form-item label="题材"
              ><el-input
                v-model="form.genre"
                placeholder="留空为通用" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="系统提示词"
          ><el-input v-model="form.system_prompt" type="textarea" :rows="5"
        /></el-form-item>
        <el-form-item label="用户模板"
          ><el-input v-model="form.user_template" type="textarea" :rows="6"
        /></el-form-item>
        <el-form-item label="启用"
          ><el-switch
            v-model="form.enabled"
            :active-value="1"
            :inactive-value="0"
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
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { promptApi } from "../api";

const list = ref([]);
const visible = ref(false);
const form = reactive({
  id: null,
  task_type: "chapter",
  genre: "",
  name: "",
  system_prompt: "",
  user_template: "",
  enabled: 1,
});

function reset() {
  Object.assign(form, {
    id: null,
    task_type: "chapter",
    genre: "",
    name: "",
    system_prompt: "",
    user_template: "",
    enabled: 1,
  });
}

function openDialog(row) {
  reset();
  if (row) Object.assign(form, row);
  visible.value = true;
}

async function load() {
  list.value = await promptApi.list();
}

async function submit() {
  if (!form.task_type || !form.system_prompt)
    return ElMessage.warning("请填写任务类型和系统提示词");
  if (form.id) await promptApi.update(form.id, form);
  else await promptApi.create(form);
  visible.value = false;
  ElMessage.success("已保存模板");
  await load();
}

onMounted(load);
</script>
