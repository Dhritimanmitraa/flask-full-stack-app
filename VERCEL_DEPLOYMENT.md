# Vercel Deployment Guide

This guide will help you deploy your Flask application to Vercel.

## Prerequisites

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Create a Vercel account at [vercel.com](https://vercel.com)

## Database Setup

Since Vercel is serverless, you'll need an external database. Here are some free options:

### Option 1: Neon (Recommended)
1. Go to [neon.tech](https://neon.tech)
2. Create a free account
3. Create a new database
4. Copy the connection string

### Option 2: Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create a free account
3. Create a new project
4. Go to Settings > Database
5. Copy the connection string

### Option 3: Railway
1. Go to [railway.app](https://railway.app)
2. Create a free account
3. Create a new PostgreSQL database
4. Copy the connection string

## Deployment Steps

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Set Environment Variables:**
   ```bash
   vercel env add SECRET_KEY
   vercel env add DATABASE_URL
   ```
   
   When prompted:
   - For `SECRET_KEY`: Enter a random secret key (you can generate one online)
   - For `DATABASE_URL`: Enter your PostgreSQL connection string

3. **Deploy:**
   ```bash
   vercel --prod
   ```

## Important Notes

- The app is configured to run in serverless mode
- Database connections are optimized for serverless environments
- Static files are served directly by Vercel
- The main entry point is `/api/index.py`

## Environment Variables Required

- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: PostgreSQL connection string

## File Structure for Vercel

```
├── api/
│   └── index.py          # Vercel entry point
├── app/                  # Your Flask application
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── vercel.json          # Vercel configuration
└── requirements.txt     # Python dependencies
```

## Troubleshooting

1. **Database Connection Issues:**
   - Make sure your DATABASE_URL is correct
   - Ensure your database allows external connections
   - Check if the connection string uses `postgresql://` (not `postgres://`)

2. **Static Files Not Loading:**
   - Vercel automatically serves files from the `static/` directory
   - Make sure your template references use the correct paths

3. **Function Timeout:**
   - Vercel free tier has a 10-second timeout limit
   - Optimize your database queries
   - Consider using database connection pooling

## Migration from Render

If you're migrating from Render:
1. Export your database from Render
2. Import it to your new database provider
3. Update the `DATABASE_URL` environment variable
4. Deploy to Vercel

## Local Development

To test locally:
```bash
python run.py
```

The serverless version can be tested with:
```bash
vercel dev
```
