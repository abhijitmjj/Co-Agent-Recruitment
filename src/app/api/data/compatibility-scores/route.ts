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

    // Query compatibility_scores collection - simplified approach
    const collection = db.collection('compatibility_scores');
    
    // Get all documents first to see what we have
    const snapshot = await collection.limit(50).get(); // Limit to 50 for now
    
    const compatibilityScores = snapshot.docs.map(doc => {
      const data = doc.data();
      console.log('Compatibility score document structure:', Object.keys(data));
      return {
        id: doc.id,
        ...data,
        created_at: doc.createTime?.toDate().toISOString() || new Date().toISOString(),
        updated_at: doc.updateTime?.toDate().toISOString() || new Date().toISOString()
      };
    });

    console.log(`Found ${compatibilityScores.length} compatibility scores in compatibility_scores collection`);
    
    // Log first compatibility score structure if available
    if (compatibilityScores.length > 0) {
      console.log('First compatibility score structure:', JSON.stringify(compatibilityScores[0], null, 2));
    }

    return NextResponse.json({
      compatibilityScores,
      total: snapshot.size,
      hasMore: snapshot.size === 50
    });

  } catch (error) {
    console.error('Error fetching compatibility scores:', error);
    return NextResponse.json(
      { error: 'Failed to fetch compatibility scores' },
      { status: 500 }
    );
  }
}