<template>
  <div>
    <div class="page-title">
      <div>
        <div class="eyebrow">CHARACTER BIBLE</div>
        <h1>人物设定库</h1>
        <p>
          以角色资产卡管理主角、配角、反派和关键人物。章节生成时会读取这些设定，避免人物目标、能力和关系前后冲突。
        </p>
        <p class="next-hint">
          建议先补主角和关键配角，再去世界观设定或大纲工坊。
        </p>
      </div>
      <div class="toolbar">
        <NovelSelect v-model="novelId" :novels="novels" />
        <el-select v-model="roleType" style="width: 140px">
          <el-option label="主角" value="主角" />
          <el-option label="配角" value="配角" />
          <el-option label="反派" value="反派" />
          <el-option label="重要人物" value="重要人物" />
        </el-select>
        <el-button type="primary" :loading="generating" @click="generate"
          >AI 生成</el-button
        >
        <el-button @click="openDialog()">手动新增</el-button>
      </div>
    </div>

    <div class="asset-layout">
      <aside class="asset-sidebar paper-card">
        <div class="panel-title">
          <strong>角色结构</strong
          ><span class="pill">{{ list.length }} 人</span>
        </div>
        <div class="role-stat" v-for="item in roleStats" :key="item.role">
          <span>{{ item.role }}</span>
          <strong>{{ item.count }}</strong>
        </div>
        <div class="divider"></div>
        <div class="muted small">
          建议每部作品至少维护：主角、核心配角、主要反派、平台编辑或推进剧情的功能性人物。
        </div>
      </aside>

      <section class="character-grid" v-if="list.length">
        <article
          v-for="item in list"
          :key="item.id"
          class="character-card paper-card"
        >
          <div class="character-top">
            <div class="avatar">{{ item.name?.slice(0, 1) }}</div>
            <div>
              <h2>{{ item.name }}</h2>
              <span class="pill"
                >{{ item.role_type }} ·
                {{ item.identity || "身份未设定" }}</span
              >
            </div>
          </div>
          <div class="trait-block">
            <label>性格</label>
            <p>{{ item.personality || "未填写" }}</p>
          </div>
          <div class="trait-block">
            <label>目标</label>
            <p>{{ item.goal || "未填写" }}</p>
          </div>
          <div class="trait-block compact">
            <label>能力 / 背景</label>
            <p>
              {{ item.ability || "未填写能力" }}；{{
                item.background || "未填写背景"
              }}
            </p>
          </div>
          <div class="card-footer">
            <span>{{ item.relation_to_protagonist || "关系未设定" }}</span>
            <div>
              <el-button link @click="openDialog(item)">编辑</el-button>
              <el-button link type="danger" @click="remove(item.id)"
                >删除</el-button
              >
            </div>
          </div>
        </article>
      </section>
      <section v-else class="empty-panel">
        暂无人物设定，可先选择角色类型并使用 AI 生成。
      </section>
    </div>

    <el-dialog v-model="visible" width="820px" title="人物设定">
      <el-form :model="form" label-width="96px">
        <el-row :gutter="16">
          <el-col :span="12"
            ><el-form-item label="姓名"
              ><el-input v-model="form.name" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="类型"
              ><el-input v-model="form.role_type" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="身份"
          ><el-input v-model="form.identity"
        /></el-form-item>
        <el-form-item label="性格"
          ><el-input v-model="form.personality" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="目标"
          ><el-input v-model="form.goal" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="能力"
          ><el-input v-model="form.ability" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="背景经历"
          ><el-input v-model="form.background" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="与主角关系"
          ><el-input v-model="form.relation_to_protagonist"
        /></el-form-item>
        <el-form-item label="剧情作用"
          ><el-input v-model="form.plot_function" type="textarea" :rows="2"
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
import { aiApi, characterApi, novelApi } from "../api";

const novels = ref([]);
const novelId = ref(null);
const roleType = ref("主角");
const list = ref([]);
const visible = ref(false);
const generating = ref(false);
const form = reactive({
  id: null,
  name: "",
  role_type: "主角",
  identity: "",
  personality: "",
  goal: "",
  ability: "",
  background: "",
  relation_to_protagonist: "",
  plot_function: "",
});

const roleStats = computed(() =>
  ["主角", "配角", "反派", "重要人物"].map((role) => ({
    role,
    count: list.value.filter((item) => item.role_type === role).length,
  })),
);

function reset() {
  Object.assign(form, {
    id: null,
    name: "",
    role_type: roleType.value,
    identity: "",
    personality: "",
    goal: "",
    ability: "",
    background: "",
    relation_to_protagonist: "",
    plot_function: "",
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
  if (novelId.value) list.value = await characterApi.list(novelId.value);
}
async function generate() {
  generating.value = true;
  try {
    const res = await aiApi.characters({
      novel_id: novelId.value,
      role_type: roleType.value,
    });
    for (const item of res.characters)
      await characterApi.create(novelId.value, item);
    await loadList();
  } finally {
    generating.value = false;
  }
}
async function submit() {
  if (form.id) await characterApi.update(form.id, form);
  else await characterApi.create(novelId.value, form);
  visible.value = false;
  loadList();
}
async function remove(id) {
  await characterApi.remove(id);
  loadList();
}
watch(novelId, loadList);
onMounted(loadNovels);
</script>

<style scoped>
.asset-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 16px;
}
.next-hint {
  margin-top: 8px !important;
  color: var(--teal) !important;
  font-size: 13px;
}
.asset-sidebar {
  padding: 18px;
  height: fit-content;
  position: sticky;
  top: 96px;
}
.role-stat {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}
.role-stat span {
  color: var(--muted);
}
.role-stat strong {
  color: var(--teal);
  font-size: 20px;
}
.divider {
  height: 1px;
  background: var(--line);
  margin: 16px 0;
}
.small {
  font-size: 13px;
  line-height: 1.8;
}
.character-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.character-card {
  padding: 20px;
}
.character-top {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 16px;
}
.avatar {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  color: #fffdf7;
  background: var(--teal);
  border-radius: 12px;
  font-size: 22px;
  font-weight: 800;
}
.character-card h2 {
  margin: 0 0 8px;
  font-size: 22px;
}
.trait-block {
  margin: 12px 0;
}
.trait-block label {
  display: block;
  margin-bottom: 5px;
  color: var(--faint);
  font-size: 12px;
}
.trait-block p {
  margin: 0;
  color: var(--ink-soft);
  line-height: 1.75;
}
.trait-block.compact p {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  color: var(--muted);
}
@media (max-width: 1180px) {
  .asset-layout {
    grid-template-columns: 1fr;
  }
  .asset-sidebar {
    position: static;
  }
  .character-grid {
    grid-template-columns: 1fr;
  }
}
</style>
