const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '..', '.env');
const args = process.argv.slice(2);

if (!fs.existsSync(envPath)) {
  console.log('⚠️  .env file not found. Initializing...');

  let sourceFile = '.env.example';
  if (args.includes('development')) {
    sourceFile = '.env.development';
    console.log('🚀  Development mode detected.');
  } else {
    console.log('ℹ️  No specific mode detected. Using default (.env.example).');
  }

  const sourcePath = path.join(__dirname, '..', sourceFile);

  if (fs.existsSync(sourcePath)) {
    fs.copyFileSync(sourcePath, envPath);
    console.log(`✅  .env created successfully from ${sourceFile}!`);
  } else {
    console.error(`❌  Error: Source file ${sourceFile} not found.`);
    process.exit(1);
  }
} else {
  console.log('✅  .env already exists.');
}
