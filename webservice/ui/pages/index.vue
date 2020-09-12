<template>
  <div>
    <p>
      Connect your Spotify account to add some smart feature around your
      listening habits and automate some of the boring tasks.
    </p>

    <div v-if="$store.state.user.authUrl">
      <a :href="$store.state.user.authUrl"> Connect </a>
    </div>

    <h2>Here is what it does</h2>
    <ul>
      <li>
        Sync all the song you like to a playlist - so you can share it with
        others.
      </li>

      <li>
        Look for duplicates in your liked songs, and keep just the oldest.
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  head: {
    title: 'Automated tasks for your Spotify playlists',
  },
}
</script>
