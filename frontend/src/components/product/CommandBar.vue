<template>
  <header class="command-bar">
    <div>
      <h2>{{ title }}</h2>
    </div>

    <div class="command-controls command-controls--refresh-only">
      <button class="icon-button command-refresh" type="button" title="Reload data" @click="$emit('reload')">
        <RefreshCw :size="18" />
      </button>
    </div>
  </header>
</template>

<script setup>
import { RefreshCw } from "lucide-vue-next";

defineProps({
  title: {
    type: String,
    required: true,
  },
});

defineEmits(["reload"]);
</script>
