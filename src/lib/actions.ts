

import { summarizeCandidateProfile, type SummarizeCandidateProfileInput } from '@/ai/flows/summarize-candidate-profile';
import { generateSEOKeywords, type GenerateSEOKeywordsInput } from '@/ai/flows/generate-seo-keywords';
import { suggestJobTitles, type SuggestJobTitlesInput } from '@/ai/flows/suggest-job-titles';
import { CandidateProfileSchema, JobDescriptionSchema, type CandidateProfileInput, type JobDescriptionInput } from './schemas';


// Utility function for consistent error handling across actions
const handleActionError = <T = unknown>(error: unknown, context: string): ActionResult<T> => {
  const errorMessage = error instanceof Error ? error.message : `Unknown error in ${context}`;
  console.error(`Error in ${context}:`, error);
  return { success: false, error: errorMessage };
};

// Utility function for successful action results
const createSuccessResult = <T>(data: T): ActionResult<T> => ({
  success: true,
  data,
});

export async function getSuggestedJobTitlesAction(input: SuggestJobTitlesInput): Promise<ActionResult<string[]>> {
  try {
    const result = await suggestJobTitles(input);
    return createSuccessResult(result.suggestedTitles);
  } catch (error) {
    return handleActionError(error, "getSuggestedJobTitlesAction");
  }
}

export async function summarizeCandidateProfileAction(input: SummarizeCandidateProfileInput): Promise<ActionResult<string>> {
  try {
    const result = await summarizeCandidateProfile(input);
    return createSuccessResult(result.summary);
  } catch (error) {
    return handleActionError(error, "summarizeCandidateProfileAction");
  }
}

export async function generateSEOKeywordsAction(input: GenerateSEOKeywordsInput): Promise<ActionResult<string[]>> {
  try {
    const result = await generateSEOKeywords(input);
    return createSuccessResult(result.keywords);
  } catch (error) {
    return handleActionError(error, "generateSEOKeywordsAction");
  }
}

// Enhanced types with better documentation and optional fields
export interface Job extends JobDescriptionInput {
  /** Unique identifier for the job posting */
  id: string;
  /** Timestamp when the job was created */
  createdAt?: Date;
  /** Timestamp when the job was last updated */
  updatedAt?: Date;
  /** Whether the job posting is currently active */
  isActive?: boolean;
}

export interface Candidate extends CandidateProfileInput {
  /** Unique identifier for the candidate */
  id: string;
  /** AI-generated summary of the candidate's profile */
  aiSummary?: string;
  /** Email address of the user associated with this candidate profile */
  user_email?: string;
  /** Timestamp when the profile was created */
  createdAt?: Date;
  /** Timestamp when the profile was last updated */
  updatedAt?: Date;
  /** Whether the candidate profile is currently active */
  isActive?: boolean;
}

// Utility types for better type safety
export type MatchResult = {
  id: string;
  name: string;
  relevance: number;
  details: string;
  type: 'job' | 'candidate';
};

export type ActionResult<T = unknown> = {
  success: boolean;
  data?: T;
  error?: string;
};

// Constants for better maintainability
export const MATCHMAKING_CONSTANTS = {
  DEFAULT_MAX_RESULTS: 5,
  MAX_ALLOWED_RESULTS: 100,
  DEFAULT_TIMEOUT: 1000,
  MAX_DETAILS_LENGTH: 97,
} as const;

// Type guards for robust validation with enhanced error handling and logging
export const isJob = (item: unknown): item is Job => {
  if (!item || typeof item !== 'object') {
    return false;
  }
  
  const parseResult = JobDescriptionSchema.safeParse(item);
  if (!parseResult.success) {
    console.debug('Job validation failed:', parseResult.error.issues);
  }
  
  return parseResult.success;
};

export const isCandidate = (item: unknown): item is Candidate => {
  if (!item || typeof item !== 'object') {
    return false;
  }
  
  const parseResult = CandidateProfileSchema.safeParse(item);
  if (!parseResult.success) {
    console.debug('Candidate validation failed:', parseResult.error.issues);
  }
  
  return parseResult.success;
};

// Enhanced type guard with detailed validation result
export const validateJob = (item: unknown): { isValid: boolean; errors?: string[]; data?: Job } => {
  if (!item || typeof item !== 'object') {
    return { isValid: false, errors: ['Item must be a non-null object'] };
  }
  
  const parseResult = JobDescriptionSchema.safeParse(item);
  if (!parseResult.success) {
    const errors = parseResult.error.issues.map(issue => `${issue.path.join('.')}: ${issue.message}`);
    return { isValid: false, errors };
  }
  
  return { isValid: true, data: { ...parseResult.data, id: (item as Record<string, unknown>).id as string || '' } as Job };
};

export const validateCandidate = (item: unknown): { isValid: boolean; errors?: string[]; data?: Candidate } => {
  if (!item || typeof item !== 'object') {
    return { isValid: false, errors: ['Item must be a non-null object'] };
  }
  
  const parseResult = CandidateProfileSchema.safeParse(item);
  if (!parseResult.success) {
    const errors = parseResult.error.issues.map(issue => `${issue.path.join('.')}: ${issue.message}`);
    return { isValid: false, errors };
  }
  
  return {
    isValid: true,
    data: {
      ...parseResult.data,
      id: (item as Record<string, unknown>).id as string || '',
      aiSummary: (item as Record<string, unknown>).aiSummary as string | undefined,
      user_email: (item as Record<string, unknown>).user_email as string | undefined
    } as Candidate
  };
};


