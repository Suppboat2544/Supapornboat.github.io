const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8080;
const ROOT = path.join(__dirname, '..', 'docs');

function mimeType(file) {
  const ext = path.extname(file).toLowerCase();
  const map = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.json': 'application/json',
    '.txt': 'text/plain'
  };
  return map[ext] || 'application/octet-stream';
}

const server = http.createServer((req, res) => {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, urlPath);
  fs.promises.stat(filePath).then(stat => {
    if (stat.isDirectory()) {
      res.writeHead(301, { Location: req.url + '/' });
      res.end();
      return;
    }
    fs.createReadStream(filePath).on('error', () => {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not found');
    }).pipe(res);
  }).catch(() => {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not found');
  });
});

server.listen(PORT, () => {
  console.log(`Serving docs/ at http://localhost:${PORT}`);
});
