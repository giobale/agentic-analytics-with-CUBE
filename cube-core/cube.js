module.exports = {
  // Basic configuration - let CUBE handle the database connection via environment variables
  apiSecret: process.env.CUBEJS_API_SECRET || 'baubeach',
  
  // Logging
  logger: (msg, params) => {
    console.log(`${new Date().toISOString()}: ${msg}`, params);
  },

  telemetry: false
};