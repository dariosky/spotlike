<template>
  <div>
    <section>
      Connect your Spotify account to add several smart features around your
      listening habits and automate some of the boring tasks.
    </section>

    <section v-if="$store.state.user.authUrl">
      <a :href="$store.state.user.authUrl" class="button action">
        <img id="spotify-logo" src="@/assets/spotify.svg" alt="" />
        Log in with Spotify
      </a>
    </section>

    <section>
      <h2>Here is what it does</h2>
      <ul>
        <li>
          Syncs all of the songs you like to a playlist - so that you can share
          them with others.
        </li>

        <li>
          Looks for duplicates in your liked songs, and only keeps the oldest.
        </li>

        <li>
          Keeps track of what you listen and suggests you what you may like.
        </li>
      </ul>
    </section>

    <section>
      Hey, it's opensource - do you want to contribute? It's in Github:
      <a href="https://github.com/dariosky/spotlike" target="_blank"
        >https://github.com/dariosky/spotlike
      </a>
    </section>
  </div>
</template>

<script>
export default {
  name: 'AboutSpotlike',
}
</script>

<style scoped>
section {
  margin: 10px;
}

#spotify-logo {
  margin-right: 10px;
  width: 32px;
  height: 32px;
  vertical-align: middle;
}

.button {
  display: inline-block;
  padding: 10px 30px;
  text-decoration: none;
  border: 1px solid black;
  margin: 10px auto;
  font-size: 1.3em;
  border-radius: 6px;
}

.action {
  background-color: #3a833a;
  color: white;
}
</style>
