#!/usr/bin/env node
import React, {useEffect, useState, useRef} from 'react';
import {render, Box, Text} from 'ink';
import TextInput from 'ink-text-input';
import Spinner from 'ink-spinner';
import {spawn} from 'node:child_process';

const App = () => {
  const [lines, setLines] = useState([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const procRef = useRef(null);

  useEffect(() => {
    // spawn python CLI
    const proc = spawn('nlbt', [], {stdio: ['pipe', 'pipe', 'pipe']});
    procRef.current = proc;

    const onData = chunk => setLines(prev => [...prev, ...chunk.toString().split(/\r?\n/)]);
    proc.stdout.on('data', onData);
    proc.stderr.on('data', onData);
    proc.on('close', () => setLines(prev => [...prev, '👋 nlbt exited']));

    return () => {
      try { proc.kill(); } catch {}
    };
  }, []);

  const onSubmit = (value) => {
    if (!procRef.current) return;
    setBusy(true);
    procRef.current.stdin.write(value + '\n');
    setInput('');
    setTimeout(() => setBusy(false), 100); // small debounce
  };

  return (
    <Box flexDirection="column">
      <Box marginBottom={1}><Text color="cyanBright">🧠 NLBT (Ink UI)</Text></Box>
      <Box flexDirection="column" height={20} overflowY="hidden">
        {lines.slice(-100).map((l, i) => (
          <Text key={i}>{l}</Text>
        ))}
      </Box>
      <Box marginTop={1}>
        <Text color="gray">💭 You: </Text>
        <TextInput
          value={input}
          onChange={setInput}
          onSubmit={onSubmit}
        />
        {busy && (
          <Box marginLeft={1}><Text color="yellow"><Spinner type="dots" /> Sending</Text></Box>
        )}
      </Box>
    </Box>
  );
};

render(<App />);

