<template>
  <v-app>
    <v-main id="app">
      <v-container fluid class="logobox">
        <router-link to="/">
          <img id="logo" alt="Spotlike" src="@/assets/spotlike.svg" />
        </router-link>
        <div id="nav">
          <router-link to="/">Home</router-link>

          <router-link v-if="$store.state.user.id" to="/events">
            Events
          </router-link>

          <router-link v-if="$store.state.user.id" to="/recents">
            Recent
          </router-link>

          <router-link v-if="$store.state.user.id" to="/logout">
            Logout
          </router-link>
        </div>
      </v-container>

      <v-container class="view">
        <div class="content">
          <nuxt />
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<style>
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

.logobox {
  text-align: center;
}

#logo {
  width: 500px;
  max-height: 130px;
  max-width: 100%;
}

.view {
  text-align: center;
}

.content {
  margin: auto;
  max-width: 1200px;
  text-align: left;
}
</style>
