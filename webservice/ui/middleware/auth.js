export default async function ({ store, $axios, error }) {
  // If we don't know the user-status - let's get it
  if (!store.state.user.id) {
    // eslint-disable-next-line no-unused-vars
    const user = await $axios
      .$get('http://localhost:4000/api/user')
      .catch((err) => {
        try {
          if (err.response.status === 401) {
            // not logged
            const authUrl = err.response.data.spotify_connect_url
            store.commit('user/setAuthUrl', authUrl)
            return
          }
        } catch (e) {}
        error('Cannot connect to the API')
      })
  }
}
