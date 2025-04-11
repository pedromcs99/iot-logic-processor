# IoT Logic Processor

The **IoT Logic Processor** is a machine data ingestion and processing service built with **FastAPI**, **Celery**, and **RabbitMQ**. It simulates IoT devices sending data, processes the data using custom logic, and publishes the results back to a message queue. This project demonstrates a scalable architecture for real-time data processing.

## Features

- **Custom Logic Execution**: Each machine has its own processing logic, which can be dynamically updated via the API.
- **Message Queue Integration**: Uses RabbitMQ for communication between producers, consumers, and workers.
- **Task Queue Management**: Processes tasks asynchronously using Celery.
- **In-Memory Caching**: Caches machine logic in Redis for faster access.
- **Simulated IoT Devices**: Mock machines send random data to the system for processing.
- **API for Machine Management**: Manage machine logic via a RESTful API built with FastAPI.

## Architecture

The system consists of the following components:

1. **Producer**: Simulates IoT devices sending data to RabbitMQ.
2. **Consumer**: Listens to RabbitMQ and sends tasks to Celery.
3. **Worker**: Processes tasks using custom logic and publishes results back to RabbitMQ.
4. **API**: Provides endpoints to manage machine logic.
5. **Redis**: Caches machine logic and stores machine states.
6. **RabbitMQ**: Acts as the message broker for communication between components.

## Technologies Used

- **Python 3.9**
- **FastAPI** for the REST API
- **Celery** for task queue management
- **RabbitMQ** as the message broker
- **Redis** for caching
- **Docker** and **Docker Compose** for containerization

## Setup and Installation

### Prerequisites

- Docker and Docker Compose installed on your system.

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/pedromcs99/iot-logic-processor#
   cd iot-logic-processor
   ```

2. Build and start the services using Docker Compose:

   ```bash
   docker-compose up --build
   ```

3. Access the services:
   - **API**: [http://localhost:8001](http://localhost:8001)
   - **RabbitMQ Management UI**: [http://localhost:15672](http://localhost:15672) (default credentials: `guest`/`guest`)
   - **Flower (Celery Monitoring)**: [http://localhost:5555](http://localhost:5555)

## Usage

### Simulating IoT Devices

The `producer` service simulates IoT devices sending data to RabbitMQ. You can view the logs to see the data being sent.

### Managing Machine Logic

Use the API to manage machine logic:

- **Get Machine Logic**:

  ```bash
  curl http://localhost:8001/machines/machine_A/logic
  ```

- **Update Machine Logic**:
  ```bash
  curl -X POST http://localhost:8001/machines/machine_A/logic \
       -H "Content-Type: application/json" \
       -d '{"logic": "def process(data, state): state[\"status\"] = \"running\" if data[\"signal\"] == 1 else \"stopped\"; return state"}'
  ```

### Viewing Processed Results

Processed results are published back to RabbitMQ. You can consume these messages using a RabbitMQ client or by extending the system.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Contact

For any questions or feedback, please contact pedromcs99@gmail.com.
