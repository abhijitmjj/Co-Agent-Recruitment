// Simple test script to verify the data endpoints are working
// Run this with: node test-data-endpoints.js

const testEndpoints = async () => {
  const baseUrl = 'http://localhost:3000'; // Adjust if your app runs on a different port
  
  const endpoints = [
    '/api/data/resumes',
    '/api/data/job-postings', 
    '/api/data/compatibility-scores'
  ];

  console.log('Testing data endpoints...\n');

  for (const endpoint of endpoints) {
    try {
      console.log(`Testing ${endpoint}...`);
      const response = await fetch(`${baseUrl}${endpoint}`);
      
      if (response.status === 401) {
        console.log(`✅ ${endpoint} - Authentication required (expected)`);
      } else if (response.ok) {
        const data = await response.json();
        console.log(`✅ ${endpoint} - Success:`, Object.keys(data));
      } else {
        console.log(`❌ ${endpoint} - Error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint} - Network error:`, error.message);
    }
    console.log('');
  }
};

// Only run if this file is executed directly
if (require.main === module) {
  testEndpoints().catch(console.error);
}

module.exports = { testEndpoints };