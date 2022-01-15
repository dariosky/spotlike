<template>
  <div>
    <about-spotlike v-if="$store.state.user.authUrl" />
    <dashboard v-else />
  </div>
</template>

<script>
export default {
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  head: {
    title: 'Automated tasks for your Spotify playlists',
  },
}
</script>

<style scoped></style>
