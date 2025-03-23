# TreeTee: AI Agent Monitoring & Control Platform

![AI Agent at Work](https://media1.giphy.com/media/mTxnhJyiVYTUA/giphy_s.gif?cid=6c09b952snrxtrklyp25g9h06jz0y0qqw20l3neyh21hp41n&ep=v1_gifs_search&rid=giphy_s.gif&ct=g)

**The Universal Handshake Protocol: Bridging AI Agents, Virtual Machines, and Human Control**

TreeTee is a comprehensive platform that allows AI agents to use computers exactly as humans do, providing secure monitoring, tracing, and remote control capabilities for both virtual and physical machines.

## 🚀 Overview

TreeTee bridges the gap between AI agents and computer systems by creating a secure monitoring environment where:

- AI agents can control virtual and physical machines via VNC/RDP
- Humans can observe agent actions in real-time
- Users can take over control at any time with native mouse and keyboard
- All sessions run in secure, verified Trusted Execution Environments (TEEs)

![Human vs AI Control](https://i.imgur.com/s9sLMCU.jpg)

## 🔒 Security & Verification

TreeTee operates completely in the cloud with strong security guarantees:

- All components are containerized for consistent deployment
- Runs in verified TEEs (Trusted Execution Environments)
- Certificates for agent control are generated and signed within the original containers
- Access is limited to authorized accounts only
- [Verified by Phala Network TEE](https://cloud.phala.network/explorer/app_48dc0b7e647cbbfef16f2ae6cf2d5ca99d129402)

![Security Meme](https://i.imgur.com/xFzY1XE.jpg)

## 🧩 Core Components

### 1. TreeTee VNC Monitoring Tool and Agent Deployer
The central monitoring platform that allows you to:
- Deploy and manage AI agents
- Monitor agent activities in real-time
- Take over control when needed
- Grant selective access to capabilities

### 2. CUA-API/VM (Computer Use Agent)
The virtual machine and API used by AI agents to:
- Execute actions on virtual or physical machines
- Process LLM commands through the Python intermediary server
- Provide VNC/RDP access to the controlled machine
- Enable file sharing, terminal access, and messaging

![AI Agent Remote Control](https://i.imgur.com/gGm9kGD.jpg)

## 🔌 Integration with Open Source Tools

TreeTee leverages battle-tested open source technologies:

- **MeshCentral**: For secure remote device management
- **Goose**: For virtualization and machine control
- **Privy**: For secure authentication and identity management

## 🚪 Access Control & Sharing

TreeTee provides granular control over agent capabilities:
- Programmatically grant temporary access to specific agent capabilities
- Share or sell access to your agents with fine-grained permissions
- Control desktop viewing, interaction, file sharing, terminal access, and messaging

![Access Control](https://i.imgur.com/d8tU3fl.jpg)

## 🏁 Getting Started

### Quick Start with Docker

1. Deploy TreeTee monitoring platform:

```bash
# Clone the repository
git clone https://github.com/J-Palomino/trifecta.git
cd trifecta

# Launch using docker-compose
docker-compose up -d
```

2. Deploy the Computer Use Agent VM:

```bash
docker pull ghcr.io/j-palomino/openai-cua-sample-app:latest
docker run -d -p 3000:3000 ghcr.io/j-palomino/openai-cua-sample-app:latest
```

![Docker Meme](https://i.imgur.com/YuV5U8a.jpg)

### Configuration

1. Configure the `.env` file based on the `.env.example` provided
2. Set up authentication credentials for Privy integration
3. Configure MeshCentral for your specific deployment needs

## 🔧 Advanced Use Cases

- **Commercial Deployment**: Create AI agents that perform tasks on behalf of users
- **Development & Testing**: Create automated workflows for software testing
- **Customer Support**: Deploy agents that can assist users by demonstrating procedures
- **Training & Education**: Create AI tutors that can demonstrate computer skills

![AI Use Cases](https://i.imgur.com/lKL4alE.jpg)

## 🌐 Resources

- [GitHub Repository](https://github.com/J-Palomino/trifecta)
- [Phala TEE Verification](https://cloud.phala.network/explorer/app_48dc0b7e647cbbfef16f2ae6cf2d5ca99d129402)
- [Docker Hub - CUA Agent](https://hub.docker.com/r/ghcr.io/j-palomino/openai-cua-sample-app)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

![Contributing Meme](https://i.imgur.com/DHpz60d.jpg)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
