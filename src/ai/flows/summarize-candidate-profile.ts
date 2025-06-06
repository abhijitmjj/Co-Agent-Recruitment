// Summarizes candidate profiles into concise descriptions, highlighting key skills and experience, to improve matching accuracy and efficiency.
'use server';

/**
 * @fileOverview Summarizes candidate profiles for efficient job matching.
 *
 * - summarizeCandidateProfile - A function that summarizes a candidate's profile.
 * - SummarizeCandidateProfileInput - The input type for the summarizeCandidateProfile function.
 * - SummarizeCandidateProfileOutput - The return type for the summarizeCandidateProfile function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeCandidateProfileInputSchema = z.object({
  profileText: z
    .string()
    .describe('The full text of the candidate profile to summarize.'),
});
export type SummarizeCandidateProfileInput = z.infer<
  typeof SummarizeCandidateProfileInputSchema
>;

const SummarizeCandidateProfileOutputSchema = z.object({
  summary: z
    .string()
    .describe(
      'A concise summary of the candidate profile, highlighting key skills and experience.'
    ),
});
export type SummarizeCandidateProfileOutput = z.infer<
  typeof SummarizeCandidateProfileOutputSchema
>;

export async function summarizeCandidateProfile(
  input: SummarizeCandidateProfileInput
): Promise<SummarizeCandidateProfileOutput> {
  return summarizeCandidateProfileFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeCandidateProfilePrompt',
  input: {schema: SummarizeCandidateProfileInputSchema},
  output: {schema: SummarizeCandidateProfileOutputSchema},
  prompt: `You are an expert resume summarizer for a recruiting company.  Please provide a concise summary of the following candidate profile, highlighting key skills and experience.  The summary should be no more than 100 words.\n\nCandidate Profile:\n{{{profileText}}}`,
});

const summarizeCandidateProfileFlow = ai.defineFlow(
  {
    name: 'summarizeCandidateProfileFlow',
    inputSchema: SummarizeCandidateProfileInputSchema,
    outputSchema: SummarizeCandidateProfileOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
