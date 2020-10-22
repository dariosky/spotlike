<template>
  <div>
    <div v-if="!loading">
      <p>You logged out from this browser.</p>
      <p>Spotlike will continue doing its magic to your account.</p>
    </div>
  </div>
</template>

<script>
export default {
  async asyncData({ $axios, store }) {
    return await $axios
      .$post('/logout')
      .then((response) => {
        store.commit('user/login', { id: null })
        return {
          loading: false,
          error: null,
        }
      })
      .catch((err) => {
        if (err.response && err.response.status === 401) {
          return { error: err.response.data }
        }
      })
  },
  data() {
    return {
      loading: true,
      error: null,
    }
  },
}
</script>
