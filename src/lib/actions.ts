

import { summarizeCandidateProfile, type SummarizeCandidateProfileInput } from '@/ai/flows/summarize-candidate-profile';
import { generateSEOKeywords, type GenerateSEOKeywordsInput } from '@/ai/flows/generate-seo-keywords';
import { suggestJobTitles, type SuggestJobTitlesInput } from '@/ai/flows/suggest-job-titles';
import { CandidateProfileSchema, JobDescriptionSchema, type CandidateProfileInput, type JobDescriptionInput } from './schemas';


export async function getSuggestedJobTitlesAction(input: SuggestJobTitlesInput) {
  try {
    const result = await suggestJobTitles(input);
    return { success: true, data: result.suggestedTitles };
  } catch (error) {
    console.error("Error suggesting job titles:", error);
    return { success: false, error: error instanceof Error ? error.message : "Failed to suggest job titles" };
  }
}

export async function summarizeCandidateProfileAction(input: SummarizeCandidateProfileInput) {
  try {
    const result = await summarizeCandidateProfile(input);
    return { success: true, data: result.summary };
  } catch (error) {
    console.error("Error summarizing candidate profile:", error);
    return { success: false, error: error instanceof Error ? error.message : "Failed to summarize profile" };
  }
}

export async function generateSEOKeywordsAction(input: GenerateSEOKeywordsInput) {
  try {
    const result = await generateSEOKeywords(input);
    return { success: true, data: result.keywords };
  } catch (error) {
    console.error("Error generating SEO keywords:", error);
    return { success: false, error: error instanceof Error ? error.message : "Failed to generate SEO keywords" };
  }
}

// Placeholder types for shared state, ideally these would be more complex and stored in a DB
export interface Job extends JobDescriptionInput {
  id: string;
  companyName?: string; // Example additional field
}

export interface Candidate extends CandidateProfileInput {
  id: string;
  aiSummary?: string;
}

// Type guards for robust validation
export const isJob = (item: any): item is Job => JobDescriptionSchema.safeParse(item).success;
export const isCandidate = (item: any): item is Candidate => CandidateProfileSchema.safeParse(item).success;


export async function publishEventAction(eventName: string, payload: any) {
  try {
    // Assuming the Python backend is running on localhost:8000
    const response = await fetch('http://localhost:8000/publish-event', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ event_name: eventName, payload }),
    });
    console.log(`Publishing event ${eventName} with response:`, response);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to publish event');
    }

    const result = await response.json();
    console.log(`Publishing event ${eventName} with response:`, result);
    return { success: true, data: result };
  } catch (error) {
    console.error(`Error publishing event ${eventName}:`, error);
    return { success: false, error: error instanceof Error ? error.message : `Failed to publish event ${eventName}` };
  }
}


// This is a mock matchmaking function. In a real app, this would be a complex AI call.
export async function performMatchmakingAction(
  item: Job | Candidate,
  allItems: (Job | Candidate)[],
  relevanceFn: (item: Job | Candidate, index: number) => number = () => Math.random()
): Promise<{ id: string; name: string; relevance: number; details: string; type: 'job' | 'candidate' }[]> {
  // Simulate AI matchmaking
  await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay

  if (isJob(item)) { // item is Job, find Candidates
    return allItems
      .filter(isCandidate)
      .map((candidate, index) => ({
        id: candidate.id,
        name: candidate.fullName,
        relevance: relevanceFn(candidate, index), // Mock relevance
        details: candidate.aiSummary || candidate.experienceSummary.substring(0, 100) + '...',
        type: 'candidate' as const,
      }))
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 5); // Return top 5 matches
  } else { // item is Candidate, find Jobs
    return allItems
      .filter(isJob)
      .map((job, index) => ({
        id: job.id,
        name: job.jobTitle,
        relevance: relevanceFn(job, index), // Mock relevance
        details: job.responsibilities.substring(0, 100) + '...',
        type: 'job' as const,
      }))
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 5); // Return top 5 matches
  }
}

export async function publishQueryAction(query: string, userId: string, sessionId?: string) {
  try {
    const response = await fetch('http://localhost:8000/orchestrator', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        user_id: userId,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to publish query');
    }

    const result = await response.json();
    return { success: true, data: result };
  } catch (error) {
    console.error(`Error publishing query:`, error);
    return { success: false, error: error instanceof Error ? error.message : `Failed to publish query` };
  }
}
