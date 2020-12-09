<template>
  <div>
    <p contenteditable="false" class="generated">{{extract}}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "Generated",
  props: {
    id: {
      type: String,
      default: null
    },
    extract: {
      type: String,
      default: "Blah"
    }
  }
});
</script>

