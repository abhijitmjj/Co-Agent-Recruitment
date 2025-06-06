'use server';

/**
 * @fileOverview A flow to generate SEO keywords based on successful job matches.
 *
 * - generateSEOKeywords - A function that generates SEO keywords.
 * - GenerateSEOKeywordsInput - The input type for the generateSEOKeywords function.
 * - GenerateSEOKeywordsOutput - The return type for the generateSEOKeywords function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateSEOKeywordsInputSchema = z.object({
  jobTitle: z.string().describe('The title of the job.'),
  jobDescription: z.string().describe('The description of the job.'),
  candidateSkills: z.array(z.string()).describe('A list of skills the candidate possesses.'),
  candidateExperience: z.string().describe('A summary of the candidate\'s experience.'),
});
export type GenerateSEOKeywordsInput = z.infer<typeof GenerateSEOKeywordsInputSchema>;

const GenerateSEOKeywordsOutputSchema = z.object({
  keywords: z.array(z.string()).describe('A list of SEO keywords.'),
});
export type GenerateSEOKeywordsOutput = z.infer<typeof GenerateSEOKeywordsOutputSchema>;

export async function generateSEOKeywords(input: GenerateSEOKeywordsInput): Promise<GenerateSEOKeywordsOutput> {
  return generateSEOKeywordsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateSEOKeywordsPrompt',
  input: {schema: GenerateSEOKeywordsInputSchema},
  output: {schema: GenerateSEOKeywordsOutputSchema},
  prompt: `You are an SEO expert. Generate a list of SEO keywords based on the job description and candidate profile.

Job Title: {{{jobTitle}}}
Job Description: {{{jobDescription}}}
Candidate Skills: {{#each candidateSkills}}{{{this}}}, {{/each}}
Candidate Experience: {{{candidateExperience}}}

Keywords:`,
});

const generateSEOKeywordsFlow = ai.defineFlow(
  {
    name: 'generateSEOKeywordsFlow',
    inputSchema: GenerateSEOKeywordsInputSchema,
    outputSchema: GenerateSEOKeywordsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
