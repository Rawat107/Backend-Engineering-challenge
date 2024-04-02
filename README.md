# Backend-Engineering-challenge
This is the backend microservices-based system that manages a simple e-commerce application, providing endpoints to manage products, orders, and user.

## Prerequisites

Before running the application and tests, make sure you have the following installed:

- Python 3.x: [Download and Install Python](https://www.python.org/downloads/)
- MongoDB: [Download and Install MongoDB](https://docs.mongodb.com/manual/installation/)

## Installation

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd e-commerce-backend
    ```

2. **Set up a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv myenv
    source myenv/bin/activate  # for Linux/macOS
    myenv\Scripts\activate      # for Windows
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up MongoDB:**

   - Install MongoDB according to your operating system.
   - Run MongoDB service.

## Configuration

1. **Database Configuration:**

    - Ensure MongoDB is running.
    - Modify the `MONGO_URI` variable in the `order_services.py` and `product_services.py` files if your MongoDB setup requires it. By default, it connects to `mongodb://localhost:27017/`.

2. **Environment Variables:**

    - If you need to configure any environment variables, create a `.env` file in the root directory and define them there.

## Usage

1. **Run the Application:**

    ```bash
    python order_services.py
    python product_services.py
    ```

2. **Run Tests:**

    ```bash
    pytest -s <test_name>
    ```

## Additional Notes

- Ensure all dependencies are installed before running the application or tests.
- If encountering any issues, refer to the project's documentation.
