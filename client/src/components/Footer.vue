<template>
  <div class="footer">
    <div class="footer-txt">Disclaimers</div>
    <div
      class="footer-txt"
    >By pressing the submit story button you provide all the information given in the form, and publish the existing story. All submitted stories are visible to anyone with the link. The feedbacks are anonymous and no specific user identification information is saved. The website uses Google Analytics, but no other cookies.</div>
    <div class="footer-txt">
      Stories are generated using a fine-tuned GPT-2 Medium model provided by
      <a
        href="https://huggingface.co"
      >huggingface</a>. The stories may contain inaccurate, inappropriate language. MIT and IBM make no warranties or guarantees, expressed or implied, assume no responsibility or liability of any kind and specifically disclaim all responsibility for any liability incurred as a direct or indirect result of using this website.
    </div>
    <div class="footer-txt">This site may be taken down at any point without further notice.</div>
    <div class="seperator"></div>
    <div class="footer-txt">
      Collaborative work of
      <a href="https://edenbd.dev/">Eden Bensaid</a>,
      <a href="https://www.mamartino.com/">Mauro Martino</a>,
      <a href="https://www.bhoov.com/">Benjamin Hoover</a>,
      <a href="https://www.mit.edu/~jda/">Jacob Andreas</a> and
      <a href="http://hendrik.strobelt.com/">Hendrik Strobelt</a>.

    </div>
    <div class="footer-txt">
      <strong>
        <a href="https://researcher.watson.ibm.com/researcher/view_group.php?id=5948">Visual AI Lab</a> @ IBM |
        <a href="https://lingo.csail.mit.edu/">Language & Intelligence</a> @ MIT
      </strong>
      - {{ new Date().getFullYear() }}
    </div>
  </div>
</template>

<script lang="js">
export default {
  name: "Footer"
};
</script>

