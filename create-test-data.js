// Script to create test data in Firestore for debugging
// This helps us understand the data structure and test the dashboard

const admin = require('firebase-admin');

// Initialize Firebase Admin (you'll need to set up credentials)
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    projectId: process.env.GCP_PROJECT || 'your-project-id'
  });
}

const db = admin.firestore();

async function createTestData() {
  console.log('Creating test data...');

  try {
    // Test resume data
    const testResume = {
      user_id: 'test-user-1',
      session_id: 'test-session-1',
      resume_data: {
        personal_details: {
          full_name: 'John Doe',
          email: 'john.doe@example.com',
          phone_number: '+1-555-0123',
          location: {
            city: 'San Francisco',
            state: 'CA',
            countryCode: 'US'
          },
          links: [
            {
              type: 'LinkedIn',
              url: 'https://linkedin.com/in/johndoe'
            }
          ]
        },
        professional_summary: 'Experienced software engineer with 5+ years in full-stack development.',
        inferred_experience_level: 'Senior',
        total_years_experience: 5.5,
        work_experience: [
          {
            job_title: 'Senior Software Engineer',
            company: 'Tech Corp',
            location: 'San Francisco, CA',
            start_date: '2020-01',
            end_date: null,
            is_current: true,
            responsibilities: [
              'Led development of microservices architecture',
              'Mentored junior developers'
            ]
          }
        ],
        skills: {
          technical: {
            programming_languages: ['JavaScript', 'Python', 'TypeScript'],
            frameworks_libraries: ['React', 'Node.js', 'Express'],
            databases: ['PostgreSQL', 'MongoDB'],
            cloud_platforms: ['AWS', 'GCP'],
            tools_technologies: ['Docker', 'Kubernetes', 'Git']
          },
          soft_skills: ['Leadership', 'Communication', 'Problem Solving']
        }
      },
      session_info: {
        operation_type: 'resume_parsing',
        timestamp: new Date().toISOString(),
        model_used: 'gemini-2.5-flash'
      }
    };

    // Test job posting data
    const testJobPosting = {
      user_id: 'test-company-1',
      session_id: 'test-session-2',
      job_posting_data: {
        job_title: 'Full Stack Developer',
        company: {
          name: 'Startup Inc',
          description: 'Fast-growing tech startup',
          website_url: 'https://startup.com',
          application_email: 'jobs@startup.com'
        },
        location: {
          city: 'San Francisco',
          state: 'CA',
          countryCode: 'US',
          remote: true
        },
        years_of_experience: '3-5 years',
        key_responsibilities: [
          'Develop and maintain web applications',
          'Collaborate with cross-functional teams',
          'Write clean, maintainable code',
          'Participate in code reviews'
        ],
        required_skills: {
          programming_languages: ['JavaScript', 'TypeScript'],
          frameworks_libraries: ['React', 'Node.js'],
          databases: ['PostgreSQL'],
          cloud_platforms: ['AWS'],
          tools_technologies: ['Git', 'Docker']
        },
        industry_type: 'Technology',
        salary_range: '$80,000 - $120,000',
        type_of_employment: 'Full-time'
      },
      session_info: {
        operation_type: 'job_posting_analysis',
        timestamp: new Date().toISOString(),
        model_used: 'gemini-2.5-flash'
      }
    };

    // Test compatibility score data
    const testCompatibilityScore = {
      user_id: 'test-user-1',
      session_id: 'test-session-3',
      compatibility_data: {
        compatibility_score: 85,
        summary: 'Strong match with excellent technical skills alignment. Candidate has relevant experience in required technologies.',
        matching_skills: ['JavaScript', 'React', 'Node.js', 'PostgreSQL', 'Git'],
        missing_skills: ['TypeScript', 'Docker']
      },
      session_info: {
        operation_type: 'compatibility_score',
        timestamp: new Date().toISOString(),
        model_used: 'gemini-2.5-flash'
      }
    };

    // Add documents to Firestore
    const resumeRef = await db.collection('candidates').add(testResume);
    console.log('Created test resume with ID:', resumeRef.id);

    const jobRef = await db.collection('jobPostings').add(testJobPosting);
    console.log('Created test job posting with ID:', jobRef.id);

    const scoreRef = await db.collection('compatibility_scores').add(testCompatibilityScore);
    console.log('Created test compatibility score with ID:', scoreRef.id);

    console.log('Test data created successfully!');

  } catch (error) {
    console.error('Error creating test data:', error);
  }
}

async function checkCollections() {
  console.log('Checking existing collections...');

  try {
    const collections = ['candidates', 'jobPostings', 'compatibility_scores'];
    
    for (const collectionName of collections) {
      const snapshot = await db.collection(collectionName).limit(5).get();
      console.log(`\n${collectionName} collection:`);
      console.log(`- Document count: ${snapshot.size}`);
      
      if (!snapshot.empty) {
        const firstDoc = snapshot.docs[0];
        console.log(`- Sample document ID: ${firstDoc.id}`);
        console.log(`- Sample document keys: ${Object.keys(firstDoc.data()).join(', ')}`);
      }
    }
  } catch (error) {
    console.error('Error checking collections:', error);
  }
}

// Main execution
async function main() {
  const action = process.argv[2];
  
  if (action === 'check') {
    await checkCollections();
  } else if (action === 'create') {
    await createTestData();
  } else {
    console.log('Usage:');
    console.log('  node create-test-data.js check   - Check existing data');
    console.log('  node create-test-data.js create  - Create test data');
  }
  
  process.exit(0);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { createTestData, checkCollections };