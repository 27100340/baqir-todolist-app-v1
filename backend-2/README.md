# baqir-todolist-app-backend
# TodoList API

A FastAPI-based backend for a TodoList application.

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file based on `.env.example`
6. Run the application: `uvicorn main:app --reload`

## Deploying to Vercel

### Prerequisites

1. [Vercel CLI](https://vercel.com/download) installed
2. A Vercel account
3. MongoDB Atlas account (or any MongoDB provider)

### Deployment Steps

1. Login to Vercel CLI:
   ```
   vercel login
   ```

2. Set up environment variables in Vercel:
   - Go to your Vercel dashboard
   - Select your project
   - Go to Settings > Environment Variables
   - Add all variables from your `.env` file

3. Deploy the application:
   ```
   vercel
   ```

4. For production deployment:
   ```
   vercel --prod
   ```

### Important Notes

- The application uses MongoDB, so make sure your MongoDB connection string is accessible from Vercel's serverless functions
- Ensure your MongoDB Atlas cluster has network access from anywhere (or at least from Vercel's IP ranges)
- The `vercel.json` file configures the deployment to use a serverless function

## API Documentation

Once deployed, you can access the API documentation at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc UI