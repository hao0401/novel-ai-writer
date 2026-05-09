<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">WORLD BIBLE</div>
        <h1>世界观设定库</h1>
        <p>
          把世界背景、势力、等级、能力规则和禁忌沉淀成统一设定卡，作为后续章节生成的约束底座。
        </p>
        <p class="next-hint">
          这一步完成后，建议进入「大纲工坊」生成全书和章节结构。
        </p>
      </div>
      <div class="toolbar">
        <NovelSelect v-model="novelId" :novels="novels" />
        <el-button type="primary" :loading="generating" @click="generate"
          >AI 生成世界观</el-button
        >
        <el-button @click="openDialog()">手动新增</el-button>
      </div>
    </div>

    <div class="world-layout" v-if="list.length">
      <article
        v-for="item in list"
        :key="item.id"
        class="world-card paper-card"
      >
        <div class="world-hero">
          <div>
            <div class="eyebrow">SETTING CARD #{{ item.id }}</div>
            <h2>{{ item.world_background || "未填写世界背景" }}</h2>
          </div>
          <div>
            <el-button link @click="openDialog(item)">编辑</el-button>
            <el-button link type="danger" @click="remove(item.id)"
              >删除</el-button
            >
          </div>
        </div>

        <div class="setting-grid">
          <section>
            <label>时代环境</label>
            <p>{{ item.era_environment || "未填写" }}</p>
          </section>
          <section>
            <label>地理区域</label>
            <p>{{ item.geography || "未填写" }}</p>
          </section>
          <section>
            <label>势力组织</label>
            <p>{{ item.organizations || "未填写" }}</p>
          </section>
          <section>
            <label>等级体系</label>
            <p>{{ item.hierarchy || "未填写" }}</p>
          </section>
          <section>
            <label>能力体系</label>
            <p>{{ item.power_system || "未填写" }}</p>
          </section>
          <section>
            <label>重要规则</label>
            <p>{{ item.important_rules || "未填写" }}</p>
          </section>
          <section class="danger-zone">
            <label>禁忌或限制</label>
            <p>{{ item.taboos || "未填写" }}</p>
          </section>
        </div>
      </article>
    </div>
    <div v-else class="empty-panel">
      暂无世界观设定。建议先用 AI 生成一版，再人工校正规则。
    </div>

    <el-dialog v-model="visible" width="900px" title="世界观设定">
      <el-form :model="form" label-width="96px">
        <el-form-item label="世界背景"
          ><el-input v-model="form.world_background" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="时代环境"
          ><el-input v-model="form.era_environment" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="地理区域"
          ><el-input v-model="form.geography" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="势力组织"
          ><el-input v-model="form.organizations" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="等级体系"
          ><el-input v-model="form.hierarchy" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="能力体系"
          ><el-input v-model="form.power_system" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="重要规则"
          ><el-input v-model="form.important_rules" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="禁忌限制"
          ><el-input v-model="form.taboos" type="textarea" :rows="2"
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
import NovelSelect from "../components/NovelSelect.vue";
import { aiApi, novelApi, worldApi } from "../api";

const novels = ref([]);
const novelId = ref(null);
const list = ref([]);
const visible = ref(false);
const generating = ref(false);
const form = reactive({
  id: null,
  world_background: "",
  era_environment: "",
  geography: "",
  organizations: "",
  hierarchy: "",
  power_system: "",
  important_rules: "",
  taboos: "",
});

function reset() {
  Object.assign(form, {
    id: null,
    world_background: "",
    era_environment: "",
    geography: "",
    organizations: "",
    hierarchy: "",
    power_system: "",
    important_rules: "",
    taboos: "",
  });
}
function openDialog(row) {
  reset();
  if (row) Object.assign(form, row);
  visible.value = true;
}
async function loadNovels() {
  novels.value = await novelApi.list();
  if (novels.value[0]) novelId.value = novels.value[0].id;
}
async function loadList() {
  if (novelId.value) list.value = await worldApi.list(novelId.value);
}
async function generate() {
  generating.value = true;
  try {
    await worldApi.create(
      novelId.value,
      await aiApi.world({ novel_id: novelId.value }),
    );
    await loadList();
  } finally {
    generating.value = false;
  }
}
async function submit() {
  if (form.id) await worldApi.update(form.id, form);
  else await worldApi.create(novelId.value, form);
  visible.value = false;
  loadList();
}
async function remove(id) {
  await worldApi.remove(id);
  loadList();
}
watch(novelId, loadList);
onMounted(loadNovels);
</script>

<style scoped>
.world-layout {
  display: grid;
  gap: 16px;
}
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
.world-card {
  padding: 22px;
}
.world-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--line);
}
.world-hero h2 {
  max-width: 980px;
  margin: 8px 0 0;
  font-size: 24px;
  line-height: 1.55;
}
.setting-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}
.setting-grid section {
  min-height: 130px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #fbf8f1;
}
.setting-grid label {
  display: block;
  margin-bottom: 8px;
  color: var(--teal);
  font-weight: 700;
  font-size: 13px;
}
.setting-grid p {
  margin: 0;
  color: var(--ink-soft);
  line-height: 1.75;
}
.danger-zone {
  grid-column: span 3;
  border-color: #d7b8b2 !important;
  background: #fff8f5 !important;
}
@media (max-width: 1100px) {
  .setting-grid {
    grid-template-columns: 1fr;
  }
  .danger-zone {
    grid-column: span 1;
  }
}
</style>
