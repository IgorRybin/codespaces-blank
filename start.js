import { execSync, spawn } from "child_process";
import fs from "fs";
import https from "https";

console.log("=== Starting Kanban Python App Launcher ===");

// Create or clean startup.log
const logStream = fs.createWriteStream("startup.log", { flags: "w" });

function log(msg) {
  console.log(msg);
  logStream.write(msg + "\n");
}

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        // Follow redirect
        downloadFile(response.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }
      response.pipe(file);
      file.on("finish", () => {
        file.close();
        resolve();
      });
    }).on("error", (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

// Diagnostics
log("--- Environment Diagnostics ---");
log(`process.env.PATH: ${process.env.PATH}`);
log(`process.cwd(): ${process.cwd()}`);

function runCmdAsync(cmd, args) {
  return new Promise((resolve, reject) => {
    log(`Spawning async: ${cmd} ${args.join(" ")}`);
    const proc = spawn(cmd, args);
    proc.stdout.on("data", (data) => {
      process.stdout.write(data);
      logStream.write(data);
    });
    proc.stderr.on("data", (data) => {
      process.stderr.write(data);
      logStream.write(data);
    });
    proc.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command ${cmd} exited with code ${code}`));
      }
    });
  });
}

// Attempt to check if pip is installed, if not bootstrap it
let hasPip = false;
try {
  execSync("python3 -m pip --version");
  hasPip = true;
  log("Pip is already present in python3.");
} catch (err) {
  log("Pip is not present. Bootstrapping...");
}

if (!hasPip) {
  try {
    log("Downloading get-pip.py...");
    await downloadFile("https://bootstrap.pypa.io/get-pip.py", "get-pip.py");
    log("get-pip.py downloaded successfully. Executing tool (async spawn)...");
    await runCmdAsync("python3", ["get-pip.py", "--user"]);
    log("get-pip.py completed successfully!");
  } catch (bootstrapErr) {
    log(`Failed to bootstrap pip with get-pip.py: ${bootstrapErr.message}`);
  }
}

// Check where custom user py binaries might live and append to PATH
const homeDir = process.env.HOME || "/root";
const userBinPath = `${homeDir}/.local/bin`;
process.env.PATH = `${userBinPath}:${process.env.PATH}`;
log(`Updated process.env.PATH: ${process.env.PATH}`);

// Try commands and catch results
const checkCmds = ["python3", "python", "pip3", "pip", "virtualenv", "uvicorn"];
checkCmds.forEach(cmd => {
  try {
    const out = execSync(`which ${cmd}`).toString().trim();
    log(`'which ${cmd}': ${out}`);
    try {
      const ver = execSync(`${cmd} --version`).toString().trim().replace(/\n/g, " ");
      log(`'${cmd} --version': ${ver}`);
    } catch (e) {
      log(`'${cmd} --version' failed: ${e.message}`);
    }
  } catch (err) {
    log(`'which ${cmd}' failed: not in PATH`);
  }
});
log("--------------------------------");

// 1. Detect python command
let pythonCmd = "python3";
try {
  execSync("python3 --version");
} catch (e) {
  try {
    execSync("python --version");
    pythonCmd = "python";
  } catch (err) {
    const errMsg = "Error: Python 3 was not found in the environment paths. Please install Python 3.";
    console.error(errMsg);
    logStream.write(errMsg + "\n");
    process.exit(1);
  }
}
log(`Using python executable: ${pythonCmd}`);

// 2. Install requirements
log("Installing python dependencies from requirements.txt...");
try {
  try {
    await runCmdAsync(pythonCmd, ["-m", "pip", "install", "-r", "requirements.txt"]);
  } catch (pipErr) {
    log(`Normal pip install failed, trying with --user... Error: ${pipErr.message}`);
    await runCmdAsync(pythonCmd, ["-m", "pip", "install", "--user", "-r", "requirements.txt"]);
  }
  log("Python dependencies installed successfully!");
} catch (err) {
  log(`Warning: pip install procedure completed with exceptions: ${err.message}`);
}

// 3. Launch App
log("Starting Uvicorn FastAPI server on 0.0.0.0:3000...");
const uvicornProcess = spawn(pythonCmd, ["-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]);

uvicornProcess.stdout.on("data", (data) => {
  process.stdout.write(data);
  logStream.write(data);
});

uvicornProcess.stderr.on("data", (data) => {
  process.stderr.write(data);
  logStream.write(data);
});

uvicornProcess.on("close", (code) => {
  log(`FastAPI server exited with code ${code}`);
  process.exit(code);
});

process.on("SIGTERM", () => {
  uvicornProcess.kill("SIGTERM");
  process.exit(0);
});

process.on("SIGINT", () => {
  uvicornProcess.kill("SIGINT");
  process.exit(0);
});
