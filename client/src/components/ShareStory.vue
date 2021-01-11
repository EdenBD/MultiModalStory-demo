<template>
  <div>
    <v-row justify="space-around">
      <v-btn
        dark
        fab
        bottom
        color="blue darken-7"
        small
        :href="`https://www.linkedin.com/sharing/share-offsite/?url=${pageUrl}`"
        target="_blank"
      >
        <v-icon>mdi-linkedin</v-icon>
      </v-btn>
      <v-btn
        dark
        fab
        bottom
        color="blue"
        small
        :href="`https://twitter.com/intent/tweet?text=${pageUrl}`"
        target="_blank"
      >
        <v-icon>mdi-twitter</v-icon>
      </v-btn>
      <v-btn
        dark
        fab
        bottom
        color="blue"
        small
        :href="`https://www.facebook.com/sharer/sharer.php?u=${pageUrl}`"
        target="_blank"
      >
        <v-icon>mdi-facebook</v-icon>
      </v-btn>
      <v-btn
        dark
        fab
        bottom
        color="green"
        small
        :href="`https://wa.me/?text=Checkout%20this%20AI%20story...%20${pageUrl}`"
        target="_blank"
      >
        <v-icon>mdi-whatsapp</v-icon>
      </v-btn>
      <v-btn
        dark
        fab
        bottom
        color="tertiary"
        small
        :href="`mailto:?subject=fairytAIlor story generator!&amp;body=Checkout this generated story!<a href='${pageUrl}'>${pageUrl}</a>`"
        target="_blank"
      >
        <v-icon>mdi-email</v-icon>
      </v-btn>
    </v-row>
  </div>
</template>

<script lang="js">
// Modified from https://techformist.com/social-share-vuetify/
export default {
  name: "ShareStory",
  data() {
    return {
      pageUrl: window.location.href,
    }
  },
  watch: {
    $route() {
      // Change the current story-id in case of a route change.
      const lastSlash = window.location.href.lastIndexOf("/");
      const root = window.location.href.substring(0, lastSlash + 1);
      this.pageUrl = root + this.$route.params.storyid;
    }
  },
};
</script>

