import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { adminApp } from '@/lib/firebase-admin';
import { getFirestore } from 'firebase-admin/firestore';

const db = getFirestore(adminApp);

export async function GET(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  request: NextRequest
) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Extract search params for potential future use
    // const { searchParams } = new URL(request.url);
    // const userId = searchParams.get('userId') || session.user.id;
    // const limit = parseInt(searchParams.get('limit') || '10');
    // const offset = parseInt(searchParams.get('offset') || '0');

    // Query candidates collection for resumes - simplified approach
    const collection = db.collection('candidates');
    
    // Get all documents first to see what we have
    const snapshot = await collection.limit(50).get(); // Limit to 50 for now
    
    const resumes = snapshot.docs.map(doc => {
      const data = doc.data();
      console.log('Document structure:', Object.keys(data));
      return {
        id: doc.id,
        ...data,
        created_at: doc.createTime?.toDate().toISOString() || new Date().toISOString(),
        updated_at: doc.updateTime?.toDate().toISOString() || new Date().toISOString()
      };
    });

    console.log(`Found ${resumes.length} resumes in candidates collection`);
    
    // Log first resume structure if available
    if (resumes.length > 0) {
      console.log('First resume structure:', JSON.stringify(resumes[0], null, 2));
    }

    return NextResponse.json({
      resumes,
      total: snapshot.size,
      hasMore: snapshot.size === 50
    });

  } catch (error) {
    console.error('Error fetching resumes:', error);
    return NextResponse.json(
      { error: 'Failed to fetch resumes' },
      { status: 500 }
    );
  }
}