<template>
  <header class="command-bar">
    <div>
      <p class="eyebrow">{{ eyebrow }}</p>
      <h2>{{ title }}</h2>
    </div>

    <div v-if="controls.length" class="command-controls">
      <label v-for="control in controls" :key="control.key">
        <span>{{ control.label }}</span>
        <select
          v-if="control.type !== 'search'"
          :value="stringValue(control.value)"
          @change="emitControl(control, $event.target.value)"
        >
          <option
            v-for="option in control.options"
            :key="`${control.key}-${stringValue(option.value)}`"
            :value="stringValue(option.value)"
          >
            {{ option.label }}
          </option>
        </select>
        <input
          v-else
          type="search"
          :value="control.value"
          :placeholder="control.placeholder || 'Search'"
          @input="$emit('update:control', control.key, $event.target.value)"
        />
      </label>

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
  controls: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:control", "reload"]);

function stringValue(value) {
  return value === null || value === undefined ? "" : String(value);
}

function emitControl(control, rawValue) {
  const matchedOption = control.options.find((option) => stringValue(option.value) === rawValue);
  let value = matchedOption ? matchedOption.value : rawValue;

  if (control.valueType === "number" && value !== null && value !== "") {
    value = Number(value);
  }

  emit("update:control", control.key, value);
}
</script>
