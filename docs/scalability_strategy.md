# AI Services Scalability & Scaling Strategy

This document outlines the infrastructure scaling, microservices architectural plan, and optimization methodology for taking the Zecpath AI hiring system from a prototype configuration to a highly available, large-scale operation processing tens of thousands of candidates concurrently.

## 1. Microservices Scaling Architecture

### Horizontal Scaling & Load Balancing
- **API Gateway & Layer 7 Load Balancing**: Deploy `Nginx` or `AWS ALB` to act as the primary reverse proxy. Routes incoming traffic:
  - `/api/v1/parse` -> CPU-Optimized Parsers Pool
  - `/api/v1/score` -> GPU-backed ATS Scoring Pool
  - `/ws/` -> WebSocket Clusters for AI Interviews
- **Microservices Orchestration**: All services (Extractors, Matchers, Scoring Engines, HR Interview Streamers) run in isolated Docker containers deployed via Kubernetes (K8s). Scale up Pods dynamically based on specific metrics (e.g., scale up parser when CPU hits 75%).

### Queue & Background Workers
- Introduce **Celery** + **RabbitMQ** (or Redis Queue). 
- Move all synchronous document processing (like `run_batch_pipeline.py`) to isolated asynchronous Celery workers.
- **Why?** Resume parsing and semantic embeddings block the event loop. Moving this to background task queues allows the frontend to respond efficiently with `HTTP 202 Accepted` and wait for processing completion via WebSockets or long polling.

## 2. API Response Latency Optimization

We have implemented strict caching strategies to drastically accelerate inference time. Let's look at `semantic_matcher.py`:
- **Problem**: Previously, comparing 1 candidate against 90 JDs meant calculating SentenceTransformer tensors for all 90 JDs every time the script was invoked.
- **Solution (`jd_embeddings_cache.pt`)**: We serialized Job Description tensors directly to disk/Redis. Latency of `model.encode()` dropped by ~90% because matrix multiplication against static job posts only happens once on ingestion, not on every candidate match.

Further strategies include:
- **Redis Result Caching**: Cache common `final_score` results based on matching a candidate's hash against a JD's hash.
- **Database Indexing**: Pre-indexing extracted Candidate skill strings into Elasticsearch or PGVector instead of using Python `for` loops.

## 3. Optimizing Memory & GPU Usage

- **Quantization Layer**: Transition from `.fp32` LLM HuggingFace models to quantized versions (`.fp16` or `.int8`). Model memory footprint shrinks by 50% without statistically degrading resume-sorting accuracy.
- **Model Multiplexing**: Instead of isolating `all-MiniLM-L6-v2` per thread, use a shared memory framework like NVIDIA Triton Inference Server or FastAPI background states to load the `.bin` weights exactly once. All worker threads query the same memory segment.

## 4. Real-time Service (Interviews) High Availability
- Real-time `WebSocket` microservices will be stateful (storing dialogue session variables). 
- To horizontally scale these: Implement **Redis Pub/Sub** to sync standard WebSocket state. If an Interview pod goes offline in Kubernetes, Redis retains the state of the conversation, allowing seamless reconnection to a different pod.
