/**
 * Tests for enhanced form validation security
 */
import { CandidateProfileSchema, JobDescriptionSchema } from '@/lib/schemas';

describe('Enhanced Form Validation Security', () => {
  describe('CandidateProfileSchema Security', () => {
    it('should sanitize and accept valid candidate data', () => {
      const validData = {
        fullName: 'John Doe',
        skills: 'JavaScript, React, Node.js, TypeScript',
        experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
        locationPreference: 'Remote'
      };

      const result = CandidateProfileSchema.safeParse(validData);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.fullName).toBe('John Doe');
        expect(result.data.skills).toBe('JavaScript, React, Node.js, TypeScript');
      }
    });

    it('should remove HTML tags from input', () => {
      const maliciousData = {
        fullName: 'John <script>alert("xss")</script> Doe',
        skills: 'JavaScript<br>, React<p>test</p>, Node.js',
        experienceSummary: '<div>I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.</div>',
        locationPreference: '<span>Remote</span>'
      };

      const result = CandidateProfileSchema.safeParse(maliciousData);
      if (result.success) {
        expect(result.data.fullName).not.toContain('<script>');
        expect(result.data.fullName).not.toContain('</script>');
        expect(result.data.skills).not.toContain('<br>');
        expect(result.data.skills).not.toContain('<p>');
        expect(result.data.experienceSummary).not.toContain('<div>');
        expect(result.data.locationPreference).not.toContain('<span>');
      }
    });

    it('should reject script tags in input', () => {
      const maliciousData = {
        fullName: 'John Doe',
        skills: 'JavaScript, React, <script>alert("hack")</script>',
        experienceSummary: 'I have experience but <script>document.cookie</script> in development',
        locationPreference: 'Remote'
      };

      const result = CandidateProfileSchema.safeParse(maliciousData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues.some(issue => 
          issue.message.includes('contains invalid content')
        )).toBe(true);
      }
    });

    it('should remove javascript: protocols', () => {
      const maliciousData = {
        fullName: 'John Doe',
        skills: 'javascript:alert(1), React, Node.js, TypeScript',
        experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
        locationPreference: 'Remote'
      };

      const result = CandidateProfileSchema.safeParse(maliciousData);
      if (result.success) {
        expect(result.data.skills).not.toContain('javascript:');
      }
    });

    it('should remove event handlers', () => {
      const maliciousData = {
        fullName: 'John onclick=alert(1) Doe',
        skills: 'JavaScript, React, Node.js, TypeScript',
        experienceSummary: 'I have 5 years onload=alert("xss") of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
        locationPreference: 'Remote'
      };

      const result = CandidateProfileSchema.safeParse(maliciousData);
      if (result.success) {
        expect(result.data.fullName).not.toContain('onclick=');
        expect(result.data.experienceSummary).not.toContain('onload=');
      }
    });

    it('should validate full name format', () => {
      const invalidData = {
        fullName: 'John123 Doe!@#',
        skills: 'JavaScript, React, Node.js, TypeScript',
        experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
        locationPreference: 'Remote'
      };

      const result = CandidateProfileSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues.some(issue => 
          issue.message.includes('can only contain letters')
        )).toBe(true);
      }
    });

    it('should accept valid names with apostrophes and hyphens', () => {
      const validData = {
        fullName: "John O'Connor-Smith",
        skills: 'JavaScript, React, Node.js, TypeScript',
        experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
        locationPreference: 'Remote'
      };

      const result = CandidateProfileSchema.safeParse(validData);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.fullName).toBe("John O'Connor-Smith");
      }
    });
  });

  describe('JobDescriptionSchema Security', () => {
    it('should sanitize and accept valid job data', () => {
      const validData = {
        jobTitle: 'Senior Software Engineer',
        responsibilities: 'Lead development of web applications using React and Node.js. Mentor junior developers and collaborate with cross-functional teams.',
        requiredSkills: 'JavaScript, React, Node.js, TypeScript, MongoDB'
      };

      const result = JobDescriptionSchema.safeParse(validData);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.jobTitle).toBe('Senior Software Engineer');
      }
    });

    it('should remove HTML tags and scripts from job description', () => {
      const maliciousData = {
        jobTitle: 'Senior <script>alert("xss")</script> Engineer',
        responsibilities: '<div>Lead development of web applications using React and Node.js. Mentor junior developers and collaborate with cross-functional teams.</div>',
        requiredSkills: 'JavaScript<br>, React, Node.js'
      };

      const result = JobDescriptionSchema.safeParse(maliciousData);
      if (result.success) {
        expect(result.data.jobTitle).not.toContain('<script>');
        expect(result.data.responsibilities).not.toContain('<div>');
        expect(result.data.requiredSkills).not.toContain('<br>');
      }
    });
  });
});