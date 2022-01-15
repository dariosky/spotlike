<template>
  <div v-if="user.id">
    <p>
      Connected as {{ user.name }}
      <img :src="userPicture" alt="" class="spotify-profile-pitcture" />
      the magic is happening.
    </p>

    <router-link v-if="$store.state.user.id" to="/logout"> Logout</router-link>
  </div>
</template>

<script>
import anonymousPicture from 'assets/anonymous-user.svg'

export default {
  name: 'Dashboard',
  computed: {
    user() {
      return this.$store.state.user
    },
    userPicture() {
      return this.$store.state.user.picture || anonymousPicture
    },
  },
}
</script>

<style scoped>
.spotify-profile-pitcture {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  vertical-align: middle;
}

a {
  font-weight: bold;
  color: #2c3e50 !important;
}
</style>
