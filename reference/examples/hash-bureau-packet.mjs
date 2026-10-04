// Offline reference for the existing Bureau packet hash. Node.js 20+; no packages.
// Usage: node hash-bureau-packet.mjs < deliberately-public-packet.json
// Reads stdin, writes only the digest, and makes no network requests.
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

export function canonical(value) {
  if(typeof value==='number'&&!Number.isFinite(value))throw new Error('Non-finite JSON number');
  if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
  if(value!==null&&typeof value==='object')
    return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+canonical(value[key])).join(',')+'}';
  const encoded=JSON.stringify(value);
  if(encoded===undefined)throw new Error('JSON values only');
  return encoded;
}

export function packetHash(packet) {
  if(!packet||typeof packet!=='object'||Array.isArray(packet)||packet.schema!=='bureau.context-packet.v1')
    throw new Error('Expected an entire bureau.context-packet.v1 object');
  return createHash('sha256').update(canonical(packet),'utf8').digest('hex');
}

async function main() {
  const chunks=[];
  let size=0;
  for await(const chunk of process.stdin) {
    size+=chunk.length;
    if(size>16384)throw new Error('Input exceeds 16384 bytes');
    chunks.push(chunk);
  }
  const text=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(chunks));
  console.log(packetHash(JSON.parse(text)));
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)
  main().catch(()=>{console.error('Cannot hash: provide one bounded UTF-8 Context Packet with finite JSON numbers.');process.exitCode=1;});
