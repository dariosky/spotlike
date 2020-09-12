export const state = () => ({
  id: null,
  name: null,
  authUrl: null,
})

export const mutations = {
  login(state, user) {
    state.user = user
  },
  setAuthUrl(state, authUrl) {
    state.authUrl = authUrl
  },
}
