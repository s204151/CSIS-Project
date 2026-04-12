# Security Event Monitoring System

A lightweight backend system for ingesting and analyzing security events using an event-driven architecture.

Built in 2 weeks as part of my preparation for a backend software engineering role, practicing backend technologies and design patterns relevant for scalable and security-focused systems.

---

## Overview

The system simulates a simplified security monitoring pipeline:

1. Events are ingested via a REST API  
2. Stored in a PostgreSQL database  
3. Processed asynchronously by a worker service  
4. Detection logic evaluates events  
5. Alerts are generated for suspicious behavior  

---

## Architecture

The system is designed using an event-driven approach to decouple ingestion from processing.

- API service handles incoming events  
- Worker service processes events asynchronously  
- Database stores both raw events and generated alerts  

This separation allows the system to scale and keeps responsibilities isolated.

---

## Technologies

FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Docker, pytest, GitHub Actions

---

## Example Detection Logic

- Multiple `login_failure` events from the same IP → triggers brute-force alert  
- `login_success` following repeated failures → flagged as suspicious  

---

## API

### Events
- `POST /events`
- `GET /events`
- `GET /events/{id}`

### Alerts
- `GET /alerts`
- `GET /alerts/{id}`

---

## Run

```bash
docker compose --env-file .env up