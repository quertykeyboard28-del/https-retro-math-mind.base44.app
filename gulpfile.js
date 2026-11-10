const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const { series } = require('gulp');

const execFileAsync = promisify(execFile);
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');

async function runPython(args) {
  const { stdout, stderr } = await execFileAsync(python, args, {
    cwd: __dirname,
    maxBuffer: 8 * 1024 * 1024,
  });
  if (stdout) process.stdout.write(stdout);
  if (stderr) process.stderr.write(stderr);
}

function compilePython() {
  return runPython(['-m', 'compileall', '-q', 'main.py', 'jcodepy_agent.py', 'kalkul8_decision.py']);
}

function runTests() {
  return runPython(['-m', 'pytest', '-q']);
}

exports.build = compilePython;
exports.test = series(compilePython, runTests);
exports.default = exports.build;
