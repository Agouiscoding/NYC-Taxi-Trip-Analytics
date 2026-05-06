<template>
  <section v-if="mode === 'metrics'" class="metric-strip">
    <article
      v-for="(item, index) in items"
      :key="item.label"
      class="metric-tile"
      :style="{ '--tile-delay': `${index * 80 + 80}ms`, '--sweep-delay': `${index * 300}ms` }"
    >
      <div class="metric-tile__label">{{ item.label }}</div>
      <div class="metric-tile__value">{{ displayedValues[index] ?? item.value }}</div>
      <div class="metric-tile__note">{{ item.note }}</div>
    </article>
  </section>

  <section v-else class="context-strip">
    <article v-for="item in contextItems" :key="item.label" class="context-pill">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </article>
  </section>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  mode: {
    type: String,
    default: "metrics",
  },
  items: {
    type: Array,
    default: () => [],
  },
  contextItems: {
    type: Array,
    default: () => [],
  },
});

const displayedValues = ref([]);
const animationFrames = new Set();
const animationTimers = new Set();
const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false;

function parseDisplayValue(value) {
  const text = String(value ?? "");
  const match = text.match(/^([^0-9+-]*)([+-]?\d[\d,]*(?:\.\d+)?)(.*)$/);

  if (!match) {
    return null;
  }

  const [, prefix, numberText, suffix] = match;
  const decimals = numberText.includes(".") ? numberText.split(".").at(-1).length : 0;
  const target = Number(numberText.replaceAll(",", ""));

  if (!Number.isFinite(target)) {
    return null;
  }

  return { prefix, suffix, target, decimals };
}

function formatAnimatedValue(value, parsed) {
  return `${parsed.prefix}${value.toLocaleString("en-US", {
    minimumFractionDigits: parsed.decimals,
    maximumFractionDigits: parsed.decimals,
  })}${parsed.suffix}`;
}

function cancelAnimations() {
  animationFrames.forEach((frame) => cancelAnimationFrame(frame));
  animationTimers.forEach((timer) => window.clearTimeout(timer));
  animationFrames.clear();
  animationTimers.clear();
}

function animateMetric(index, parsed) {
  if (reduceMotion) {
    displayedValues.value[index] = formatAnimatedValue(parsed.target, parsed);
    return;
  }

  const duration = 1250;
  const startTime = performance.now();
  const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);

  const tick = (now) => {
    const progress = Math.min((now - startTime) / duration, 1);
    displayedValues.value[index] = formatAnimatedValue(parsed.target * easeOutQuart(progress), parsed);

    if (progress < 1) {
      const frame = requestAnimationFrame(tick);
      animationFrames.add(frame);
    }
  };

  const frame = requestAnimationFrame(tick);
  animationFrames.add(frame);
}

watch(
  () => [props.items, props.mode],
  ([items, mode]) => {
    if (mode !== "metrics") {
      cancelAnimations();
      return;
    }

    cancelAnimations();
    displayedValues.value = items.map((item) => String(item.value ?? ""));

    items.forEach((item, index) => {
      const parsed = parseDisplayValue(item.value);
      if (!parsed) return;
      displayedValues.value[index] = formatAnimatedValue(0, parsed);
      const timer = window.setTimeout(() => {
        animationTimers.delete(timer);
        animateMetric(index, parsed);
      }, index * 90);
      animationTimers.add(timer);
    });
  },
  { deep: true, immediate: true }
);

onBeforeUnmount(cancelAnimations);
</script>
