const { CubejsServer } = require('@cubejs-backend/server');
const path = require('path');

// Add debug logging for environment variables
console.log('Environment variables:');
console.log('CUBEJS_DB_TYPE:', process.env.CUBEJS_DB_TYPE);
console.log('CUBEJS_DB_HOST:', process.env.CUBEJS_DB_HOST);
console.log('CUBEJS_DB_PORT:', process.env.CUBEJS_DB_PORT);
console.log('CUBEJS_DB_NAME:', process.env.CUBEJS_DB_NAME);
console.log('CUBEJS_DB_USER:', process.env.CUBEJS_DB_USER);
console.log('CUBEJS_DEV_MODE:', process.env.CUBEJS_DEV_MODE);
console.log('CUBEJS_API_SECRET:', process.env.CUBEJS_API_SECRET ? 'SET' : 'NOT SET');

// Check if configuration files exist
const fs = require('fs');
const configPath = path.join(__dirname, 'cube.js');
console.log('Config file exists at', configPath, ':', fs.existsSync(configPath));

const modelPath = path.join(__dirname, 'model');
console.log('Model directory exists at', modelPath, ':', fs.existsSync(modelPath));

// Load configuration
let config = {};
try {
  config = require('./cube.js');
  console.log('Configuration loaded successfully');
} catch (e) {
  console.error('Error loading configuration:', e);
}

// Store original console.log to capture token output
const originalConsoleLog = console.log;
let capturedToken = null;

console.log = function(...args) {
  // Capture JWT token when it's logged
  const message = args.join(' ');
  if (message.includes('🔒 Your temporary cube.js token:')) {
    capturedToken = message.split('token: ')[1];
    // Save token to a file for the test script
    try {
      require('fs').writeFileSync('/tmp/cube-jwt-token', capturedToken);
    } catch (e) {
      console.error('Could not save token to file:', e.message);
    }
  }
  originalConsoleLog.apply(console, args);
};

const server = new CubejsServer(config);

server.listen().then(({ version, port }) => {
  console.log(`🚀 Cube.js server (${version}) is listening on ${port}`);
  console.log('Development mode:', process.env.CUBEJS_DEV_MODE === 'true');
  console.log('API Secret configured:', !!process.env.CUBEJS_API_SECRET);
  
  // Additional debug info
  if (capturedToken) {
    console.log(`🎫 JWT Token captured and saved to /tmp/cube-jwt-token`);
  }
}).catch(e => {
  console.error('Fatal error during Cube.js startup: ');
  console.error(e.stack || e);
  process.exit(1);
});