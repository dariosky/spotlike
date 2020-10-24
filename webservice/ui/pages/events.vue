<template>
  <div>
    <div v-if="!loading">
      <v-list two-line>
        <v-list-item v-for="item in items" :key="item.id" elevation="1" tile>
          <v-list-item-content>
            <v-list-item-title>{{ item.message }}</v-list-item-title>
            <v-list-item-subtitle>{{ item.date }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </div>
    <div v-else>
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    <div v-if="error">
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  async asyncData({ $axios, store }) {
    return await $axios
      .$get('/events')
      .then((response) => {
        return {
          loading: false,
          error: null,
          ...response,
        }
      })
      .catch((err) => {
        return {
          error: err.response.data,
          loading: false,
        }
      })
  },
  data() {
    return {
      loading: true,
      error: null,
      items: [],
    }
  },
  mounted() {
    if (!this.$store.state.user.id)
      setTimeout(() => this.$router.push('/'), 3000)
  },
}
</script>
