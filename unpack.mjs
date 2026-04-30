import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const archivePath = path.resolve('project.tar.gz.b64');

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function parseOctal(buf, start, len) {
  const raw = buf.subarray(start, start + len).toString('utf8').replace(/\0.*$/, '').trim();
  return raw ? parseInt(raw, 8) : 0;
}

function parseString(buf, start, len) {
  return buf.subarray(start, start + len).toString('utf8').replace(/\0.*$/, '');
}

function safeJoin(root, entryName) {
  const normalized = path.normalize(entryName).replace(/^(\.\.(\/|\\|$))+/, '');
  const target = path.resolve(root, normalized);
  if (!target.startsWith(root)) {
    throw new Error(`Unsafe tar path: ${entryName}`);
  }
  return target;
}

function unpackTar(tarBuffer, rootDir) {
  let offset = 0;

  while (offset + 512 <= tarBuffer.length) {
    const header = tarBuffer.subarray(offset, offset + 512);
    offset += 512;

    if (header.every((byte) => byte === 0)) break;

    const name = parseString(header, 0, 100);
    const prefix = parseString(header, 345, 155);
    const size = parseOctal(header, 124, 12);
    const typeFlag = parseString(header, 156, 1);
    const fullName = prefix ? `${prefix}/${name}` : name;

    const fileData = tarBuffer.subarray(offset, offset + size);
    offset += Math.ceil(size / 512) * 512;

    if (!fullName) continue;

    const target = safeJoin(rootDir, fullName);

    if (typeFlag === '5') {
      fs.mkdirSync(target, { recursive: true });
      continue;
    }

    ensureDir(target);
    fs.writeFileSync(target, fileData);
  }
}

if (!fs.existsSync(archivePath)) {
  console.log('[unpack] project.tar.gz.b64 not found; assuming project is already unpacked.');
  process.exit(0);
}

const root = process.cwd();
const b64 = fs.readFileSync(archivePath, 'utf8').replace(/\s+/g, '');
const tarGz = Buffer.from(b64, 'base64');
const tar = zlib.gunzipSync(tarGz);

unpackTar(tar, root);

console.log('[unpack] ddchat source restored.');
