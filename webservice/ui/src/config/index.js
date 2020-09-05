const ENV_URLS = {
  // in development use the python API in another port
  development: 'http://localhost:4000/',
}
const API_BASE = ENV_URLS[process.env.NODE_ENV] || '/'

const config = {
  urls: {
    currentUser: API_BASE + 'graphql',
  },
}

export default config
