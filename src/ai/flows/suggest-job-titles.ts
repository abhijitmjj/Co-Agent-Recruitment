// 'use server';

/**
 * @fileOverview Job title suggestion flow.
 *
 * This file defines a Genkit flow that suggests job titles based on a given job description.
 * It exports:
 * - suggestJobTitles: The main function to trigger the flow.
 * - SuggestJobTitlesInput: The input type for the flow.
 * - SuggestJobTitlesOutput: The output type for the flow.
 */

'use server';

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SuggestJobTitlesInputSchema = z.object({
  jobDescription: z
    .string()
    .describe('The description of the job for which to suggest titles.'),
});
export type SuggestJobTitlesInput = z.infer<typeof SuggestJobTitlesInputSchema>;

const SuggestJobTitlesOutputSchema = z.object({
  suggestedTitles: z
    .array(z.string())
    .describe('An array of suggested job titles based on the job description.'),
});
export type SuggestJobTitlesOutput = z.infer<typeof SuggestJobTitlesOutputSchema>;

export async function suggestJobTitles(input: SuggestJobTitlesInput): Promise<SuggestJobTitlesOutput> {
  return suggestJobTitlesFlow(input);
}

const prompt = ai.definePrompt({
  name: 'suggestJobTitlesPrompt',
  input: {schema: SuggestJobTitlesInputSchema},
  output: {schema: SuggestJobTitlesOutputSchema},
  prompt: `You are an expert in job title optimization for SEO and candidate attraction.

  Based on the following job description, suggest 5 job titles that are likely to attract qualified candidates and perform well in search engines. Return the titles as a JSON array of strings.

  Job Description: {{{jobDescription}}}`,
});

const suggestJobTitlesFlow = ai.defineFlow(
  {
    name: 'suggestJobTitlesFlow',
    inputSchema: SuggestJobTitlesInputSchema,
    outputSchema: SuggestJobTitlesOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
