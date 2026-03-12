#!/usr/bin/env node

const http = require('http');
const readline = require('readline');
const URL_BASE = 'http://localhost:8082';
const SSE_URL = `${URL_BASE}/mcp`;
const AUTH_HEADER = 'Bearer bsk_WlZWYD2ZUE6Bs00I0d9iaf_NEReuHXBjAEXletJl2Pkp7IXZNCG7uYtfsdt7DUjH';

let postEndpoint = null;
let queue = [];

const sseOptions = {
  hostname: 'localhost',
  port: 8082,
  path: '/mcp',
  method: 'GET',
  headers: {
    'Authorization': AUTH_HEADER,
    'Accept': 'text/event-stream'
  }
};

const sseReq = http.request(sseOptions, (res) => {
  let buffer = '';
  res.on('data', (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep last partial line
    
    let currentEvent = 'message';
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      if (!line) continue;
      
      if (line.startsWith('event:')) {
        currentEvent = line.substring(6).trim();
      } else if (line.startsWith('data:')) {
        let data = line.substring(5).trim();
        if (currentEvent === 'endpoint') {
           postEndpoint = new URL(data, SSE_URL).href;
           // Flush queued messages
           while(queue.length > 0) {
             sendPost(queue.shift());
           }
        } else if (currentEvent === 'message') {
           process.stdout.write(data + '\n');
        }
        currentEvent = 'message'; // reset
      }
    }
  });
  
  res.on('end', () => {
    process.exit(1);
  });
});

sseReq.on('error', (err) => {
  // Silent fail
  process.exit(1);
});
sseReq.end();

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  if (!line.trim()) return;
  
  let jsonrpc;
  try {
    jsonrpc = JSON.parse(line);
  } catch (err) {
    return;
  }

  if (!postEndpoint) {
    queue.push(jsonrpc);
  } else {
    sendPost(jsonrpc);
  }
});

function sendPost(jsonrpc) {
  const url = new URL(postEndpoint);
  const options = {
    hostname: url.hostname,
    port: url.port,
    path: url.pathname + url.search,
    method: 'POST',
    headers: {
      'Authorization': AUTH_HEADER,
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream'
    }
  };

  const req = http.request(options, (res) => {
    let body = '';
    res.on('data', (chunk) => body += chunk);
    res.on('end', () => {
       if (res.statusCode >= 400) {
           // Silent
       } else {
           // Wait, does the server return JSON-RPC directly in the POST response?
           if (body.trim() && body.includes('jsonrpc')) {
               process.stdout.write(body.trim() + '\n');
           }
       }
    });
  });

  req.on('error', (err) => {
    // Silent
  });

  req.write(JSON.stringify(jsonrpc));
  req.end();
}
