# GLM-5V Nexus Chat Web App

A modern, full-stack multi-modal AI chat application built with Vue 3, FastAPI, MySQL, and Zhipu AI's flagship GLM-4V-Plus (GLM-5 Vision) model.

## Features
- **Multi-modal Input**: Supports uploading local images or pasting online image URLs.
- **Fluid UI**: Dark-themed glassmorphism interface with smooth animations and typewriter streaming effects.
- **History Logs**: Persisted chat histories via MySQL with session switching and deletion.
- **Microservice Architecture**: Fully containerized backend and frontend separated via Docker Compose.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed on your host machine.
- A valid [Zhipu AI (Bigmodel.cn)](https://open.bigmodel.cn/) API Key.

## Quick Start

1. **Clone the repository**
   \`\`\`bash
   git clone <your-repo-url>
   cd <repo-folder>
   \`\`\`

2. **Configure API Key**
   Copy the example environment file:
   \`\`\`bash
   cp .env.example .env
   \`\`\`
   Edit `.env` and replace `your_zhipu_api_key_here` with your actual ZhipuAI API Key.

3. **Deploy with Docker**
   Run the following command at the root of the project to build and start all microservices (Frontend, Backend, and MySQL):
   \`\`\`bash
   docker-compose up -d --build
   \`\`\`

4. **Access the Application**
   - Frontend Web UI: [http://localhost:5173](http://localhost:5173)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

**Enjoy chatting with GLM-5V!**
