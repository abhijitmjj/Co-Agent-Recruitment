'use server';

import { summarizeCandidateProfile, type SummarizeCandidateProfileInput } from '@/ai/flows/summarize-candidate-profile';
import { generateSEOKeywords, type GenerateSEOKeywordsInput } from '@/ai/flows/generate-seo-keywords';
import { suggestJobTitles, type SuggestJobTitlesInput } from '@/ai/flows/suggest-job-titles';
import type { CandidateProfileInput, JobDescriptionInput } from './schemas';

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
  } catch (error)
  {
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

// This is a mock matchmaking function. In a real app, this would be a complex AI call.
export async function performMatchmakingAction(
  item: Job | Candidate,
  allItems: (Job | Candidate)[]
): Promise<{ id: string; name: string; relevance: number; details: string; type: 'job' | 'candidate' }[]> {
  // Simulate AI matchmaking
  await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay

  if ('jobTitle' in item) { // item is Job, find Candidates
    return (allItems as Candidate[])
      .filter(candidate => 'fullName' in candidate) // Ensure it's a candidate
      .map(candidate => ({
        id: candidate.id,
        name: candidate.fullName,
        relevance: Math.random(), // Mock relevance
        details: candidate.aiSummary || candidate.experienceSummary.substring(0, 100) + '...',
        type: 'candidate' as const,
      }))
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 5); // Return top 5 matches
  } else { // item is Candidate, find Jobs
    return (allItems as Job[])
      .filter(job => 'jobTitle' in job) // Ensure it's a job
      .map(job => ({
        id: job.id,
        name: job.jobTitle,
        relevance: Math.random(), // Mock relevance
        details: job.responsibilities.substring(0, 100) + '...',
        type: 'job' as const,
      }))
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 5); // Return top 5 matches
  }
}

