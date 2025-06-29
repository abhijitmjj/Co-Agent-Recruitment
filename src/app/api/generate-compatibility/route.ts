import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { adminApp } from '@/lib/firebase-admin';
import { getFirestore } from 'firebase-admin/firestore';
import { getCloudRunAuthHeaders } from '@/lib/cloud-run-auth';

const db = getFirestore(adminApp);

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { resumeId, jobPostingId } = await request.json();

    if (!resumeId || !jobPostingId) {
      return NextResponse.json({ 
        error: 'Both resumeId and jobPostingId are required' 
      }, { status: 400 });
    }

    // Get the resume and job posting data
    const [resumeDoc, jobPostingDoc] = await Promise.all([
      db.collection('candidates').doc(resumeId).get(),
      db.collection('jobPostings').doc(jobPostingId).get()
    ]);

    if (!resumeDoc.exists || !jobPostingDoc.exists) {
      return NextResponse.json({ 
        error: 'Resume or job posting not found' 
      }, { status: 404 });
    }

    const resumeData = resumeDoc.data();
    const jobPostingData = jobPostingDoc.data();

    // Extract the actual data from the nested structure
    const resume = resumeData?.response || resumeData?.resume_data || resumeData;
    const jobPosting = jobPostingData?.response?.analyze_job_posting_response?.job_posting_data || 
                     jobPostingData?.job_posting_data || 
                     jobPostingData;

    if (!resume || !jobPosting) {
      return NextResponse.json({ 
        error: 'Invalid data structure in resume or job posting' 
      }, { status: 400 });
    }

    // Call the Python backend matcher agent
    try {
      const cloudRunUrl = `${process.env.CLOUD_RUNNER_AGENT_API_URL}/orchestrator`;
      const authHeaders = await getCloudRunAuthHeaders(cloudRunUrl);
      
      const matcherResponse = await fetch(cloudRunUrl, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          query: `Generate compatibility score between this resume and job posting. Resume: ${JSON.stringify(resume)}. Job Posting: ${JSON.stringify(jobPosting)}`,
          user_id: session.user.id,
          session_id: `compatibility_${Date.now()}`,
        }),
      });

      if (!matcherResponse.ok) {
        throw new Error('Failed to get compatibility score from matcher service');
      }

      const matcherResult = await matcherResponse.json();
      
      // The result should be saved to Firestore automatically via Pub/Sub
      // But let's also return it directly to the user
      return NextResponse.json({
        success: true,
        data: matcherResult,
        message: 'Compatibility analysis initiated. Results will be saved to the database.'
      });

    } catch (matcherError) {
      console.error('Matcher service error:', matcherError);
      
      // Fallback: create a mock compatibility score for demonstration
      const mockCompatibilityScore = {
        user_id: session.user.id,
        session_id: `compatibility_${Date.now()}`,
        compatibility_data: {
          compatibility_score: Math.floor(Math.random() * 40) + 60, // 60-100%
          summary: `Analysis of ${resume.personal_details?.full_name || 'candidate'} for ${jobPosting.job_title || 'position'}. Strong technical alignment with some areas for growth.`,
          matching_skills: extractMatchingSkills(resume, jobPosting),
          missing_skills: extractMissingSkills(resume, jobPosting)
        },
        session_info: {
          operation_type: 'compatibility_score',
          timestamp: new Date().toISOString(),
          model_used: 'mock-compatibility-generator'
        }
      };

      // Save the mock score to Firestore
      const docRef = await db.collection('compatibility_scores').add(mockCompatibilityScore);
      
      return NextResponse.json({
        success: true,
        data: { id: docRef.id, ...mockCompatibilityScore },
        message: 'Mock compatibility score generated and saved.'
      });
    }

  } catch (error) {
    console.error('Error generating compatibility score:', error);
    return NextResponse.json(
      { error: 'Failed to generate compatibility score' },
      { status: 500 }
    );
  }
}

function extractMatchingSkills(resume: Record<string, any>, jobPosting: Record<string, any>): string[] {
  const resumeSkills = [
    ...(resume.skills?.technical?.programming_languages || []),
    ...(resume.skills?.technical?.frameworks_libraries || []),
    ...(resume.skills?.technical?.databases || []),
    ...(resume.skills?.technical?.cloud_platforms || []),
    ...(resume.skills?.technical?.tools_technologies || [])
  ].map(skill => skill.toLowerCase());

  const jobSkills = [
    ...(jobPosting.required_skills?.programming_languages || []),
    ...(jobPosting.required_skills?.frameworks_libraries || []),
    ...(jobPosting.required_skills?.databases || []),
    ...(jobPosting.required_skills?.cloud_platforms || []),
    ...(jobPosting.required_skills?.tools_technologies || [])
  ].map(skill => skill.toLowerCase());

  return resumeSkills.filter(skill => 
    jobSkills.some(jobSkill => 
      jobSkill.includes(skill) || skill.includes(jobSkill)
    )
  ).slice(0, 8);
}

function extractMissingSkills(resume: Record<string, any>, jobPosting: Record<string, any>): string[] {
  const resumeSkills = [
    ...(resume.skills?.technical?.programming_languages || []),
    ...(resume.skills?.technical?.frameworks_libraries || []),
    ...(resume.skills?.technical?.databases || []),
    ...(resume.skills?.technical?.cloud_platforms || []),
    ...(resume.skills?.technical?.tools_technologies || [])
  ].map(skill => skill.toLowerCase());

  const jobSkills = [
    ...(jobPosting.required_skills?.programming_languages || []),
    ...(jobPosting.required_skills?.frameworks_libraries || []),
    ...(jobPosting.required_skills?.databases || []),
    ...(jobPosting.required_skills?.cloud_platforms || []),
    ...(jobPosting.required_skills?.tools_technologies || [])
  ].map(skill => skill.toLowerCase());

  return jobSkills.filter(skill => 
    !resumeSkills.some(resumeSkill => 
      resumeSkill.includes(skill) || skill.includes(resumeSkill)
    )
  ).slice(0, 6);
}