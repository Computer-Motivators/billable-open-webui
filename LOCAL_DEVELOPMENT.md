# Local Development Guide

This guide will walk you through setting up a local development environment for the Open WebUI project on Linux. This guide assumes you're new to development tools like npm and Python environment management with conda.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installing Prerequisites](#installing-prerequisites)
4. [Project Setup](#project-setup)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Running the Development Servers](#running-the-development-servers)
8. [Accessing the Application](#accessing-the-application)
9. [Development Workflow](#development-workflow)
10. [Troubleshooting](#troubleshooting)
11. [Optional Configuration](#optional-configuration)

---

## Prerequisites

Before you begin, you'll need the following tools installed on your Linux system:

- **Node.js** (version 18.13.0 or higher, up to 22.x.x)
- **npm** (version 6.0.0 or higher) - usually comes with Node.js
- **Python** (version 3.11 or 3.12)
- **Conda** (Miniconda or Anaconda) - for managing Python environments
- **Git** (for cloning the repository, if needed)

---

## System Requirements

- **Operating System**: Linux (any modern distribution)
- **RAM**: At least 4GB (8GB recommended)
- **Disk Space**: At least 2GB free space
- **Internet Connection**: Required for downloading dependencies

---

## Installing Prerequisites

### Step 1: Check Current Versions

First, let's check what you already have installed:

```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check Python version
python3 --version

# Check pip version
pip3 --version

# Check Git version
git --version
```

### Step 2: Install Node.js and npm

If Node.js is not installed or your version is too old, install it using one of these methods:

#### Option A: Using NodeSource Repository (Recommended)

```bash
# For Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# For Fedora/RHEL
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs
```

#### Option B: Using Package Manager

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# For Fedora/RHEL
sudo dnf install nodejs npm

# For Arch Linux
sudo pacman -S nodejs npm
```

#### Option C: Using nvm (Node Version Manager) - Recommended for Developers

**This is the best option for Fedora users** as it allows easy version management and upgrades.

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload your shell configuration
source ~/.bashrc  # or ~/.zshrc if using zsh

# Install the latest Node.js 20 (this will install 20.18.1 or higher)
nvm install 20
nvm use 20
nvm alias default 20

# Or install the latest LTS version
nvm install --lts
nvm use --lts
nvm alias default lts/*
```

**Note for Fedora users**: If you already have Node.js installed via dnf, you may need to remove it first or ensure nvm's version takes precedence in your PATH.

After installation, verify:

```bash
node --version  # Should show v18.x.x, v20.x.x, or v22.x.x
npm --version   # Should show 6.x.x or higher
```

### Step 3: Install Python 3.11 or 3.12

Most Linux distributions come with Python 3, but you may need to install a specific version:

#### For Ubuntu/Debian:

```bash
# Add deadsnakes PPA for Python 3.11
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-dev python3-pip
```

#### For Fedora/RHEL:

```bash
sudo dnf install python3.11 python3.11-devel python3-pip
```

#### For Arch Linux:

```bash
sudo pacman -S python python-pip
```

Verify Python installation:

```bash
python3.11 --version  # Should show Python 3.11.x or 3.12.x
pip3 --version
```

### Step 4: Install Conda

Conda is a package and environment manager for Python. You can install either Miniconda (minimal) or Anaconda (full distribution).

#### Option A: Install Miniconda (Recommended)

```bash
# Download Miniconda installer
cd /tmp
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Run the installer
bash Miniconda3-latest-Linux-x86_64.sh

# Follow the prompts (accept license, choose installation location)
# When asked, say "yes" to initialize conda

# Reload your shell configuration
source ~/.bashrc  # or ~/.zshrc if using zsh
```

#### Option B: Install Anaconda

```bash
# Download Anaconda installer
cd /tmp
wget https://repo.anaconda.com/archive/Anaconda3-latest-Linux-x86_64.sh

# Run the installer
bash Anaconda3-latest-Linux-x86_64.sh

# Follow the prompts and reload your shell
source ~/.bashrc
```

Verify conda installation:

```bash
conda --version  # Should show conda version
conda info       # Shows conda environment info
```

### Step 5: Install Git (if not already installed)

```bash
# Ubuntu/Debian
sudo apt install git

# Fedora/RHEL
sudo dnf install git

# Arch Linux
sudo pacman -S git
```

---

## Project Setup

### Step 1: Navigate to Project Directory

```bash
# Navigate to your project directory
cd /path/to/your/project
```

Or if you need to clone the repository:

```bash
git clone <repository-url>
cd billable-open-webui
```

### Step 2: Verify Project Structure

You should see the following key directories:

- `backend/` - Python backend code
- `src/` - Frontend Svelte code
- `package.json` - Node.js dependencies
- `requirements.txt` - Python dependencies

---

## Backend Setup

### Step 1: Create Conda Environment

A conda environment isolates your project's Python packages from system packages. This is a best practice.

```bash
# Navigate to the project root directory
cd /path/to/your/project

# Create a conda environment with Python 3.11 or 3.12
conda create -n open-webui python=3.11 -y

# Or for Python 3.12:
# conda create -n open-webui python=3.12 -y
```

### Step 2: Activate the Conda Environment

```bash
# Activate the conda environment
conda activate open-webui
```

You should see `(open-webui)` at the beginning of your terminal prompt, indicating the conda environment is active.

**Important**: You must activate the conda environment every time you open a new terminal to work on the backend.

### Step 3: Upgrade pip

```bash
# Upgrade pip to the latest version
pip install --upgrade pip
```

### Step 4: Install Python Dependencies

```bash
# Navigate to the backend directory
cd backend

# Install all required Python packages
pip install -r requirements.txt

# Return to project root
cd ..
```

This will take several minutes as it downloads and installs many packages. You'll see progress output in your terminal.

**Note**: If you encounter errors during installation, you may need to install system-level dependencies. Common ones include:

```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev libssl-dev libffi-dev

# Fedora/RHEL
sudo dnf install gcc python3-devel openssl-devel libffi-devel
```

### Step 5: Install python-dotenv (if not included)

The project uses `.env` files for configuration. Install dotenv if needed:

```bash
pip install python-dotenv
```

### Step 5: Install the Project in Editable Mode

**This is critical!** You need to install the `open_webui` package itself so Python can find it when running the server.

```bash
# Make sure you're in the project root with conda environment activated
# Install the project in editable mode
# This makes the open_webui package importable without copying files
pip install -e .
```

**What does `-e` mean?**: The `-e` flag stands for "editable" mode. It installs the package in a way that links directly to your source code, so changes you make are immediately available without reinstalling.

### Step 6: Create Backend Data Directory

```bash
# Create the data directory if it doesn't exist
cd backend
mkdir -p data

# Return to project root
cd ..
```

---

## Frontend Setup

### Step 1: Navigate to Project Root

```bash
# Make sure you're in the project root directory
cd /path/to/your/project
```

### Step 2: Install Node.js Dependencies

```bash
# Install all npm packages (this may take a few minutes)
npm install
```

This command reads `package.json` and downloads all required JavaScript/TypeScript packages into a `node_modules/` directory.

**What is npm?**: npm (Node Package Manager) is the package manager for Node.js. It's similar to `pip` for Python or `apt` for Ubuntu.

### Step 3: Verify Installation

```bash
# Check that node_modules directory was created
ls -la node_modules | head -20

# You should see many directories here
```

---

## Running the Development Servers

The project requires **two separate servers** to run simultaneously:
1. **Backend server** (Python/FastAPI) - handles API requests
2. **Frontend server** (Node.js/Vite) - serves the web interface

You'll need **two terminal windows** open.

### Terminal 1: Start the Backend Server

```bash
# Navigate to project root
cd /path/to/your/project

# Activate the conda environment (IMPORTANT!)
conda activate open-webui

# Run the backend development server
bash backend/dev.sh
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
```

The backend is now running on **http://localhost:8080**

**Keep this terminal open!** The server will automatically reload when you make changes to backend code.

### Terminal 2: Start the Frontend Server

Open a **new terminal window** and run:

```bash
# Navigate to project root
cd /path/to/your/project

# Start the frontend development server
npm run dev
```

You should see output like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

The frontend is now running on **http://localhost:5173**

**Keep this terminal open too!** The frontend will automatically reload when you make changes to frontend code.

---

## Accessing the Application

1. Open your web browser
2. Navigate to: **http://localhost:5173**
3. You should see the Open WebUI interface

The frontend (port 5173) automatically communicates with the backend (port 8080) through Vite's proxy configuration.

---

## Development Workflow

### Making Changes

- **Frontend changes**: Edit files in `src/` directory. Changes will automatically reload in the browser.
- **Backend changes**: Edit files in `backend/open_webui/` directory. The uvicorn server will automatically reload.

### Stopping the Servers

- **Backend**: In Terminal 1, press `Ctrl+C`
- **Frontend**: In Terminal 2, press `Ctrl+C`

### Restarting After Closing Terminals

If you close your terminals, you'll need to restart both servers:

1. **Backend**: 
   ```bash
   cd /path/to/your/project
   conda activate open-webui
   bash backend/dev.sh
   ```

2. **Frontend**:
   ```bash
   cd /path/to/your/project
   npm run dev
   ```

---

## Troubleshooting

### Problem: "command not found: node" or "command not found: npm"

**Solution**: Node.js is not installed or not in your PATH. Follow the [Installing Prerequisites](#installing-prerequisites) section to install Node.js.

### Problem: "command not found: python3.11"

**Solution**: 
- Try `python3` instead of `python3.11`
- Or install Python 3.11 following the [Installing Prerequisites](#installing-prerequisites) section

### Problem: "EACCES: permission denied" when running npm install

**Solution**: Don't use `sudo` with npm. If you need to fix permissions:

```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Problem: Backend server won't start - "ModuleNotFoundError: No module named 'open_webui'"

**Error message example**:
```
ModuleNotFoundError: No module named 'open_webui'
```

**Solution**: The `open_webui` package isn't installed or Python can't find it. Follow these steps:

1. **Make sure you're using the correct conda environment**:
   ```bash
   # Activate the conda environment (you should see (open-webui) in prompt)
   conda activate open-webui
   ```

2. **Install the project in editable mode** (this is the most common fix):
   ```bash
   # Make sure you're in project root
   cd /path/to/your/project
   
   # Install the project in editable mode
   pip install -e .
   
   # Verify it's installed
   python -c "import open_webui; print('open_webui found!')"
   ```

3. **If that doesn't work, check your Python path**:
   ```bash
   # Make sure you're in project root with conda environment activated
   python -c "import sys; print('\n'.join(sys.path))"
   # You should see the backend directory or site-packages with open_webui
   ```

4. **Alternative: Set PYTHONPATH manually** (if editable install doesn't work):
   ```bash
   # From project root, export PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
   
   # Then try running the server again
   bash backend/dev.sh
   ```

5. **If you're using a different conda environment**, make sure it's the correct one:
   ```bash
   # Deactivate current environment if any
   conda deactivate
   
   # Activate the correct one
   conda activate open-webui
   pip install -e .
   ```

**Root cause**: The `open_webui` package needs to be installed so Python can import it. Installing with `pip install -e .` from the project root makes it available in editable mode.

### Problem: Backend server won't start - Other "ModuleNotFoundError"

**Solution**: 
1. Make sure the conda environment is activated (you should see `(open-webui)` in your prompt)
2. Reinstall dependencies:
   ```bash
   cd backend
   conda activate open-webui
   pip install -r requirements.txt
   cd ..
   ```

### Problem: Frontend shows "Cannot connect to backend" or CORS errors

**Solution**: 
1. Make sure the backend server is running on port 8080
2. Check that `CORS_ALLOW_ORIGIN` in `backend/dev.sh` includes `http://localhost:5173`
3. Verify both servers are running

### Problem: Port 8080 or 5173 is already in use

**Solution**: 
- Find what's using the port:
  ```bash
  # For port 8080
  sudo lsof -i :8080
  # or
  sudo netstat -tulpn | grep 8080
  
  # For port 5173
  sudo lsof -i :5173
  ```
- Kill the process or use a different port:
  - Backend: Edit `backend/dev.sh` and change `PORT=8080` to another port
  - Frontend: Use `npm run dev:5050` to run on port 5050, or edit `vite.config.ts`

### Problem: "npm install" fails with network errors

**Solution**:
- Check your internet connection
- Clear npm cache: `npm cache clean --force`
- Try using a different registry: `npm config set registry https://registry.npmjs.org/`

### Problem: "npm install" fails with ERESOLVE dependency conflicts

**Error message example**:
```
npm error ERESOLVE could not resolve
npm error peer @tiptap/core@"^2.7.0" from @tiptap/extension-bubble-menu@2.26.1
```

**Solution**: This happens when package versions are mismatched. The project has been updated to fix this, but if you encounter it:

1. **First, try updating package.json** (if the fix hasn't been applied yet):
   - The issue is usually that some `@tiptap` packages are on version 2.x while others are on 3.x
   - Check `package.json` and ensure all `@tiptap` packages use compatible versions (all should be 3.x)

2. **If the package.json is already fixed, try these steps**:
   ```bash
   # Remove node_modules and package-lock.json
   rm -rf node_modules package-lock.json
   
   # Clear npm cache
   npm cache clean --force
   
   # Try installing again
   npm install
   ```

3. **If it still fails, use legacy peer deps** (workaround):
   ```bash
   npm install --legacy-peer-deps
   ```
   
   **Note**: This bypasses peer dependency checks. The project should work, but you may see warnings.

4. **Alternative: Use --force flag** (not recommended unless necessary):
   ```bash
   npm install --force
   ```

**Root cause**: This typically happens when dependencies have conflicting version requirements. The project maintainers should keep all related packages (like all `@tiptap` packages) on compatible versions.

### Problem: "npm install" fails with EBADENGINE - Node.js version too old

**Error message example**:
```
npm error engine Unsupported engine
npm error engine Not compatible with your version of node/npm: undici@7.16.0
npm error notsup Required: {"node":">=20.18.1"}
npm error notsup Actual:   {"npm":"10.8.2","node":"v20.17.0"}
```

**Solution**: Your Node.js version is too old. Some dependencies require Node.js >= 20.18.1, but you have an older version.

#### For Fedora Users:

**Option 1: Upgrade using nvm (Recommended)**

If you don't have nvm installed:
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload your shell
source ~/.bashrc  # or ~/.zshrc if using zsh

# Install latest Node.js 20 (will be >= 20.18.1)
nvm install 20
nvm use 20
nvm alias default 20

# Verify the version
node --version  # Should show v20.18.1 or higher
```

If you already have nvm:
```bash
# Install/upgrade to latest Node.js 20
nvm install 20
nvm use 20

# Verify
node --version
```

**Option 2: Upgrade using NodeSource Repository**

```bash
# Remove old Node.js (if installed via dnf)
sudo dnf remove nodejs npm

# Add NodeSource repository for latest Node.js 20
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

# Install/upgrade Node.js
sudo dnf install -y nodejs

# Verify
node --version  # Should show v20.18.1 or higher
```

**Option 3: Upgrade using Fedora's default repositories**

```bash
# Update system packages
sudo dnf update

# Check available Node.js versions
dnf list available nodejs

# If a newer version is available, upgrade
sudo dnf upgrade nodejs npm

# Verify
node --version
```

**Important**: After upgrading Node.js, you may need to:
1. Remove `node_modules` and `package-lock.json`:
   ```bash
   rm -rf node_modules package-lock.json
   ```
2. Clear npm cache:
   ```bash
   npm cache clean --force
   ```
3. Reinstall dependencies:
   ```bash
   npm install
   ```

### Problem: Python package installation fails (compilation errors)

**Solution**: Install build tools:
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc python3-devel
```

### Problem: Database migration errors

**Solution**: The database will be created automatically on first run. If you see migration errors:
```bash
conda activate open-webui
python -m open_webui.config
```

---

## Optional Configuration

### Environment Variables

You can create a `.env` file in the project root for custom configuration:

```bash
# Create .env file
touch .env
```

Add any of these variables (all are optional for basic development):

```bash
# .env file example
ENV=dev
DATABASE_URL=sqlite:///./backend/data/webui.db
WEBUI_SECRET_KEY=your-secret-key-here
OLLAMA_BASE_URL=http://localhost:11434
CORS_ALLOW_ORIGIN=http://localhost:5173;http://localhost:8080
```

### Using a Different Backend Port

Edit `backend/dev.sh`:

```bash
PORT=9000  # Change from 8080 to 9000
```

Then update your frontend proxy configuration if needed.

### Using a Different Frontend Port

```bash
# Run on port 5050
npm run dev:5050

# Or edit package.json to change the default port
```

### Database Options

By default, the project uses SQLite (no setup required). For PostgreSQL:

1. Install PostgreSQL:
   ```bash
   sudo apt install postgresql postgresql-contrib  # Ubuntu/Debian
   sudo dnf install postgresql postgresql-server   # Fedora/RHEL
   ```

2. Create database and user
3. Set `DATABASE_URL` in `.env` file

---

## Quick Reference Commands

```bash
# Activate conda environment
conda activate open-webui

# Start backend (from project root with conda environment activated)
bash backend/dev.sh

# Start frontend (from project root)
npm run dev

# Install new Python package (with conda environment activated)
pip install <package-name>

# Or use conda if available
conda install <package-name>

# Install new npm package
npm install <package-name>

# Update Python dependencies
conda activate open-webui
cd backend
pip install --upgrade -r requirements.txt
cd ..

# Update npm dependencies
npm update

# Deactivate conda environment when done
conda deactivate
```

---

## Next Steps

- Read the main [README.md](./README.md) for project overview
- Check [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for contribution guidelines
- Explore the codebase:
  - Frontend: `src/lib/components/`
  - Backend: `backend/open_webui/routers/`
- Join the community for support and questions

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) file
2. Review error messages carefully - they often contain helpful information
3. Check that all prerequisites are installed correctly
4. Verify both servers are running and accessible
5. Look at server logs in both terminal windows for error details

Happy coding! 🚀

