<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">ANALYTICS</div>
        <h1>数据统计</h1>
        <p>
          把创作活动、章节规模和题材结构整理成一个轻量分析面板，用于本地创作管理和项目展示。
        </p>
      </div>
      <span class="pill">本地运营视图</span>
    </div>

    <div class="bento-grid">
      <div class="bento span-3" v-for="item in metrics" :key="item.label">
        <div class="muted">{{ item.label }}</div>
        <div class="metric">{{ item.value }}</div>
        <div class="metric-caption">{{ item.caption }}</div>
      </div>

      <div class="bento span-7">
        <div class="panel-title">
          <strong>题材结构分布</strong>
          <span class="pill">{{ genreTotal }} 个项目</span>
        </div>
        <div ref="pieRef" style="height: 340px"></div>
      </div>

      <div class="bento span-5">
        <div class="panel-title">
          <strong>运营摘要</strong>
          <span class="muted">Summary</span>
        </div>
        <div class="summary-grid">
          <section>
            <label>平均每部小说字数</label>
            <strong>{{ avgWords }}</strong>
          </section>
          <section>
            <label>平均每章字数</label>
            <strong>{{ avgChapterWords }}</strong>
          </section>
          <section>
            <label>待上传占比</label>
            <strong>{{ pendingRate }}</strong>
          </section>
          <section>
            <label>已上传占比</label>
            <strong>{{ uploadedRate }}</strong>
          </section>
        </div>
      </div>

      <div class="bento span-12">
        <div class="panel-title">
          <strong>项目结构表</strong>
          <span class="muted">Genre Mix</span>
        </div>
        <el-table :data="data.genre_distribution || []">
          <el-table-column prop="name" label="题材类型" min-width="180" />
          <el-table-column prop="value" label="项目数量" width="120" />
          <el-table-column label="占比">
            <template #default="{ row }">
              <el-progress
                :percentage="genrePercent(row.value)"
                :show-text="false"
                color="#1d5d58"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import * as echarts from "echarts";
import { dashboardApi } from "../api";

const data = ref({ summary: {}, genre_distribution: [] });
const pieRef = ref(null);
const summary = computed(() => data.value.summary || {});
const genreTotal = computed(() =>
  (data.value.genre_distribution || []).reduce(
    (sum, item) => sum + item.value,
    0,
  ),
);
const avgWords = computed(() => {
  const novels = summary.value.novel_count || 1;
  return Math.round((summary.value.total_words || 0) / novels);
});
const avgChapterWords = computed(() => {
  const chapters = summary.value.chapter_count || 1;
  return Math.round((summary.value.total_words || 0) / chapters);
});
const pendingRate = computed(() => {
  const total = summary.value.chapter_count || 1;
  return `${Math.round(((summary.value.pending_upload_count || 0) / total) * 100)}%`;
});
const uploadedRate = computed(() => {
  const total = summary.value.chapter_count || 1;
  return `${Math.round(((summary.value.uploaded_count || 0) / total) * 100)}%`;
});
const metrics = computed(() => [
  {
    label: "小说项目数",
    value: summary.value.novel_count || 0,
    caption: "当前作品数量",
  },
  {
    label: "章节数量",
    value: summary.value.chapter_count || 0,
    caption: "累计章节规模",
  },
  {
    label: "总创作字数",
    value: summary.value.total_words || 0,
    caption: "正文累计字数",
  },
  {
    label: "AI 生成次数",
    value: summary.value.ai_count || 0,
    caption: "调用记录总量",
  },
]);

function genrePercent(value) {
  const total = genreTotal.value || 1;
  return Math.round((value / total) * 100);
}

onMounted(async () => {
  data.value = await dashboardApi.stats();
  await nextTick();
  const chart = echarts.init(pieRef.value);
  chart.setOption({
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        type: "pie",
        radius: ["42%", "70%"],
        center: ["50%", "44%"],
        itemStyle: { borderRadius: 8, borderColor: "#fffdf7", borderWidth: 3 },
        label: { formatter: "{b}\n{d}%" },
        data: data.value.genre_distribution,
      },
    ],
  });
});
</script>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.summary-grid section {
  min-height: 120px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #fbf8f1;
}
.summary-grid label {
  display: block;
  margin-bottom: 12px;
  color: var(--muted);
  line-height: 1.6;
}
.summary-grid strong {
  color: var(--teal);
  font-size: 28px;
}
@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
