<template>
  <div>
    <v-speed-dial v-model="dialShare" absolute left top direction="bottom" open-on-hover>
      <template v-slot:activator>
        <v-btn fab bottom small color="black" class="share-btn">
          <v-icon v-if="dialShare">mdi-close</v-icon>
          <v-icon v-else>mdi-share-variant</v-icon>
        </v-btn>
      </template>
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
        :href="`https://twitter.com/share?url=${pageUrl}`"
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
        :href="`mailto:?subject=fairytAIlor story generator!&amp;body=Checkout this AI Story!<a href='${pageUrl}'>${pageUrl}</a>`"
        target="_blank"
      >
        <v-icon>mdi-email</v-icon>
      </v-btn>
    </v-speed-dial>
  </div>
</template>

<script lang="js">
// Slightly Modified from https://techformist.com/social-share-vuetify/
export default {
  name: "ShareStory",
    data() {
    return {
      dialShare: false,
      pageUrl: window.location.href
    }
  }
};
</script>

