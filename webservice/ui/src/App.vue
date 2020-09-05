<template>
  <div id="app">
    <img id="logo" alt="Spotlike" src="./assets/spotlike.svg">
    <div id="nav">
      <router-link to="/">Home</router-link>
      |
      <router-link to="/logout">Logout</router-link>
    </div>

    <div id="view">
      <div id="content">
        <router-view/>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  metaInfo: {
    title: 'Spotlike - automation tasks for your Spotify playlists',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    ],
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

#logo {
  width: 500px;
  max-height: 130px;
  max-width: 100%;
}

#view {
  text-align: center;
}

#content {
  margin: auto;
  max-width: 1200px;
  text-align: left;
}

</style>
