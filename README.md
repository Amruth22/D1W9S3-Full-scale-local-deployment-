# Library Book Reservation System - Full-scale Local Deployment

A complete library book reservation system demonstrating full-scale local deployment, multi-environment simulation, performance excellence, and SLA monitoring.

## 🎯 System Overview

This system showcases:
- **Full-scale Local Deployment** without containers
- **Multi-environment Simulation** via configuration files
- **Performance Excellence** with caching and connection pooling
- **SLA Monitoring** with automated reporting

## 🏗️ Architecture

```
[Users] → [Reverse Proxy :8000] → [API Server :8080] ← [Background Workers]
                                → [API Server :8081] ← [Background Workers]
                                        ↓
                                [SQLite + Connection Pool]
                                        ↓
                                [LRU Cache + SLA Monitoring]
```

## ✨ Key Features

### 🚀 **Full-scale Local Deployment**
- **Main API Server**: Port 8000 (reverse proxy entry point)
- **Load Balanced APIs**: Ports 8080 and 8081
- **Background Workers**: Multiprocessing/threading for reservation processing
- **SQLite Database**: Connection pooling (min=2, max=10)
- **Simple Python Reverse Proxy**: Distributes requests between API instances

### 🔧 **Multi-environment Simulation**
- **Dev**: 1 worker thread, instant processing, verbose logging
- **Staging**: 2 worker threads, 1-second delays, normal logging
- **Production**: 4 worker threads, realistic delays, minimal logging
- **Config-based**: JSON configuration files for each environment

### ⚡ **Performance Excellence**
- **LRU Cache**: Size=1000 for book availability data
- **Connection Pool**: min=2, max=10 connections
- **Batch Processing**: Process reservations every 5 seconds
- **Concurrency Target**: Handle 500 concurrent users

### 📊 **SLA Monitoring**
- **Reservation Processing**: 95% < 2 seconds
- **System Availability**: 99% uptime during business hours
- **Queue Depth**: < 50 pending reservations
- **Automated Reporting**: SLA reports every 30 minutes to `sla_report.txt`

## 🚀 Quick Start

### 1. Setup
```bash
git clone https://github.com/Amruth22/D1W9S3-Full-scale-local-deployment-.git
cd D1W9S3-Full-scale-local-deployment-
pip install -r requirements.txt
```

### 2. Choose Environment
```bash
# Development (default)
export ENVIRONMENT=dev

# Staging
export ENVIRONMENT=staging

# Production
export ENVIRONMENT=prod
```

### 3. Start Complete System
```bash
python start_system.py
```

This starts:
- API Server on port 8080
- API Server on port 8081  
- Reverse Proxy on port 8000 (main entry point)

### 4. Access the System
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **SLA Monitoring**: http://localhost:8000/sla
- **System Metrics**: http://localhost:8000/metrics

### 5. Run Tests
```bash
python unit_test.py
```

## 📊 API Endpoints

### **Books**
```http
GET  /books              # List all books
GET  /books/{isbn}       # Get specific book (cached)
POST /books              # Add new book
```

### **Users**
```http
POST /users              # Create library user
GET  /users/{user_id}    # Get user information
```

### **Reservations**
```http
POST /reservations           # Create reservation (queued)
GET  /reservations/my/{id}   # Get user's reservations
```

### **Monitoring**
```http
GET /sla                 # SLA compliance status
GET /metrics             # System performance metrics
GET /health              # Health check
```

## 🔧 Environment Configuration

### **Development** (`config_dev.json`)
```json
{
  "environment": "dev",
  "worker_threads": 1,
  "processing_delay": 0,
  "log_level": "DEBUG",
  "cache_size": 500,
  "batch_interval": 2,
  "sla_report_interval": 5
}
```

### **Staging** (`config_staging.json`)
```json
{
  "environment": "staging", 
  "worker_threads": 2,
  "processing_delay": 1,
  "log_level": "INFO",
  "cache_size": 1000,
  "batch_interval": 5,
  "sla_report_interval": 15
}
```

### **Production** (`config_prod.json`)
```json
{
  "environment": "prod",
  "worker_threads": 4,
  "processing_delay": 0.5,
  "log_level": "WARNING", 
  "cache_size": 2000,
  "batch_interval": 5,
  "sla_report_interval": 30
}
```

## 📈 SLA Monitoring

### **SLA Targets**
1. **Reservation Processing**: 95% of reservations processed in < 2 seconds
2. **System Availability**: 99% uptime during business hours
3. **Queue Depth**: < 50 pending reservations at any time

### **SLA Reports**
Automated reports generated every 30 minutes in `sla_report.txt`:

```
SLA Report - 2024-01-15 14:30:00
Environment: prod
=====================================

Reservation Processing SLA (Target: 95% < 2 seconds):
- 95th Percentile: 1.234 seconds
- Average Time: 0.856 seconds
- Total Processed: 1,247
- SLA Met: YES

System Availability SLA (Target: 99% uptime):
- Current Uptime: 99.8%
- SLA Met: YES

Queue Depth SLA (Target: < 50 pending):
- Current Queue: 12
- SLA Met: YES
```

