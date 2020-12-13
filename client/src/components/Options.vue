<template>
  <v-card max-width="400" class="mx-auto" v-show="isOpen">
    <v-list>
      <v-list-item-group>
        <!--     Text Row     -->
        <v-list-item v-for="(text, index) in texts" :key="index" @click="$emit('text-insert', text)">
          <v-list-item-icon>
            <v-icon>mdi-star</v-icon>
          </v-list-item-icon>
          <v-list-item-title v-text="text"></v-list-item-title>
        </v-list-item>
        <!--     Images Row     -->
        <v-list-item>
        <v-list-item-icon>
          <v-icon>mdi-star</v-icon>
        </v-list-item-icon>
        <v-list-item-title v-for="(img, index) in imgs" :key="index" @click="$emit('img-insert', img)">
          <v-img :src="img"></v-img>
        </v-list-item-title>
        </v-list-item>
      <v-list-item-group>
    </v-list>
  </v-card>
</template>

<script lang="js">
export default {
  name: "Options",
  props: [
    isOpen: Boolean,
    texts: Array,
    imgs: Array],
};
</script>

