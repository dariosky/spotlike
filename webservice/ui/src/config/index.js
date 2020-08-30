const ENV_URLS = {
  // in development use the python API in another port
  development: 'http://localhost:4000/',
}
const API_BASE = ENV_URLS[process.env.NODE_ENV] || '/'

const config = {
  GRAPHQL_ENDPOINT: API_BASE + 'graphql',
  APPLICATION_SERVER_KEY: 'BAtYqi2RowWBPHZfUUs0ypHfJ6lCpeiMCWVxUxd' +
    'Zuhap5rBj6m7ngRE7o2ADn_bqkCCF5WKJuvrTRqMCRDDffak',
  PUSH_SUBSCRIBE_ENDPOINT: API_BASE + 'push/subscribe',
  PUSH_UNSUBSCRIBE_ENDPOINT: API_BASE + 'push/unsubscribe',
}

export default config