## 🔍 Performance Features

### **LRU Cache**
- **Capacity**: 1000-2000 items (environment dependent)
- **Cache Strategy**: Book availability data
- **Hit Rate Monitoring**: Track cache effectiveness
- **Automatic Invalidation**: Clear cache on data updates

### **Connection Pool**
- **Pool Size**: 2-10 connections (min-max)
- **Thread-safe**: Concurrent access handling
- **Resource Management**: Automatic connection lifecycle
- **Performance**: Reduced connection overhead

### **Batch Processing**
- **Queue Management**: In-memory reservation queue
- **Batch Interval**: Process every 5 seconds
- **Worker Threads**: 1-4 threads (environment dependent)
- **SLA Tracking**: Monitor processing times

## 🚀 Deployment Guide

### **Single API Instance** (Development)
```bash
export ENVIRONMENT=dev
python main.py
```

### **Full-scale Deployment** (Production)
```bash
export ENVIRONMENT=prod
python start_system.py
```

### **Manual Multi-instance**
```bash
# Terminal 1: API Server 1
export PORT=8080 && export ENVIRONMENT=prod && python main.py

# Terminal 2: API Server 2  
export PORT=8081 && export ENVIRONMENT=prod && python main.py

# Terminal 3: Reverse Proxy
python reverse_proxy.py
```

## 📊 Usage Examples

### **1. Create Library User**
```bash
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "STU001",
       "name": "John Student",
       "email": "john@university.edu",
       "membership_type": "student"
     }'
```

### **2. Browse Books**
```bash
# All books
curl "http://localhost:8000/books"

# Books by category
curl "http://localhost:8000/books?category=Programming"

# Specific book (cached)
curl "http://localhost:8000/books/978-0134685991"
```

### **3. Make Reservation**
```bash
curl -X POST "http://localhost:8000/reservations" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "STU001",
       "isbn": "978-0134685991"
     }'
```

### **4. Monitor System**
```bash
# SLA compliance
curl "http://localhost:8000/sla"

# System metrics
curl "http://localhost:8000/metrics"

# Health check
curl "http://localhost:8000/health"
```

## 🧪 Testing

### **Run All Tests**
```bash
python unit_test.py
```

### **Test Categories**
- **Environment Configuration**: Config file validation
- **Database & Connection Pool**: Database setup and connection management
- **Cache Performance**: LRU cache functionality
- **API Endpoints**: Core API functionality
- **SLA Monitoring**: SLA compliance tracking
- **Load Balancer**: Reverse proxy functionality
- **Performance Excellence**: Concurrent request handling
- **System Integration**: Complete workflow testing

### **Test with Running System**
```bash
# Start the system
python start_system.py

# In another terminal, run tests
python unit_test.py
```

## 📋 System Components

### **Core Files**
- `main.py` - Main FastAPI application
- `reverse_proxy.py` - Simple Python reverse proxy
- `start_system.py` - System startup script
- `unit_test.py` - Comprehensive test suite

### **Configuration Files**
- `config_dev.json` - Development environment
- `config_staging.json` - Staging environment
- `config_prod.json` - Production environment

### **Generated Files**
- `library_system.db` - SQLite database
- `sla_report.txt` - SLA compliance reports
- Log files from each API instance

## 🎯 Learning Objectives

This project demonstrates:

### **Full-scale Deployment**
- **Multi-process Architecture** without containers
- **Load Balancing** with simple Python proxy
- **Service Discovery** and health checking
- **Process Management** and monitoring

### **Performance Engineering**
- **Caching Strategies** with LRU implementation
- **Connection Pooling** for database efficiency
- **Batch Processing** for improved throughput
- **Concurrent Request Handling**

### **SLA Management**
- **Performance Monitoring** with percentile tracking
- **Availability Monitoring** and uptime calculation
- **Queue Management** and depth monitoring
- **Automated Reporting** for compliance

### **Environment Management**
- **Configuration-driven Deployment** 
- **Environment-specific Behavior**
- **Resource Scaling** per environment
- **Logging Level Management**

## 🔍 Monitoring & Observability

### **Real-time Metrics**
- Queue depth and processing times
- Cache hit rates and performance
- Connection pool utilization
- Request distribution across servers

### **SLA Compliance Tracking**
- 95th percentile response times
- System availability percentage
- Queue depth monitoring
- Automated threshold alerting

### **Performance Optimization**
- Database query optimization with indexes
- LRU cache for frequently accessed data
- Batch processing for efficiency
- Connection pool for resource management

## 🤝 Contributing

This is an educational project demonstrating full-scale deployment patterns. Feel free to:
- Add new reservation features
- Improve load balancing algorithms
- Enhance SLA monitoring
- Add more performance optimizations
- Implement additional environments

## 📄 License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Built with ❤️ for learning full-scale deployment and performance excellence**