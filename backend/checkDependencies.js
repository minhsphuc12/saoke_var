const dependencies = require('./dependencies');
const { execSync } = require('child_process');

Object.entries(dependencies).forEach(([dep, version]) => {
  try {
    require(dep);
  } catch (error) {
    console.log(`Installing missing dependency: ${dep}@${version}`);
    execSync(`npm install ${dep}@${version}`);
  }
});

console.log('All dependencies are installed.');