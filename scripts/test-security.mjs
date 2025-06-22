#!/usr/bin/env node

/**
 * Simple validation script to test security improvements without full test environment
 */

import { CandidateProfileSchema, JobDescriptionSchema } from '../lib/schemas.js';

console.log('🔒 Testing security validations...\n');

// Test 1: Basic valid data
console.log('Test 1: Valid data validation');
try {
  const validCandidate = {
    fullName: 'John Doe',
    skills: 'JavaScript, React, Node.js, TypeScript',
    experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
    locationPreference: 'Remote'
  };
  
  const result = CandidateProfileSchema.safeParse(validCandidate);
  if (result.success) {
    console.log('✅ Valid data passed validation');
  } else {
    console.log('❌ Valid data failed validation:', result.error.issues);
  }
} catch (e) {
  console.log('❌ Error testing valid data:', e.message);
}

// Test 2: XSS Prevention
console.log('\nTest 2: XSS Prevention');
try {
  const xssData = {
    fullName: 'John <script>alert("xss")</script> Doe',
    skills: 'JavaScript, React<script>document.cookie</script>, Node.js',
    experienceSummary: 'I have <div onclick="alert()">5 years</div> of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
    locationPreference: 'Remote'
  };
  
  const result = CandidateProfileSchema.safeParse(xssData);
  if (result.success) {
    const hasScript = JSON.stringify(result.data).includes('<script>');
    const hasOnclick = JSON.stringify(result.data).includes('onclick');
    
    if (!hasScript && !hasOnclick) {
      console.log('✅ XSS content successfully sanitized');
      console.log('   Sanitized name:', result.data.fullName);
    } else {
      console.log('❌ XSS content not properly sanitized');
    }
  } else {
    // Check if it failed due to script detection
    const hasScriptError = result.error.issues.some(issue => 
      issue.message.includes('contains invalid content')
    );
    if (hasScriptError) {
      console.log('✅ XSS content properly rejected');
    } else {
      console.log('❌ XSS content failed for wrong reason:', result.error.issues);
    }
  }
} catch (e) {
  console.log('❌ Error testing XSS prevention:', e.message);
}

// Test 3: Name format validation
console.log('\nTest 3: Name format validation');
try {
  const invalidNameData = {
    fullName: 'John123 Doe!@#',
    skills: 'JavaScript, React, Node.js, TypeScript',
    experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
    locationPreference: 'Remote'
  };
  
  const result = CandidateProfileSchema.safeParse(invalidNameData);
  if (!result.success) {
    const hasNameError = result.error.issues.some(issue => 
      issue.message.includes('can only contain letters')
    );
    if (hasNameError) {
      console.log('✅ Invalid name format properly rejected');
    } else {
      console.log('❌ Invalid name failed for wrong reason');
    }
  } else {
    console.log('❌ Invalid name format was accepted');
  }
} catch (e) {
  console.log('❌ Error testing name validation:', e.message);
}

// Test 4: Valid special characters in names
console.log('\nTest 4: Valid special characters in names');
try {
  const validSpecialName = {
    fullName: "Mary O'Connor-Smith Jr.",
    skills: 'JavaScript, React, Node.js, TypeScript',
    experienceSummary: 'I have 5 years of experience in web development using modern technologies. I have worked on various projects including e-commerce platforms and SaaS applications.',
    locationPreference: 'Remote'
  };
  
  const result = CandidateProfileSchema.safeParse(validSpecialName);
  if (result.success) {
    console.log('✅ Valid special characters in name accepted');
    console.log('   Name:', result.data.fullName);
  } else {
    console.log('❌ Valid special characters in name rejected:', result.error.issues);
  }
} catch (e) {
  console.log('❌ Error testing special characters:', e.message);
}

console.log('\n🔒 Security validation tests completed!');