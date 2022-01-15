<template>
  <div v-if="$store.state.user.id" id="nav" fluid class="logobox">
    <router-link to="/">Home</router-link>

    <router-link to="/events"> Events </router-link>

    <router-link to="/recents"> Recents </router-link>

    <router-link to="/about"> About </router-link>
  </div>
</template>

<script>
export default {
  name: 'Navbar',
}
</script>

<style scoped>
#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
  margin: 0 10px;
}

#nav a.nuxt-link-exact-active {
  color: #42b983;
}
</style>