export async function publishEventAction(
  eventName: string,
  payload: unknown,
  options: { timeout?: number; baseUrl?: string } = {}
): Promise<ActionResult> {
  const { timeout = 5000, baseUrl = 'http://localhost:8000' } = options;
  
  try {
    // Input validation
    if (!eventName || typeof eventName !== 'string') {
      throw new Error('Event name must be a non-empty string');
    }
    
    if (eventName.length > 100) {
      throw new Error('Event name must not exceed 100 characters');
    }

    // Create AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(`${baseUrl}/publish-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ event_name: eventName, payload }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    console.log(`Publishing event ${eventName} with status:`, response.status);
    
    if (!response.ok) {
      let errorMessage = 'Failed to publish event';
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        // If we can't parse the error response, use the default message
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log(`Successfully published event ${eventName}`);
    return createSuccessResult(result);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return handleActionError(new Error(`Request timeout after ${timeout}ms`), `publishEventAction(${eventName})`);
    }
    return handleActionError(error, `publishEventAction(${eventName})`);
  }
}


// Enhanced matchmaking function with better error handling and performance optimization
export async function performMatchmakingAction(
  item: Job | Candidate,
  allItems: (Job | Candidate)[],
  options: {
    relevanceFn?: (item: Job | Candidate, index: number) => number;
    maxResults?: number;
    timeout?: number;
  } = {}
): Promise<ActionResult<MatchResult[]>> {
  const {
    relevanceFn = () => Math.random(),
    maxResults = MATCHMAKING_CONSTANTS.DEFAULT_MAX_RESULTS,
    timeout = MATCHMAKING_CONSTANTS.DEFAULT_TIMEOUT
  } = options;

  try {
    // Input validation
    if (!item || !Array.isArray(allItems)) {
      return { success: false, error: 'Invalid input parameters' };
    }

    if (maxResults <= 0 || maxResults > MATCHMAKING_CONSTANTS.MAX_ALLOWED_RESULTS) {
      return { success: false, error: `maxResults must be between 1 and ${MATCHMAKING_CONSTANTS.MAX_ALLOWED_RESULTS}` };
    }

    // Simulate AI matchmaking with configurable timeout
    await new Promise(resolve => setTimeout(resolve, timeout));

    // Filter and validate items upfront for better performance
    const validCandidates = allItems.filter(isCandidate);
    const validJobs = allItems.filter(isJob);

    if (isJob(item)) {
      // item is Job, find matching Candidates
      if (validCandidates.length === 0) {
        return createSuccessResult([]);
      }

      const matches = validCandidates
        .map((candidate, index) => {
          const relevance = Math.max(0, Math.min(1, relevanceFn(candidate, index))); // Clamp between 0-1
          const details = candidate.aiSummary ||
                         (candidate.experienceSummary.length > 100
                           ? candidate.experienceSummary.substring(0, MATCHMAKING_CONSTANTS.MAX_DETAILS_LENGTH) + '...'
                           : candidate.experienceSummary);
          
          return {
            id: candidate.id,
            name: candidate.fullName,
            relevance,
            details,
            type: 'candidate' as const,
          };
        })
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, maxResults);

      return createSuccessResult(matches);
    } else if (isCandidate(item)) {
      // item is Candidate, find matching Jobs
      if (validJobs.length === 0) {
        return createSuccessResult([]);
      }

      const matches = validJobs
        .map((job, index) => {
          const relevance = Math.max(0, Math.min(1, relevanceFn(job, index))); // Clamp between 0-1
          const details = job.responsibilities.length > 100
                         ? job.responsibilities.substring(0, MATCHMAKING_CONSTANTS.MAX_DETAILS_LENGTH) + '...'
                         : job.responsibilities;
          
          return {
            id: job.id,
            name: job.jobTitle,
            relevance,
            details,
            type: 'job' as const,
          };
        })
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, maxResults);

      return createSuccessResult(matches);
    } else {
      return { success: false, error: 'Item must be either a Job or Candidate' };
    }
  } catch (error) {
    return handleActionError(error, 'performMatchmakingAction');
  }
}

export async function publishQueryAction(
  query: string,
  userId: string,
  sessionId?: string,
  options: { timeout?: number; baseUrl?: string } = {}
): Promise<ActionResult> {
  const { timeout = 1000000, baseUrl = 'http://localhost:8000' } = options;
  
  try {
    // Input validation
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string');
    }
    
    if (!userId || typeof userId !== 'string') {
      throw new Error('User ID must be a non-empty string');
    }
    
    if (query.length > 10000) {
      throw new Error('Query must not exceed 10,000 characters');
    }

    if (sessionId && typeof sessionId !== 'string') {
      throw new Error('Session ID must be a string if provided');
    }

    // Create AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(`${baseUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.trim(),
        user_id: userId,
        session_id: sessionId,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = 'Failed to publish query';
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        // If we can't parse the error response, use the default message
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return createSuccessResult(result);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return handleActionError(new Error(`Request timeout after ${timeout}ms`), 'publishQueryAction');
    }
    return handleActionError(error, 'publishQueryAction');
  }
}
