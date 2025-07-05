# Cloud Run Deployment Guide

This guide provides step-by-step instructions for deploying the Co-Agent-Recruitment platform to Google Cloud Run.

## Prerequisites

Before deploying, ensure you have:

- Google Cloud SDK (`gcloud`) installed and configured
- A Google Cloud Project with billing enabled
- The following APIs enabled in your project:
  - Cloud Run API
  - Vertex AI API
  - Firestore API
  - Pub/Sub API
  - Cloud Build API
  - Container Registry API
- Docker installed (for local testing)
- Firebase project configured

## Environment Setup

1. **Set your Google Cloud project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable pubsub.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Set up authentication:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

## Backend Deployment (Python Agents)

1. **Navigate to the backend directory:**
   ```bash
   cd co_agent_recruitment
   ```

2. **Deploy the Python backend to Cloud Run:**
   ```bash
   gcloud run deploy co-agent-recruitment-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 3600 \
     --set-env-vars PROJECT_ID=YOUR_PROJECT_ID,GEMINI_MODEL=gemini-2.5-flash
   ```

3. **Note the service URL** that is displayed after successful deployment. You'll need this for the frontend configuration.

## Frontend Deployment (Next.js)

1. **Return to the project root:**
   ```bash
   cd ..
   ```

2. **Create a production environment file:**
   ```bash
   cp .env.example .env.production
   ```

3. **Configure production environment variables in `.env.production`:**
   ```bash
   # Authentication
   NEXTAUTH_SECRET=your_production_secret_32_chars
   NEXTAUTH_URL=https://your-frontend-url.run.app
   
   # Google OAuth
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   
   # GitHub OAuth (optional)
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   
   # AI Model Configuration
   GEMINI_MODEL=gemini-2.5-flash
   PROJECT_ID=YOUR_PROJECT_ID
   
   # Firebase Configuration
   FIREBASE_SERVICE_ACCOUNT_KEY=your_firebase_service_account_key_json
   NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=YOUR_PROJECT_ID
   NEXT_PUBLIC_FIREBASE_APP_ID=your_firebase_app_id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
   NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
   
   # Cloud Run Configuration
   CLOUD_RUNNER_AGENT_API_URL=https://co-agent-recruitment-backend-xxx-uc.a.run.app
   
   # Feature Flags
   NEXT_PUBLIC_FEATURE_ROLE_RESTRICTION_ENABLED=true
   ```

4. **Deploy the Next.js frontend to Cloud Run:**
   ```bash
   gcloud run deploy co-agent-recruitment-frontend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1 \
     --timeout 300 \
     --env-vars-file .env.production
   ```

## Post-Deployment Configuration

### 1. Firebase Authentication Setup

1. **Go to the Firebase Console** and select your project
2. **Enable Authentication** and configure sign-in methods:
   - Google (use the same OAuth client from Google Cloud Console)
   - GitHub (optional)
3. **Add authorized domains** in Authentication > Settings:
   - Add your Cloud Run frontend URL
   - Add any custom domains you plan to use

### 2. Firestore Database Setup

1. **Create a Firestore database** in your Firebase project
2. **Set up security rules** in `firestore.rules`:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // Allow authenticated users to read/write their own data
       match /users/{userId} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
       
       // Allow authenticated users to read/write job postings and resumes
       match /{collection=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

### 3. Pub/Sub Topics Setup

Create the required Pub/Sub topics:

```bash
# Create topics for agent communication
gcloud pubsub topics create parse-resume-events
gcloud pubsub topics create parse-job-posting-events
gcloud pubsub topics create compatibility-score-events

# Create subscriptions for Cloud Functions
gcloud pubsub subscriptions create firestore-saver-sub \
  --topic=parse-resume-events

gcloud pubsub subscriptions create job-posting-saver-sub \
  --topic=parse-job-posting-events

gcloud pubsub subscriptions create compatibility-saver-sub \
  --topic=compatibility-score-events
```

### 4. Cloud Functions Deployment (Optional)

Deploy the Firestore saver function:

```bash
cd co_agent_recruitment/firestore_saver
gcloud functions deploy firestore-saver \
  --runtime python39 \
  --trigger-topic parse-resume-events \
  --set-env-vars PROJECT_ID=YOUR_PROJECT_ID
```

## OAuth Configuration

### Google OAuth Setup

1. **Go to Google Cloud Console** > APIs & Services > Credentials
2. **Create OAuth 2.0 Client ID** for web application
3. **Add authorized redirect URIs:**
   - `https://your-frontend-url.run.app/api/auth/callback/google`
   - `http://localhost:3000/api/auth/callback/google` (for development)

### GitHub OAuth Setup (Optional)

1. **Go to GitHub** > Settings > Developer settings > OAuth Apps
2. **Create a new OAuth App**
3. **Set Authorization callback URL:**
   - `https://your-frontend-url.run.app/api/auth/callback/github`

## Custom Domain Setup (Optional)

1. **Map a custom domain** to your Cloud Run service:
   ```bash
   gcloud run domain-mappings create \
     --service co-agent-recruitment-frontend \
     --domain your-custom-domain.com \
     --region us-central1
   ```

2. **Update DNS records** as instructed by the mapping command

3. **Update environment variables** to use the custom domain

## Monitoring and Logging

1. **Enable Cloud Logging** for your services
2. **Set up monitoring** in Google Cloud Console
3. **Configure alerts** for service health and performance

## Security Considerations

1. **Review IAM permissions** for all services
2. **Enable Cloud Armor** for DDoS protection (optional)
3. **Set up VPC** for network isolation (optional)
4. **Regular security audits** of dependencies and configurations

## Troubleshooting

### Common Issues

1. **Build failures:**
   - Check that all required files are included
   - Verify environment variables are set correctly
   - Review build logs in Cloud Build

2. **Authentication errors:**
   - Verify OAuth client configuration
   - Check Firebase project settings
   - Ensure authorized domains are configured

3. **Service communication issues:**
   - Verify Cloud Run service URLs
   - Check IAM permissions
   - Review network connectivity

### Useful Commands

```bash
# View service logs
gcloud run services logs read co-agent-recruitment-frontend --region us-central1

# Update service with new environment variables
gcloud run services update co-agent-recruitment-frontend \
  --update-env-vars KEY=VALUE \
  --region us-central1

# Scale service
gcloud run services update co-agent-recruitment-frontend \
  --max-instances 10 \
  --region us-central1
```

## Cost Optimization

1. **Set appropriate resource limits** (CPU, memory)
2. **Configure auto-scaling** based on traffic patterns
3. **Use Cloud Run's pay-per-use** pricing model effectively
4. **Monitor usage** and optimize based on metrics

## Support

For deployment issues or questions:
- Check the [main README](README.md) for general setup
- Review Google Cloud Run documentation
- Open an issue in the project repository