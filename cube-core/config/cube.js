const path = require('path');

module.exports = {
  schemaPath: path.join(__dirname, '../model'),
  
  // Add API secret back for development mode
  apiSecret: process.env.CUBEJS_API_SECRET || 'baubeach',
  
  contextToAppId: ({ securityContext }) => {
    return `CUBE_APP`;
  },
  
  contextToOrchestratorId: ({ securityContext }) => {
    return `CUBE_ORCHESTRATOR`;
  },

  driverFactory: ({ dataSource }) => {
    console.log('Creating driver for dataSource:', dataSource);
    console.log('DB Config:', {
      host: process.env.CUBEJS_DB_HOST,
      port: process.env.CUBEJS_DB_PORT,
      database: process.env.CUBEJS_DB_NAME,
      user: process.env.CUBEJS_DB_USER
    });
    
    return {
      type: 'mysql',
      host: process.env.CUBEJS_DB_HOST,
      port: process.env.CUBEJS_DB_PORT,
      database: process.env.CUBEJS_DB_NAME,
      user: process.env.CUBEJS_DB_USER,
      password: process.env.CUBEJS_DB_PASS,
    };
  },

  dbType: ({ dataSource }) => 'mysql',
  
  scheduledRefreshTimer: 30,
  
  preAggregationsSchema: 'pre_aggregations',

  // Logging configuration
  logger: (msg, params) => {
    console.log(`${new Date().toISOString()}: ${msg}`, params);
  },

  telemetry: false
};