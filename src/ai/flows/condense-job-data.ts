'use server';

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const JobDataInputSchema = z.object({
  jobDescription: z.string().describe('The full text of the job description to condense.'),
  jobTitle: z.string().describe('The title of the job.'),
  companyName: z.string().describe('The name of the company offering the job.'),
  location: z.string().describe('The location of the job.'),
  responsibilities: z.string().describe('The responsibilities associated with the job.'),
  requiredSkills: z.string().describe('The skills required for the job, as a comma-separated list.'),
});

export type CondenseJobDataInput = z.infer<typeof JobDataInputSchema>;

const CondenseJobDataOutputSchema = z.object({
  condensedDescription: z.string().describe('A condensed version of the job description.'),
});
export type CondenseJobDataOutput = z.infer<typeof CondenseJobDataOutputSchema>;

const prompt = ai.definePrompt({
    name: 'condenseJobDataPrompt',
    input: {schema: JobDataInputSchema},
    output: {schema: CondenseJobDataOutputSchema},
    prompt: `You are an expert in job descriptions. Read the following job data and condense it into an elaborate description that highlights the key aspects of the job. The description should include the job title, company name, location, responsibilities, and required skills.
Job Title: {{{jobTitle}}}
Company Name: {{{companyName}}}
Location: {{{location}}}
Responsibilities: {{{responsibilities}}}
Required Skills: {{{requiredSkills}}}
Job Description:{{{jobDescription}}}

Condensed Description:
`,
});

const condenseJobDataFlow = ai.defineFlow(
  {
    name: 'condenseJobDataFlow',
    inputSchema: JobDataInputSchema,
    outputSchema: CondenseJobDataOutputSchema,
  },
  async (input) => {
    const {output} = await prompt(input);
    return output!;
  }
);

export async function condenseJobData(
  input: CondenseJobDataInput
): Promise<CondenseJobDataOutput> {
  return condenseJobDataFlow(input);
}
// Export the flow for use in other parts of the application