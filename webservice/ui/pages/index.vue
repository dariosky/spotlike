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
    title: 'Home',
  },
}
</script>

<style scoped></style>
