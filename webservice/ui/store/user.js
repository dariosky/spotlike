export const state = () => ({
  id: null,
  name: null,
  authUrl: null,
  picture: null,
})

export const mutations = {
  login(state, user) {
    state.id = user.id
    state.name = user.name
    state.picture = user.picture
    state.authUrl = null
  },
  setAuthUrl(state, authUrl) {
    state.authUrl = authUrl
  },
}
