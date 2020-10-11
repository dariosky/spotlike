export default async function ({ store, $axios, error }) {
  // If we don't know the user-status - let's get it
  if (!store.state.user.id) {
    // eslint-disable-next-line no-unused-vars
    const user = await $axios
      .$get('/user')
      .then((response) => {
        store.commit('user/login', response)
      })
      .catch((err) => {
        if (err.response && err.response.status === 401) {
          // not logged
          const authUrl = err.response.data.spotify_connect_url
          store.commit('user/setAuthUrl', authUrl)
          return
        }
        error('Cannot connect to the API')
      })
  }
}
