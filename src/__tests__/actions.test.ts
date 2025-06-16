// Mock the genkit flows to avoid module import issues
jest.mock('@/ai/flows/summarize-candidate-profile', () => ({
  summarizeCandidateProfile: jest.fn(),
}));

jest.mock('@/ai/flows/generate-seo-keywords', () => ({
  generateSEOKeywords: jest.fn(),
}));

jest.mock('@/ai/flows/suggest-job-titles', () => ({
  suggestJobTitles: jest.fn(),
}));

import { performMatchmakingAction, isJob, isCandidate } from '../lib/actions';
import type { Job, Candidate } from '../lib/actions';

// Mock data for testing
const mockJobs: Job[] = [
  { id: 'job1', jobTitle: 'Software Engineer', responsibilities: 'Develop and maintain web applications. This is a long text to pass validation.', requiredSkills: 'JavaScript, React, Node.js' },
  { id: 'job2', jobTitle: 'Product Manager', responsibilities: 'Define product vision and strategy. This is a long text to pass validation.', requiredSkills: 'Agile, Scrum, JIRA' },
];

const mockCandidates: Candidate[] = [
  { id: 'cand1', fullName: 'Alice Smith', skills: 'JavaScript, React, Node.js', experienceSummary: '5 years of experience in web development. This is a long text to pass validation.', locationPreference: 'Remote' },
  { id: 'cand2', fullName: 'Bob Johnson', skills: 'Python, Django, Flask', experienceSummary: '3 years of experience in backend development. This is a long text to pass validation.', locationPreference: 'New York' },
];

const mockCombinedList = [...mockJobs, ...mockCandidates];

// Mock relevance function for deterministic testing
const deterministicRelevanceFn = (_item: Job | Candidate, index: number) => 1 - (index * 0.1);

describe('performMatchmakingAction', () => {
  it('should return a sorted list of candidates for a given job', async () => {
    const job = mockJobs[0];
    const matches = await performMatchmakingAction(job, mockCombinedList, deterministicRelevanceFn);

    expect(matches).toHaveLength(2);
    expect(matches[0].name).toBe('Alice Smith');
    expect(matches[0].relevance).toBe(1);
    expect(matches[1].name).toBe('Bob Johnson');
    expect(matches[1].relevance).toBe(0.9);
  });

  it('should return a sorted list of jobs for a given candidate', async () => {
    const candidate = mockCandidates[0];
    const matches = await performMatchmakingAction(candidate, mockCombinedList, deterministicRelevanceFn);
    
    expect(matches).toHaveLength(2);
    expect(matches[0].name).toBe('Software Engineer');
    expect(matches[0].relevance).toBe(1);
    expect(matches[1].name).toBe('Product Manager');
    expect(matches[1].relevance).toBe(0.9);
  });

  it('should use the default random relevance function if no function is provided', async () => {
    const job = mockJobs[0];
    const matches = await performMatchmakingAction(job, mockCombinedList);
    
    expect(matches).toHaveLength(2);
    matches.forEach(match => {
      expect(typeof match.relevance).toBe('number');
      expect(match.relevance).toBeGreaterThanOrEqual(0);
      expect(match.relevance).toBeLessThanOrEqual(1);
    });
  });
});

describe('Type Guards', () => {
  it('isJob should correctly identify jobs', () => {
    expect(isJob(mockJobs[0])).toBe(true);
    expect(isJob(mockCandidates[0])).toBe(false);
  });

  it('isCandidate should correctly identify candidates', () => {
    expect(isCandidate(mockCandidates[0])).toBe(true);
    expect(isCandidate(mockJobs[0])).toBe(false);
  });
});