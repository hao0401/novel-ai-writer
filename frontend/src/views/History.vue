<template>
  <div>
    <div class="page-title">
      <div>
        <h1>AI 生成历史</h1>
        <p>保留每次创意生成、人物设定、世界观、大纲、正文、续写和润色记录。</p>
      </div>
    </div>
    <div class="section-card">
      <el-table :data="records">
        <el-table-column prop="generation_type" label="生成类型" width="120" />
        <el-table-column prop="novel_id" label="所属小说ID" width="110" />
        <el-table-column
          prop="input_text"
          label="输入内容"
          min-width="240"
          show-overflow-tooltip
        />
        <el-table-column
          prop="output_text"
          label="输出内容"
          min-width="320"
          show-overflow-tooltip
        />
        <el-table-column prop="created_at" label="生成时间" width="200" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { aiApi } from "../api";
const records = ref([]);
onMounted(async () => {
  records.value = await aiApi.records();
});
</script>
