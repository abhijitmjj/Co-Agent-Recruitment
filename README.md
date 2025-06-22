# Co-Agent-Recruitment

<img width="904" alt="image" src="https://github.com/user-attachments/assets/1f2b12a3-b809-47cc-a63d-80b8d656a155" />


This is a NextJS starter in Firebase Studio.

## Environment Variables

Copy `.env.example` to `.env.local` (or set equivalent environment variables) and fill in the following credentials:

- **NextAuth**:
  - `NEXTAUTH_URL`: the full URL of your site (e.g. `http://localhost:3000` in development or `https://your-domain.com` in production)
  - `NEXTAUTH_SECRET`: a secure, random string (at least 32 characters)
- **OAuth Providers**:
  - `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
  - `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`
  - **Ensure** you add your app's callback URIs in the Google/GitHub console (`/api/auth/callback/google`, etc.)
- **Firebase (client-side)**:
  - `NEXT_PUBLIC_FIREBASE_API_KEY`, `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, `NEXT_PUBLIC_FIREBASE_PROJECT_ID`,
    `NEXT_PUBLIC_FIREBASE_APP_ID`, `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`,
    `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`, `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`
- **Firebase Admin (server-side)**:
  - `FIREBASE_SERVICE_ACCOUNT_KEY`: your Firebase service account JSON as a **single-line** string (no line breaks).

  ```bash
  # Assuming serviceAccount.json is your downloaded key
  # Convert to one line with escaped newlines:
  jq -c . serviceAccount.json > .env.local
  ```

If `FIREBASE_SERVICE_ACCOUNT_KEY` is not set, the Admin SDK will fall back to Application Default Credentials (ADC). To configure ADC locally, run:

    gcloud auth application-default login

To get started, take a look at `src/app/page.tsx`.

![Co-Agent-Recruitment](https://github.com/user-attachments/assets/dc4c42ff-b095-4aff-8d8f-fbd5b0c90522)
