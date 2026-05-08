<template>
  <div class="data-table">
    <div class="table-shell">
      <table>
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key" :class="{ numeric: column.numeric }">
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in visibleRows" :key="`${page}-${index}`">
            <td v-for="column in columns" :key="column.key" :class="{ numeric: column.numeric }">
              {{ column.format ? column.format(row[column.key], row) : row[column.key] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="paginated && limitedRows.length" class="table-pagination">
      <span>{{ startRow }}-{{ endRow }} of {{ limitedRows.length }}</span>
      <div class="table-pagination__actions">
        <button type="button" title="Previous page" :disabled="page <= 1" @click="page -= 1">
          <ChevronLeft :size="15" />
        </button>
        <strong>{{ page }} / {{ pageCount }}</strong>
        <button type="button" title="Next page" :disabled="page >= pageCount" @click="page += 1">
          <ChevronRight :size="15" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight } from "lucide-vue-next";
import { computed, ref, watch } from "vue";

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  columns: {
    type: Array,
    default: () => [],
  },
  limit: {
    type: Number,
    default: 12,
  },
  paginated: {
    type: Boolean,
    default: false,
  },
  pageSize: {
    type: Number,
    default: 25,
  },
});

const page = ref(1);

const normalizedLimit = computed(() => Math.max(0, Number(props.limit) || 0));
const normalizedPageSize = computed(() => Math.max(1, Number(props.pageSize) || 25));
const limitedRows = computed(() => props.rows.slice(0, normalizedLimit.value));
const pageCount = computed(() =>
  props.paginated ? Math.max(1, Math.ceil(limitedRows.value.length / normalizedPageSize.value)) : 1
);
const visibleRows = computed(() => {
  if (!props.paginated) {
    return limitedRows.value;
  }

  const start = (page.value - 1) * normalizedPageSize.value;
  return limitedRows.value.slice(start, start + normalizedPageSize.value);
});
const startRow = computed(() => (limitedRows.value.length ? (page.value - 1) * normalizedPageSize.value + 1 : 0));
const endRow = computed(() => Math.min(page.value * normalizedPageSize.value, limitedRows.value.length));

watch(
  () => [props.rows, props.limit, props.pageSize, props.paginated],
  () => {
    page.value = 1;
  }
);

watch(pageCount, (count) => {
  if (page.value > count) {
    page.value = count;
  }
});
</script>
