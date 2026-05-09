<template>
  <el-select
    v-model="model"
    placeholder="请选择小说项目"
    filterable
    style="width: 260px"
  >
    <el-option
      v-for="item in novels"
      :key="item.id"
      :label="item.title"
      :value="item.id"
    />
  </el-select>
</template>

<script setup>
const model = defineModel();
defineProps({ novels: { type: Array, default: () => [] } });
</script>
