<template>
  <div>
    <h1>
      Page Not Found
    </h1>

    <p>
      <router-link :to="{name:'home'}">
        Try to go back to the homepage
      </router-link>
    </p>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  metaInfo: {
    title: 'Spotlike - page not found',
  },
}
</script>
