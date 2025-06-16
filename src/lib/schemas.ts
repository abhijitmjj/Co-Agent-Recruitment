import { z } from 'zod';

// Custom validation functions for security
const sanitizeText = (text: string): string => {
  // Remove potential HTML tags and suspicious content
  return text
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .trim();
};

const createSecureStringSchema = (minLength: number, maxLength: number, fieldName: string) => {
  return z.string()
    .min(minLength, { message: `${fieldName} must be at least ${minLength} characters.` })
    .max(maxLength, { message: `${fieldName} must not exceed ${maxLength} characters.` })
    .refine(
      (text) => !text.includes('<script'),
      { message: `${fieldName} contains invalid content.` }
    )
    .refine(
      (text) => !/javascript:/gi.test(text),
      { message: `${fieldName} contains invalid content.` }
    )
    .refine(
      (text) => !/on\w+\s*=/gi.test(text),
      { message: `${fieldName} contains invalid content.` }
    )
    .transform(sanitizeText)
    .refine(
      (text) => text.length >= minLength,
      { message: `${fieldName} must be at least ${minLength} characters after sanitization.` }
    );
};

export const JobDescriptionSchema = z.object({
  jobTitle: createSecureStringSchema(3, 100, "Job title"),
  responsibilities: createSecureStringSchema(50, 5000, "Responsibilities"),
  requiredSkills: createSecureStringSchema(10, 1000, "Required skills")
    .describe("Comma-separated list of skills"),
});
export type JobDescriptionInput = z.infer<typeof JobDescriptionSchema>;

export const CandidateProfileSchema = z.object({
  fullName: createSecureStringSchema(2, 100, "Full name")
    .refine(
      (name) => /^[a-zA-Z\s\-'.]+$/.test(name),
      { message: "Full name can only contain letters, spaces, hyphens, apostrophes, and periods." }
    ),
  skills: createSecureStringSchema(10, 1000, "Skills")
    .describe("Comma-separated list of skills"),
  experienceSummary: createSecureStringSchema(50, 5000, "Experience summary"),
  locationPreference: createSecureStringSchema(2, 100, "Location preference"),
});
export type CandidateProfileInput = z.infer<typeof CandidateProfileSchema>;
