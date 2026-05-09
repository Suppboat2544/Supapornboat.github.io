const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, '..', 'docs');
(async () => {
  try {
    if (fs.existsSync(OUT)) {
      await fs.promises.rm(OUT, { recursive: true, force: true });
      console.log('Removed docs/');
    } else {
      console.log('No docs/ to remove');
    }
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
})();
