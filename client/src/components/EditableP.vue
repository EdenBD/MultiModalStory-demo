<template>
  <div>
    <p
      v-for="(value, index) in content"
      :id="`content-${index}`"
      :key="index"
      contenteditable
      @input="event => onInput(event, index)"
      @keyup.delete="onRemove(index)"
    />
  </div>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  data() {
    return {
      content: [
        { value: "paragraph 1" },
        { value: "paragraph 2" },
        { value: "paragraph 3" }
      ]
    };
  },
  mounted() {
    this.updateAllContent();
  },
  methods: {
    onInput(event, index) {
      const value = event.target.innerText;
      this.content[index].value = value;
    },
    onRemove(index) {
      if (this.content.length > 1 && this.content[index].value.length === 0) {
        this.$delete(this.content, index);
        this.updateAllContent();
      }
    },
    updateAllContent() {
      this.content.forEach((c, index) => {
        const el = document.getElementById(`content-${index}`);
        el.innerText = c.value;
      });
    }
  }
});
</script>
