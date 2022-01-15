<template>
  <v-app>
    <v-main id="app">
      <v-container fluid class="logobox">
        <router-link to="/">
          <img id="logo" alt="Spotlike" src="@/assets/spotlike.svg" />
        </router-link>
        <navbar />
      </v-container>

      <v-container class="view">
        <div class="content">
          <nuxt />
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<style>
.logobox {
  text-align: center;
}

#logo {
  width: 500px;
  max-height: 130px;
  max-width: 100%;
}

.view {
  text-align: center;
}

.content {
  margin: auto;
  max-width: 1200px;
  text-align: left;
}
</style>
