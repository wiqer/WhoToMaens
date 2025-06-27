# BugAgaric User Guide

## Overview
BugAgaric is a powerful document management and search system that combines the capabilities of multiple services to provide efficient document processing, search, and chat functionality.

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Basic Usage](#basic-usage)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements
- Docker and Docker Compose
- Python 3.8+
- Go 1.21+
- PostgreSQL 13+
- Redis 6+
- MinIO
- Milvus 2.3+

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/bugagaric-bug.git
cd bugagaric-bug
```

2. Install dependencies:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Go dependencies
cd go-services
go mod download
```

3. Start services:
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose -f docker-compose.milvus.yml up -d
```

## Configuration

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
# Server
SERVER_PORT=8080

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=bugagaric

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=bugagaric

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Basic Usage

### Document Management
1. Upload a document:
```python
from bugagaric import DocumentManager

manager = DocumentManager()
doc_id = manager.upload_document("path/to/document.pdf")
```

2. Search documents:
```python
results = manager.search_documents("query text")
```

### Chat Interface
1. Create a chat session:
```python
from bugagaric import ChatManager

chat = ChatManager()
session_id = chat.create_session()
```

2. Send a message:
```python
response = chat.send_message(session_id, "Hello, how can I help you?")
```

## Advanced Features

### Knowledge Management
- Document indexing
- Vector search
- Semantic search
- Hybrid search

### Performance Optimization
- Cache management
- Query optimization
- Resource monitoring

## Troubleshooting

### Common Issues
1. Service Connection Issues
   - Check if all required services are running
   - Verify network connectivity
   - Check service logs

2. Performance Issues
   - Monitor resource usage
   - Check cache hit rates
   - Optimize query patterns

### Getting Help
- Check the [FAQ](FAQ.md)
- Submit an issue on GitHub
- Contact support

For more detailed information, please refer to the specific documentation sections. 