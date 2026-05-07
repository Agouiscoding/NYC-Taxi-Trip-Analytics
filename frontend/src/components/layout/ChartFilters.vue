<template>
  <div v-if="controls.length" class="chart-filters">
    <label v-for="control in controls" :key="control.key">
      <span>{{ control.label }}</span>
      <input
        v-if="control.type === 'search'"
        type="search"
        :value="control.value"
        :placeholder="control.placeholder || 'Search'"
        @input="$emit('update:control', control.key, $event.target.value)"
      />
      <div v-else-if="control.type === 'limit'" class="limit-filter">
        <select
          :value="presetValue(control)"
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
          type="number"
          :min="control.min"
          :max="control.max"
          :step="control.step || 1"
          :value="stringValue(control.value)"
          @change="emitControl(control, $event.target.value)"
        />
        <em>max {{ control.max }}</em>
      </div>
      <select
        v-else
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
    </label>
  </div>
</template>

<script setup>
defineProps({
  controls: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:control"]);

function stringValue(value) {
  return value === null || value === undefined ? "" : String(value);
}

function presetValue(control) {
  const matchedOption = control.options?.find((option) => stringValue(option.value) === stringValue(control.value));
  return matchedOption ? stringValue(matchedOption.value) : "";
}

function emitControl(control, rawValue) {
  const matchedOption = control.options?.find((option) => stringValue(option.value) === rawValue);
  let value = matchedOption ? matchedOption.value : rawValue;

  if (control.valueType === "number" && value !== null && value !== "") {
    value = Number(value);
  }

  emit("update:control", control.key, value);
}
</script>
