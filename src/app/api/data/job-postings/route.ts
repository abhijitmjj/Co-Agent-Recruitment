import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { adminApp } from '@/lib/firebase-admin';
import { getFirestore } from 'firebase-admin/firestore';

const db = getFirestore(adminApp);

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId') || session.user.id;
    const limit = parseInt(searchParams.get('limit') || '10');
    const offset = parseInt(searchParams.get('offset') || '0');

    // Query jobPostings collection - simplified approach
    const collection = db.collection('jobPostings');
    
    // Get all documents first to see what we have
    const snapshot = await collection.limit(50).get(); // Limit to 50 for now
    
    const jobPostings = snapshot.docs.map(doc => {
      const data = doc.data();
      console.log('Job posting document structure:', Object.keys(data));
      return {
        id: doc.id,
        ...data,
        created_at: doc.createTime?.toDate().toISOString() || new Date().toISOString(),
        updated_at: doc.updateTime?.toDate().toISOString() || new Date().toISOString()
      };
    });

    console.log(`Found ${jobPostings.length} job postings in jobPostings collection`);
    
    // Log first job posting structure if available
    if (jobPostings.length > 0) {
      console.log('First job posting structure:', JSON.stringify(jobPostings[0], null, 2));
    }

    return NextResponse.json({
      jobPostings,
      total: snapshot.size,
      hasMore: snapshot.size === 50
    });

  } catch (error) {
    console.error('Error fetching job postings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch job postings' },
      { status: 500 }
    );
  }
}