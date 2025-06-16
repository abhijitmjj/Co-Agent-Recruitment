import { config } from 'dotenv';
import path from 'path';

// Securely load environment variables with explicit path
const envPath = path.resolve(process.cwd(), '.env');
config({ path: envPath });

import '@/ai/flows/summarize-candidate-profile.ts';
import '@/ai/flows/generate-seo-keywords.ts';
import '@/ai/flows/suggest-job-titles.ts';