const { spawn } = require('child_process');

const process = spawn('node', ['node_modules/meshcentral'], {
  stdio: 'inherit'
});

process.on('close', (code) => {
  console.log(`MeshCentral process exited with code ${code}`);
});

//this will run with node and needs to echo the command node node_modules/meshcentral
console.log('Starting MeshCentral server...');




// Log a message to indicate the server is running
console.log('MeshCentral server is running.'); 