# Kite Watch

Kite Watch is a web application that helps kite enthusiasts find and share great places to fly kites. Users can submit locations with ratings and notes about wind conditions, accessibility, and other relevant information.

## Features

- Submit kite flying locations with a name, notes, and a 1-5 star rating
- Browse locations added by other users
- Input validation and profanity filtering to maintain quality content
- Mobile-friendly responsive design

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: Simple JSON file storage
- **Deployment**: Docker support

## Setup

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/username/kite-watch.git
   cd kite-watch
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```
   The application will be available at http://localhost:5000

### Using Docker

1. Build and run using Docker:
   ```
   docker build -t kite-watch .
   docker run -p 5000:5000 -v $(pwd)/data:/data kite-watch
   ```

2. Use pre-built Docker image:
   ```
   docker pull git.woodburn.au/nathanwoodburn/kite-watch:latest
    ```

   Then run it with:
   ```
    docker run -p 5000:5000 git.woodburn.au/nathanwoodburn/kite-watch:latest
    ```

## Configuration

The application can be configured with environment variables:
- `WORKERS`: Number of Gunicorn workers (default: 1)
- `THREADS`: Number of threads per worker (default: 2)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.