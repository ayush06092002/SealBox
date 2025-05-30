# SealBox: Secure, Temporary File Sharing

SealBox is a robust and secure temporary file sharing platform designed for sharing sensitive documents with controlled access. Files are encrypted before storage and automatically expire or become inaccessible after a set number of downloads, ensuring data privacy and efficient resource management.

-----

## ✨ Features

  * **End-to-End Encryption:** Files are encrypted client-side (or server-side before storage) using AES-256 (or similar) before being uploaded to cloud storage.
  * **Time-Limited Access:** Uploaded files automatically expire after a configurable duration.
  * **Download Count Limit:** Files can be configured to be accessible only for a specific number of downloads.
  * **Secure Storage:** Leverages Amazon S3 for highly scalable, durable, and secure cloud storage.
  * **Persistent Metadata:** File metadata (tokens, expiry, download counts) is securely stored in MongoDB, ensuring data persistence across application restarts.
  * **Authentication:** User authentication via JWT (JSON Web Tokens) for secure access to upload and manage files.
  * **FastAPI Backend:** Built with FastAPI for high performance and easy API development.

-----

## 🏗️ Architecture & Tech Stack

SealBox is built with a modern, asynchronous Python stack:

  * **Backend Framework:** [**FastAPI**](https://fastapi.tiangolo.com/) - A modern, fast (high-performance) web framework for building APIs with Python 3.8+.
  * **Web Server:** [**Uvicorn**](https://www.uvicorn.org/) - An ASGI server for FastAPI.
  * **Database:** [**MongoDB**](https://www.mongodb.com/) - A NoSQL document database used for storing file metadata (e.g., download tokens, expiry dates, S3 keys). Managed asynchronously with [**Motor**](https://motor.readthedocs.io/en/stable/).
  * **File Storage:** [**Amazon S3**](https://aws.amazon.com/s3/) - Scalable object storage for encrypted files. Interacted with asynchronously using [**aiobotocore**](https://github.com/aio-libs/aiobotocore) (an async wrapper for `boto3`).
  * **Encryption:** Custom Python module for AES-256 encryption/decryption (or a similar symmetric encryption scheme).
  * **Authentication:** JWT (JSON Web Tokens) with [**python-jose**](https://python-jose.readthedocs.io/) and password hashing with [**Passlib**](https://passlib.readthedocs.io/).
  * **Configuration:** [**Pydantic-Settings**](https://docs.pydantic.dev/latest/usage/pydantic_settings/) - For managing application settings and environment variables.
  * **Data Validation:** [**Pydantic**](https://www.google.com/search?q=https://docs.pydantic.dev/) - For robust data validation and serialization.

-----

## 📂 Project Structure

```
sealbox/
├── backend/
│   ├── core/
│   │   ├── config.py         # Application settings loaded from .env
│   │   ├── database.py       # MongoDB connection and dependency
│   │   └── s3.py             # AWS S3 client connection and dependency
│   ├── models/
│   │   ├── file.py           # Pydantic model for file metadata (MongoDB document)
│   ├── routes/
│   │   ├── auth.py           # User authentication endpoints (signup, login)
│   │   ├── upload.py         # File upload endpoint
│   │   └── download.py       # File download endpoint
│   ├── main.py               # Main FastAPI application entry point, includes routers and lifespan events
│   └── __init__.py
├── encryption/
│   ├── encryptor.py          # Encryption/decryption logic
│   └── __init__.py
├── .env.example              # Example environment variables file
├── .env                      # Your actual environment variables (IGNORED BY GIT)
├── requirements.txt          # Project dependencies
├── README.md                 # This README file
└── venv/                     # Python virtual environment (IGNORED BY GIT)
```

-----

## 🚀 Getting Started

Follow these steps to set up and run SealBox locally.

### Prerequisites

  * **Python 3.8+**
  * **MongoDB:**
      * Install MongoDB Community Server: [MongoDB Installation Guides](https://www.mongodb.com/docs/manual/installation/)
      * Ensure your MongoDB instance is running (default port `27017`).
  * **AWS Account & S3 Bucket:**
      * An active AWS account.
      * An S3 bucket created in your desired region (e.g., `ap-south-1`).
      * IAM User with programmatic access (Access Key ID & Secret Access Key) and permissions for `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket` on your chosen bucket.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/ayush06092002/sealbox.git
    cd sealbox
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**

      * Create a `.env` file in the project root directory (same level as `requirements.txt`).
      * Copy the content from `.env.example` into your new `.env` file.
      * **Fill in the placeholder values** with your actual secrets and configurations.

    <!-- end list -->

    ```dotenv
    # .env
    # --- JWT Authentication Settings ---
    JWT_SECRET_KEY="YOUR_SUPER_SECRET_JWT_KEY_GENERATED_SECURELY"
    ACCESS_TOKEN_EXPIRE_MINUTES=120 # 2 hours

    # --- Encryption Settings ---
    ENCRYPTION_KEY="YOUR_32_BYTE_ENCRYPTION_KEY_FOR_AES256" # Must be exactly 32 characters for AES-256

    # --- AWS S3 Settings ---
    AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
    AWS_REGION_NAME="ap-south-1" # e.g., us-east-1, eu-west-2. Must match your S3 bucket's region
    S3_BUCKET_NAME="your-unique-sealbox-bucket-name"

    # --- MongoDB Settings ---
    MONGO_DB_URL="mongodb://localhost:27017" # Adjust if your MongoDB is hosted elsewhere
    MONGO_DB_NAME="sealbox_db"
    MONGO_COLLECTION_NAME="files"

    # --- Application Settings (Optional, default values available) ---
    APP_NAME="SealBox"
    ENVIRONMENT="development"
    DEBUG=True
    ```

    **Important:** Do NOT commit your `.env` file to version control.

### Running the Application

Once everything is set up, start the FastAPI application:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

  * `--reload`: Automatically reloads the server on code changes (for development).
  * `--host 0.0.0.0`: Makes the server accessible from other devices on your local network.
  * `--port 8000`: Runs the server on port 8000.

You should see logs indicating successful connections to MongoDB and AWS S3 on startup.

The API documentation will be available at: `http://localhost:8000/docs`

-----

## 🔌 API Endpoints

SealBox provides the following RESTful API endpoints:

### Authentication

  * **`POST /auth/signup`**
      * **Description:** Registers a new user.
      * **Request Body (JSON):**
        ```json
        {
          "username": "testuser",
          "password": "strongpassword123"
        }
        ```
  * **`POST /auth/login`**
      * **Description:** Authenticates a user and returns a JWT access token.
      * **Request Body (JSON):**
        ```json
        {
          "username": "testuser",
          "password": "strongpassword123"
        }
        ```
      * **Response (JSON):**
        ```json
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer"
        }
        ```
      * **Note:** This token needs to be included in the `Authorization` header as `Bearer <access_token>` for protected endpoints.

### File Management

  * **`POST /upload`**
      * **Description:** Uploads an encrypted file to S3 and stores its metadata in MongoDB. Requires authentication.
      * **Request:**
          * **Header:** `Authorization: Bearer <your_access_token>`
          * **Body:** `multipart/form-data` with a `File` field (the actual file).
      * **Response (JSON):**
        ```json
        {
          "download_link": "http://localhost:8000/download/abcdefg1",
          "expires_at": "2025-12-31T23:59:59Z"
        }
        ```
  * **`GET /download/{token}`**
      * **Description:** Downloads an encrypted file, decrypts it, and streams it back. Decrements download count and checks for expiry/limit. Does **not** require authentication for download.
      * **Path Parameter:** `token` (the unique 8-character token from the upload response).
      * **Response:** File download (`application/octet-stream`) or HTTP error (404, 403, 500).

-----

## 🔒 Security Considerations

  * **Encryption:** Files are encrypted before leaving your application towards S3.
  * **JWT Authentication:** Protects upload and management endpoints.
  * **Environment Variables:** Sensitive information (keys, credentials) are stored in `.env` and kept out of version control.
  * **Ephemeral Links:** Time and download limited links reduce the window of exposure for shared files.
  * **IAM Least Privilege:** The AWS IAM user should have only the minimum necessary permissions on the S3 bucket (`PutObject`, `GetObject`, `DeleteObject`).

-----

## 🚀 Future Enhancements

  * **User-Specific File Listings:** Allow authenticated users to view/manage their uploaded files.
  * **Web Interface:** A simple frontend (React, Vue, etc.) for a better user experience.
  * **Custom Expiry/Download Limits:** Allow users to specify these settings during upload.
  * **File Previews:** Secure, temporary previews of common file types.
  * **Auditing/Logging:** More detailed logging of file access and events.
  * **Containerization:** Dockerize the application for easier deployment.
  * **Cloud Deployment:** Kubernetes, AWS ECS, or other cloud platforms for production.
  * **Asynchronous File Operations:** Stream S3 downloads/uploads without loading entire file into memory (currently reads/writes whole file).

-----

## 🤝 Contributing

Contributions are welcome\! Please fork the repository, create a new branch, and submit a pull request.
