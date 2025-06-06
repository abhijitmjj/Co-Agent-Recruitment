import { z } from 'zod';

export const JobDescriptionSchema = z.object({
  jobTitle: z.string().min(3, { message: "Job title must be at least 3 characters." }).max(100),
  responsibilities: z.string().min(50, { message: "Responsibilities must be at least 50 characters." }).max(5000),
  requiredSkills: z.string().min(10, { message: "Required skills must be at least 10 characters." }).max(1000)
    .describe("Comma-separated list of skills"),
});
export type JobDescriptionInput = z.infer<typeof JobDescriptionSchema>;


export const CandidateProfileSchema = z.object({
  fullName: z.string().min(2, { message: "Full name must be at least 2 characters." }).max(100),
  skills: z.string().min(10, { message: "Skills must be at least 10 characters." }).max(1000)
    .describe("Comma-separated list of skills"),
  experienceSummary: z.string().min(50, { message: "Experience summary must be at least 50 characters." }).max(5000),
  locationPreference: z.string().min(2, { message: "Location preference must be at least 2 characters." }).max(100),
});
export type CandidateProfileInput = z.infer<typeof CandidateProfileSchema>;
